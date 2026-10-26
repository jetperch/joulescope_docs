# SPDX-FileCopyrightText: Copyright 2026 Jetperch LLC
# SPDX-License-Identifier: Apache-2.0

"""Indexes for search engines and LLM agents: sitemap.xml, robots.txt,
llms.txt, a Markdown copy of every page, and llms-full.txt.

The HTML build writes the indexes, which "python -m joulescope_docs html"
moves to the site root.  The "markdown" builder
(sphinx-markdown-builder) writes <page>.md, which this extension rewrites
to absolute links; "python -m joulescope_docs html" copies them next to the
HTML pages.  See doc/architecture.md, "Indexes for agents".
"""

import posixpath
import re
from xml.sax.saxutils import escape

from sphinx_markdown_builder.translator import MarkdownTranslator

# Generated pages that are not content.
SKIP = {'404', 'genindex', 'search', 'py-modindex'}
_LINK = re.compile(r'(!?)\[([^\]]*)\]\(([^)\s\[\]]+)\)')


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


def _title(env, doc):
    return env.titles[doc].astext() if doc in env.titles else doc


def _llms_txt(app, pages):
    base = app.config.site_index_base_url
    root = app.config.site_index_root_url
    env = app.env
    lines = [
        f'# {app.config.project}', '',
        '> User\'s guides, datasheets and software documentation for Joulescope',
        '> precision DC energy analyzers.', '',
        '## How to read this site', '',
        '- Every page is HTML and Markdown at the same path: replace ".html" with',
        f'  ".md", for example {base}products/js320/guide/fuse.md.',
        '  The Markdown uses absolute links.',
        '- Contents, below, lists every page in reading order.',
        f'- {root}llms-full.txt is every page in one file, in the same order.',
        f'- {root}sitemap.xml lists the HTML pages.',
        '- Each product has its guide, datasheet, PDFs and datasheet YAML under',
        f'  {base}products/<model>/.  The YAML format is described at',
        f'  {base}products/datasheet_format.html.',
        '- Release archives of the software documentation are under',
        f'  {base}archive/<project>/<tag>/, listed in',
        f'  {base}archive/<project>/versions.json.', '',
    ]
    yamls = [(doc, f'{doc.rsplit("/", 2)[-2]}_datasheet.yaml') for _, doc in pages
             if doc.startswith('products/') and doc.endswith('/datasheet')]
    yamls = [(doc, f'{posixpath.dirname(doc)}/{name}') for doc, name in yamls
             if (app.srcdir / posixpath.dirname(doc) / name).exists()]
    if yamls:
        lines += ['## Datasheets (YAML)', '']
        lines += [f'- [{_title(env, doc)}]({base}{y})' for doc, y in yamls]
        lines.append('')
    pdf_paths = app.config.site_index_pdf_paths
    pdfs = [(pdf_paths[tex], title) for _, tex, title, *_ in app.config.latex_documents
            if tex in pdf_paths]
    if pdfs:
        lines += ['## PDFs', '']
        lines += [f'- [{title}]({base}{path})' for path, title in pdfs]
        lines.append('')
    lines += ['## Contents', '']
    lines += [f'{"  " * depth}- [{_title(env, doc)}]({base}{doc}.md)' for depth, doc in pages]
    return '\n'.join(lines) + '\n'


def _sitemap(base, pages):
    urls = ''.join(f'  <url><loc>{escape(base + doc)}.html</loc></url>\n' for _, doc in pages)
    return ('<?xml version="1.0" encoding="UTF-8"?>\n'
            '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
            f'{urls}</urlset>\n')


def _build_finished(app, exception):
    if exception:
        return
    pages = toc(app.env, app.config.root_doc)
    out = app.outdir
    base = app.config.site_index_base_url
    if app.builder.format == 'html':
        (out / 'llms.txt').write_text(_llms_txt(app, pages), encoding='utf-8')
        (out / 'sitemap.xml').write_text(_sitemap(base, pages), encoding='utf-8')
        (out / 'robots.txt').write_text(
            f'User-agent: *\nAllow: /\n\nSitemap: {app.config.site_index_root_url}sitemap.xml\n',
            encoding='utf-8')
    elif app.builder.name == 'markdown':
        for doc in SKIP:
            (out / f'{doc}.md').unlink(missing_ok=True)
        full = []
        for _, doc in pages:
            path = out / f'{doc}.md'
            text = absolute_links(path.read_text(encoding='utf-8'), doc, base,
                                  app.config.site_index_root_url)
            path.write_text(text, encoding='utf-8')
            full.append(f'<!-- {base}{doc}.html -->\n\n{text.strip()}\n')
        (out / 'llms-full.txt').write_text('\n\n'.join(full), encoding='utf-8')


def _page_context(app, pagename, templatename, context, doctree):
    if doctree is not None and pagename not in SKIP:
        md = posixpath.basename(pagename) + '.md'
        context['metatags'] = context.get('metatags', '') + (
            f'\n<link rel="alternate" type="text/markdown" href="{md}">')


class _MarkdownTranslator(MarkdownTranslator):
    # sphinx-markdown-builder 0.6 does not render figure captions.
    visit_caption = MarkdownTranslator.visit_paragraph


def setup(app):
    app.add_config_value('site_index_base_url', '', 'html')  # pages, such as .../en/
    app.add_config_value('site_index_root_url', '', 'html')  # llms.txt, sitemap.xml
    app.add_config_value('site_index_pdf_paths', {}, 'html')  # {tex name: path}
    app.set_translator('markdown', _MarkdownTranslator)
    app.connect('html-page-context', _page_context)
    app.connect('build-finished', _build_finished)
    return {'parallel_read_safe': True, 'parallel_write_safe': True}
