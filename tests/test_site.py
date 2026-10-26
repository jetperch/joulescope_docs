# SPDX-FileCopyrightText: Copyright 2026 Jetperch LLC
# SPDX-License-Identifier: Apache-2.0

"""Checks on the built site.  Run "python -m joulescope_docs html" first."""

import json

import pytest

from joulescope_docs import (ANCHORS, EXTERNAL, SITE, SITE_LANGUAGE, SOURCE, load_projects,
                             load_urls, mounted, published_urls)

EN = SITE_LANGUAGE

_needs_site = pytest.mark.skipif(not (EN / 'index.html').exists(), reason='site not built')


def _searchindex():
    text = (EN / 'searchindex.js').read_text()
    return json.loads(text[text.index('(') + 1:text.rindex(')')])


@_needs_site
@pytest.mark.parametrize('name', list(mounted(load_projects())))
def test_project_pages_keep_their_paths(name):
    """Every upstream page is at /en/software/<name>/<same path>.html, so old
    Read the Docs URLs map to new ones by prefix only."""
    doc_dir = EXTERNAL / name / mounted(load_projects())[name]['doc_dir']
    docs = [p.relative_to(doc_dir).with_suffix('') for p in doc_dir.rglob('*')
            if p.suffix in ('.rst', '.md') and '_build' not in p.parts]
    assert docs
    missing = [str(d) for d in docs if not (EN / 'software' / name / f'{d}.html').exists()]
    assert not missing


@_needs_site
def test_search_index_covers_everything():
    index = _searchindex()
    prefixes = {'/'.join(d.split('/')[:2]) for d in index['docnames']}
    expected = ({f'software/{n}' for n in mounted(load_projects())} | {'software/joulescope_ui'} |
                {f'products/{n}' for n in ['js110', 'js220', 'js220plus', 'js320']} |
                {'introduction', 'getting_started/unboxing'})
    assert expected <= prefixes
    for term in ['jsdrv_open', 'jls_rd_open', 'scan']:
        assert any(term in o for objs in index['objects'].values() for o in objs) \
            or term in index['terms'], term


@_needs_site
@pytest.mark.parametrize('name', list(mounted(load_projects())))
def test_version_switcher(name):
    entries = json.loads((EN / 'archive' / name / 'versions.json').read_text())
    assert entries[0] == {'name': 'latest', 'version': 'latest',
                          'url': f'/en/software/{name}/', 'preferred': True}


@_needs_site
def test_datasheets_published_unchanged():
    yamls = sorted((SOURCE / 'products').glob('*/*_datasheet.yaml'))
    assert len(yamls) == 4
    for path in yamls:
        published = EN / path.relative_to(SOURCE)
        assert published.read_bytes() == path.read_bytes()


def test_image_names_are_unique():
    """Sphinx copies every image to one _images/ directory and renames
    clashes in build order, so a page move could give a cached URL a
    different picture.  Unique names keep image URLs stable."""
    mount_dirs = [SOURCE / 'software' / name for name in mounted(load_projects())]
    names = {}
    for path in SOURCE.rglob('*'):
        if path.suffix.lower() in ('.png', '.jpg', '.jpeg', '.svg', '.gif') and \
                not any(path.is_relative_to(m) for m in mount_dirs) and \
                '_static' not in path.parts and '_include' not in path.parts:
            names.setdefault(path.name, []).append(str(path.relative_to(SOURCE)))
    assert not {k: v for k, v in names.items() if len(v) > 1}


@_needs_site
def test_404_page_uses_absolute_links():
    """CloudFront serves 404.html at any depth, so relative links would break."""
    html = (SITE / '404.html').read_text()
    assert 'href="/en/_static/' in html
    assert 'href="/en/"' in html
    assert 'href="_static/' not in html and 'src="_static/' not in html


@_needs_site
def test_agent_indexes():
    """Every page has a Markdown copy, and llms.txt and the sitemap list them."""
    pages = sorted(p.relative_to(EN).with_suffix('').as_posix() for p in EN.rglob('*.md'))
    assert 'products/js320/guide/fuse' in pages
    assert not [p for p in pages if not (EN / f'{p}.html').exists()]
    llms = (SITE / 'llms.txt').read_text()
    sitemap = (SITE / 'sitemap.xml').read_text()
    for page in pages:
        assert f'/en/{page}.md)' in llms, page
        assert f'/en/{page}.html</loc>' in sitemap, page
    assert 'Sitemap: https://docs.joulescope.com/sitemap.xml' in (SITE / 'robots.txt').read_text()
    assert (SITE / 'llms-full.txt').stat().st_size > 100_000
    assert not [p for p in (EN / '_sources').rglob('*') if p.is_file()]  # raw MyST


@_needs_site
def test_urls_unchanged():
    """URLs are permanent: see CLAUDE.md.  CI builds the PDFs in another job,
    so they are compared only when built; test_cli checks their names."""
    expected = load_urls()
    actual = published_urls(SITE)
    if not any(SITE.rglob('*.pdf')):
        expected = [u for u in expected if not u.endswith('.pdf')]
    removed = sorted(set(expected) - set(actual))
    added = sorted(set(actual) - set(expected))
    assert not removed and not added, (
        f'URLs changed.  Removed {len(removed)}: {removed[:10]}  '
        f'Added {len(added)}: {added[:10]}.  Removing or renaming a '
        f'URL needs approval and a redirect (CLAUDE.md).  Then run '
        f'"python -m joulescope_docs urls" and commit urls.txt.')


@_needs_site
def test_root_redirects_to_language():
    html = (SITE / 'index.html').read_text()
    assert 'url=en/' in html and 'href="en/"' in html
    assert sorted(p.name for p in SITE.iterdir() if p.is_file()) == [
        '404.html', 'index.html', 'llms-full.txt', 'llms.txt', 'robots.txt', 'sitemap.xml']


@_needs_site
def test_product_layout():
    """Everything about a product is under /en/products/<model>/."""
    for model in ['js110', 'js220', 'js220plus', 'js320']:
        d = EN / 'products' / model
        for name in ['index.html', 'datasheet.html', f'{model}_datasheet.yaml',
                     'guide/index.html']:
            assert (d / name).exists(), (model, name)


@_needs_site
def test_cited_anchors_exist():
    """Other sites link to these sections (anchors.txt, CLAUDE.md)."""
    missing = []
    for url in load_urls(ANCHORS):
        path, _, fragment = url.partition('#')
        page = SITE / path
        if not page.exists() or f'id="{fragment}"' not in page.read_text(encoding='utf-8'):
            missing.append(url)
    assert not missing, f'Cited anchors missing: {missing}'
