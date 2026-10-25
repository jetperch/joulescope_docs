# SPDX-FileCopyrightText: Copyright 2026 Jetperch LLC
# SPDX-License-Identifier: Apache-2.0

"""Checks on the built site.  Run "python -m joulescope_docs html" first."""

import json

import pytest

from joulescope_docs import EXTERNAL, SITE, SOURCE, load_projects, mounted

_needs_site = pytest.mark.skipif(not (SITE / 'index.html').exists(), reason='site not built')


def _searchindex():
    text = (SITE / 'searchindex.js').read_text()
    return json.loads(text[text.index('(') + 1:text.rindex(')')])


@_needs_site
@pytest.mark.parametrize('name', list(mounted(load_projects())))
def test_project_pages_keep_their_paths(name):
    """Every upstream page is at /software/<name>/<same path>.html, so old
    Read the Docs URLs map to new ones by prefix only."""
    doc_dir = EXTERNAL / name / mounted(load_projects())[name]['doc_dir']
    docs = [p.relative_to(doc_dir).with_suffix('') for p in doc_dir.rglob('*')
            if p.suffix in ('.rst', '.md') and '_build' not in p.parts]
    assert docs
    missing = [str(d) for d in docs if not (SITE / 'software' / name / f'{d}.html').exists()]
    assert not missing


@_needs_site
def test_search_index_covers_everything():
    index = _searchindex()
    prefixes = {'/'.join(d.split('/')[:2]) for d in index['docnames']}
    expected = ({f'software/{n}' for n in mounted(load_projects())} | {'software/joulescope_ui'} |
                {f'products/{n}' for n in ['js110', 'js220', 'js220plus', 'js320',
                                           'datasheets']} |
                {'introduction', 'getting_started/unboxing'})
    assert expected <= prefixes
    for term in ['jsdrv_open', 'jls_rd_open', 'scan']:
        assert any(term in o for objs in index['objects'].values() for o in objs) \
            or term in index['terms'], term


@_needs_site
@pytest.mark.parametrize('name', list(mounted(load_projects())))
def test_version_switcher(name):
    entries = json.loads((SITE / 'archive' / name / 'versions.json').read_text())
    assert entries[0] == {'name': 'latest', 'version': 'latest',
                          'url': f'/software/{name}/', 'preferred': True}


@_needs_site
def test_datasheets_published_unchanged():
    yamls = sorted((SOURCE / 'products' / 'datasheets').glob('*.yaml'))
    assert yamls
    for path in yamls:
        published = SITE / 'products' / 'datasheets' / path.name
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
