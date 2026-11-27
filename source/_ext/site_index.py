# SPDX-FileCopyrightText: Copyright 2026 Jetperch LLC
# SPDX-License-Identifier: Apache-2.0

"""Indexes for search engines and LLM agents: sitemap.xml, robots.txt,
llms.txt, a Markdown copy of every page, llms-full.txt and one llms-full.txt
per product and software project.

The HTML build writes sitemap.xml, robots.txt and each page's meta
description.  The "markdown" builder (sphinx-markdown-builder) writes
<page>.md, which this extension cleans, gives YAML front matter and
absolute links, and then writes llms.txt and the llms-full.txt bundles.
"python -m joulescope_docs html" copies them next to the HTML pages.  See
doc/architecture.md, "Indexes for agents".
"""

import json
import posixpath
import re
import subprocess
from pathlib import Path
from xml.sax.saxutils import escape, quoteattr

from docutils import nodes
from sphinx import addnodes
from sphinx_markdown_builder.translator import MarkdownTranslator

# Generated pages that are not content.
SKIP = {'404', 'genindex', 'search', 'py-modindex'}
# Sections that get their own llms-full.txt: products/<model>, software/<project>.
BUNDLE_PARENTS = ('products', 'software')
DESCRIPTION_MAX = 240  # characters
_LINK = re.compile(r'(!?)\[([^\]]*)\]\(([^)\s\[\]]+)\)')
_COMMENT = re.compile(r'<!--.*?-->\n?', re.S)
_FENCE = re.compile(r'^\s*(```|~~~)')
# Download and license badges, which say nothing about the content.
_BADGE = re.compile(r'\[!\[[^\]]*\]\([^)]*(?:shields\.io|pepy\.tech|badge)[^)]*\)\]\([^)]*\)')


def toc(env, root):
    """[(depth, docname)] in table-of-contents order, then any orphans."""
    result, seen = [], set()

    def walk(doc, depth):
        if doc in seen:
            return
        seen.add(doc)
        result.append((depth, doc))
        for child in env.toctree_includes.get(doc, []):
            walk(child, depth + 1)

    walk(root, 0)
    result += [(0, d) for d in sorted(env.found_docs - seen - SKIP)]
    return result


def parents(env, root):
    """{docname: parent docname}, from the first toctree that includes it."""
    result = {}
    for _, doc in toc(env, root):
        for child in env.toctree_includes.get(doc, []):
            result.setdefault(child, doc)
    return result


def absolute_links(text, docname, base_url, root_url):
    """Rewrite the relative links of a Markdown page to absolute URLs.

    Images resolve to the HTML build's flat _images/ (names are unique, see
    tests/test_site.py) and downloads to its _downloads/.
    """
    def repl(m):
        bang, label, target = m.groups()
        if target.startswith('/') and not target.startswith('//'):  # site: links
            return f'{bang}[{label}]({root_url}{target[1:]})'
        if re.match(r'[a-z][a-z0-9+.-]*:|#|/', target):
            return m.group(0)
        if bang:
            url = f'{base_url}_images/{posixpath.basename(target)}'
        elif '_downloads/' in target:
            url = base_url + target[target.index('_downloads/'):]
        else:
            url = posixpath.normpath(posixpath.join(posixpath.dirname(docname), target))
            if url.removesuffix('.md') in SKIP:  # generated pages have no Markdown
                url = url.removesuffix('.md') + '.html'
            url = base_url + url
        return f'{bang}[{label}]({url})'
    return _LINK.sub(repl, text)


def clean(text):
    """Remove what only helps authors: HTML comments (SPDX headers,
    include-fragment notes) and badges.  Code blocks are kept as they are."""
    out, prose = [], []

    def flush():
        if prose:
            s = _BADGE.sub('', _COMMENT.sub('', ''.join(prose)))
            out.append(re.sub(r'\n{3,}', '\n\n', s))
            prose.clear()

    fence = None
    for line in text.splitlines(keepends=True):
        m = _FENCE.match(line)
        if fence is None and m:
            flush()
            fence = m.group(1)
            out.append(line)
        elif fence is not None:
            out.append(line)
            if m and m.group(1) == fence and not line.strip()[3:].strip():
                fence = None
        else:
            prose.append(line)
    flush()
    return re.sub(r'\n{3,}', '\n\n', ''.join(out)).strip() + '\n'


def summarize(text, limit=DESCRIPTION_MAX):
    """Whole sentences of text, up to limit characters."""
    text = ' '.join(text.split())
    result = ''
    for sentence in re.split(r'(?<=[.!?])\s+(?=[A-Z(])', text):
        if result and len(result) + len(sentence) + 1 > limit:
            break
        result = f'{result} {sentence}'.strip()
    if len(result) > limit:
        result = result[:limit].rsplit(' ', 1)[0].rstrip(',;:') + '…'
    return result


def describe(doctree):
    """A description from the page: its first paragraph of prose, or the
    names of the API objects it documents."""
    def prose(p):
        text = ' '.join(p.astext().split())
        return len(text) >= 40 and not text.endswith(':') and '<br' not in text

    candidates = [p for p in doctree.findall(nodes.paragraph)
                  if isinstance(p.parent, (nodes.section, nodes.document)) and prose(p)]
    # Prefer the introduction, before the first subsection.
    first = [p for p in candidates if p.parent.parent is doctree or p.parent is doctree]
    for p in first + candidates:
        return summarize(p.astext())
    names = []
    for desc in doctree.findall(addnodes.desc):
        if isinstance(desc.parent, addnodes.desc_content):
            continue  # a member of a documented class
        for sig in desc.findall(addnodes.desc_signature):
            name = next(iter(sig.findall(addnodes.desc_name)), None)
            name = name.astext().strip() if name is not None else ''
            if name and name not in names:
                names.append(name)
            break
    if names:
        more = f' and {len(names) - 4} more' if len(names) > 4 else ''
        return f'API reference: {", ".join(names[:4])}{more}.'
    return ''


def _doctree_read(app, doctree):
    docname = app.env.docname
    meta = app.env.metadata[docname]
    text = meta.get('description') or app.config.site_index_descriptions.get(docname)
    meta['description'] = ' '.join(str(text).split()) if text else describe(doctree)


class _GitDates:
    """The last commit date of files, one "git log" per repository."""

    def __init__(self):
        self._repos = {}  # repository root: {path: date}

    def _repo(self, path):
        for d in path.parents:
            if (d / '.git').exists():
                return d
        return None

    def date(self, path):
        path = Path(path).resolve()
        repo = self._repo(path)
        if repo is None:
            return None
        if repo not in self._repos:
            dates = {}
            try:
                log = subprocess.run(
                    ['git', '-C', str(repo), 'log', '--format=@%cs', '--name-only'],
                    capture_output=True, text=True, check=True).stdout
            except (OSError, subprocess.CalledProcessError):
                log = ''
            date = None
            for line in log.splitlines():
                if line.startswith('@'):
                    date = line[1:]
                elif line:
                    dates.setdefault(str((repo / line).resolve()), date)
            self._repos[repo] = dates
        return self._repos[repo].get(str(path))


def _title(env, doc):
    return env.titles[doc].astext() if doc in env.titles else doc


def _section(doc):
    """'products/js320' for a page in a product or project section, else None."""
    parts = doc.split('/')
    if len(parts) >= 3 and parts[0] in BUNDLE_PARENTS:
        return '/'.join(parts[:2])
    return None


def front_matter(app, doc, parent_of, git):
    """The page facts an agent needs when it reads one page alone."""
    env, config = app.env, app.config
    meta = env.metadata.get(doc, {})
    result = {'title': _title(env, doc)}
    if meta.get('description'):
        result['description'] = meta['description']
    ancestors, d = [], parent_of.get(doc)
    while d is not None and d != config.root_doc:
        ancestors.insert(0, d)
        d = parent_of.get(d)
    if ancestors:
        result['breadcrumb'] = ' > '.join(_title(env, a) for a in ancestors)
    for a in reversed(ancestors + [doc]):
        rev = env.metadata.get(a, {})
        if 'revision' in rev:
            result['document'] = (f'{_title(env, a)}, revision {rev["revision"]} '
                                  f'({rev["date"]})')
            break
    section = _section(doc)
    if section and section.startswith('products/'):
        index = f'{section}/index'
        result['product'] = _title(env, index)
        status = env.metadata.get(index, {}).get('status')
        if status:
            result['product_status'] = status
    elif section:
        software = config.site_index_software.get(section.split('/')[1])
        if software:
            result['software'] = software
    result['url'] = f'{config.site_index_base_url}{doc}.html'
    files = [env.doc2path(doc)] + sorted(env.dependencies.get(doc, ()))
    dates = [x for x in (git.date(f) for f in files) if x]
    if dates:
        result['last_updated'] = max(dates)
    return result


def _yaml(fields):
    # JSON strings are valid YAML scalars, so any text is quoted safely.
    lines = [f'{k}: {json.dumps(str(v), ensure_ascii=False)}' for k, v in fields.items()]
    return '---\n' + '\n'.join(lines) + '\n---\n'


def _tokens(text):
    """A rough token count for an agent's context budget."""
    n = len(text) / 4
    return f'{round(n / 1000)}k' if n >= 1000 else f'{round(n, -2):.0f}'


def _entry(env, base, doc, depth=0, title=None, anchor=''):
    desc = env.metadata.get(doc, {}).get('description', '')
    line = f'{"  " * depth}- [{title or _title(env, doc)}]({base}{doc}.md{anchor})'
    return f'{line}: {desc}' if desc else line


def _llms_txt(app, pages, bundles):
    config, env = app.config, app.env
    base, root = config.site_index_base_url, config.site_index_root_url
    lines = [
        f'# {config.project}', '',
        '> User\'s guides, datasheets and software documentation for the Joulescope',
        '> precision DC energy analyzers made by Jetperch LLC.  The JS320 is the',
        '> current instrument.  The JS220, JS220+ and JS110 are obsolete and',
        '> still documented.', '',
        '- To write code that controls a Joulescope, use the pyjoulescope_driver',
        '  Python package, not the original joulescope package, and start from',
        f'  the pyjoulescope_driver examples: {base}software/pyjoulescope_examples/index.md.',
        '- For specification values, read the datasheet YAML, listed below.',
        '- Every page is HTML and Markdown at the same path: replace ".html" with',
        f'  ".md", for example {base}products/js320/guide/fuse.md.  The',
        '  Markdown uses absolute links and starts with YAML front matter: the',
        '  title, description, breadcrumb, document revision, product and its',
        '  status, documented software version, URL and last update.',
        '- Each product and software project has an llms-full.txt with all its',
        f'  pages, listed under Bundles.  {root}llms-full.txt has every page.',
        '', '## Start here', '',
    ]
    for item in config.site_index_start:
        doc, _, anchor = item[0].partition('#')
        title = item[1] if len(item) > 1 else None
        line = _entry(env, base, doc, title=title, anchor=f'#{anchor}' if anchor else '')
        if len(item) > 2:
            line = line.split(': ', 1)[0] + f': {item[2]}'
        lines.append(line)
    lines += ['', '## Bundles', '',
              'Each file holds every page of one section in reading order, each',
              'page with its front matter.  Sizes are approximate.', '']
    for section, size in bundles:
        name = _title(env, f'{section}/index') if section else 'Every page'
        path = f'{base}{section}/llms-full.txt' if section else f'{root}llms-full.txt'
        lines.append(f'- [{name}]({path}): about {size} tokens.')
    yamls = [f'products/{model}' for model in (d.split('/')[1] for _, d in pages
             if d.startswith('products/') and d.endswith('/datasheet'))]
    yamls = [s for s in yamls if (app.srcdir / s / f'{s.split("/")[1]}_datasheet.yaml').exists()]
    if yamls:
        lines += ['', '## Datasheets (YAML)', '',
                  f'Format: {base}products/datasheet_format.md.', '']
        lines += [f'- [{_title(env, s + "/datasheet")}]({base}{s}/{s.split("/")[1]}'
                  f'_datasheet.yaml): specification values.' for s in yamls]

    # Contents: the pages without children first, then one heading per section.
    top = [(depth, doc) for depth, doc in pages if depth <= 1]
    leaves = [doc for depth, doc in top if not env.toctree_includes.get(doc) or depth == 0]
    lines += ['', '## General', '']
    lines += [_entry(env, base, doc) for doc in leaves]
    for _, doc in top:
        if doc in leaves:
            continue
        lines += ['', f'## {_title(env, doc)}', '', _entry(env, base, doc)]
        i = pages.index((1, doc)) + 1
        while i < len(pages) and pages[i][0] > 1:
            lines.append(_entry(env, base, pages[i][1], pages[i][0] - 1))
            i += 1

    lines += ['', '## Where to buy', '',
              '- [Joulescope Store](https://www.joulescope.com): sells the instruments and',
              '  accessories.  Agent instructions: https://www.joulescope.com/agents.md.',
              '- [Distributors](https://www.joulescope.com/pages/distributors)', '']
    lines += ['## Optional', '']
    pdf_paths = config.site_index_pdf_paths
    for _, tex, title, *_ in config.latex_documents:
        if tex in pdf_paths:
            lines.append(f'- [{title} (PDF)]({base}{pdf_paths[tex]}): the print edition of '
                         'Markdown pages listed above.')
    lines.append(f'- Release archives of the software documentation: '
                 f'{base}archive/<project>/<tag>/, listed in '
                 f'{base}archive/<project>/versions.json.')
    return '\n'.join(lines) + '\n'


def _sitemap(base, pages):
    urls = ''.join(f'  <url><loc>{escape(base + doc)}.html</loc></url>\n' for _, doc in pages)
    return ('<?xml version="1.0" encoding="UTF-8"?>\n'
            '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
            f'{urls}</urlset>\n')


def _markdown_finished(app, pages):
    out = app.outdir
    base, root = app.config.site_index_base_url, app.config.site_index_root_url
    for doc in SKIP:
        (out / f'{doc}.md').unlink(missing_ok=True)
    parent_of, git = parents(app.env, app.config.root_doc), _GitDates()
    texts = {}
    for _, doc in pages:
        path = out / f'{doc}.md'
        text = clean(absolute_links(path.read_text(encoding='utf-8'), doc, base, root))
        text = _yaml(front_matter(app, doc, parent_of, git)) + '\n' + text
        path.write_text(text, encoding='utf-8')
        texts[doc] = text
    full = '\n'.join(texts[doc] for _, doc in pages)
    (out / 'llms-full.txt').write_text(full, encoding='utf-8')
    bundles = []
    for _, doc in pages:
        parts = doc.split('/')
        if len(parts) == 3 and parts[0] in BUNDLE_PARENTS and parts[2] == 'index':
            section = '/'.join(parts[:2])
            text = '\n'.join(texts[d] for _, d in pages if d.startswith(section + '/'))
            (out / section / 'llms-full.txt').write_text(text, encoding='utf-8')
            bundles.append((section, _tokens(text)))
    bundles.append(('', _tokens(full)))
    (out / 'llms.txt').write_text(_llms_txt(app, pages, bundles), encoding='utf-8')


def _build_finished(app, exception):
    if exception:
        return
    pages = toc(app.env, app.config.root_doc)
    out = app.outdir
    if app.builder.format == 'html':
        (out / 'sitemap.xml').write_text(
            _sitemap(app.config.site_index_base_url, pages), encoding='utf-8')
        (out / 'robots.txt').write_text(
            f'User-agent: *\nAllow: /\n\nSitemap: {app.config.site_index_root_url}sitemap.xml\n',
            encoding='utf-8')
    elif app.builder.name == 'markdown':
        _markdown_finished(app, pages)


def _page_context(app, pagename, templatename, context, doctree):
    if doctree is not None and pagename not in SKIP:
        md = posixpath.basename(pagename) + '.md'
        tags = f'\n<link rel="alternate" type="text/markdown" href="{md}">'
        desc = app.env.metadata.get(pagename, {}).get('description')
        if desc:
            tags += f'\n<meta name="description" content={quoteattr(desc)}>'
        context['metatags'] = context.get('metatags', '') + tags


class _MarkdownTranslator(MarkdownTranslator):
    # sphinx-markdown-builder 0.6 does not render figure captions.
    visit_caption = MarkdownTranslator.visit_paragraph


def setup(app):
    app.add_config_value('site_index_base_url', '', 'html')  # pages, such as .../en/
    app.add_config_value('site_index_root_url', '', 'html')  # llms.txt, sitemap.xml
    app.add_config_value('site_index_pdf_paths', {}, 'html')  # {tex name: path}
    app.add_config_value('site_index_software', {}, 'html')  # {project: "package version"}
    # llms.txt "Start here": (docname[#anchor], [title, [note]]).
    app.add_config_value('site_index_start', [], 'html')
    # {docname: description} for pages without front matter: mounted projects.
    app.add_config_value('site_index_descriptions', {}, 'html')
    app.set_translator('markdown', _MarkdownTranslator)
    app.connect('doctree-read', _doctree_read)
    app.connect('html-page-context', _page_context)
    app.connect('build-finished', _build_finished)
    return {'parallel_read_safe': True, 'parallel_write_safe': True}
