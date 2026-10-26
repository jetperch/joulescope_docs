# SPDX-FileCopyrightText: Copyright 2026 Jetperch LLC
# SPDX-License-Identifier: Apache-2.0

import types

import pytest

import site_index

ROOT = 'https://docs.example.com/'
BASE = ROOT + 'en/'


@pytest.mark.parametrize('text, expected', [
    ('[Fuse](fuse.md)', f'[Fuse]({BASE}products/js320/fuse.md)'),
    ('[Guide](../js220/index.md#top)', f'[Guide]({BASE}products/js220/index.md#top)'),
    ('![x](products/js320/media/a.svg)', f'![x]({BASE}_images/a.svg)'),
    ('[y](../../_downloads/abc/js320.yaml)', f'[y]({BASE}_downloads/abc/js320.yaml)'),
    ('[i](../../genindex.md)', f'[i]({BASE}genindex.html)'),
    ('[e](https://example.com/a)', '[e](https://example.com/a)'),
    ('[m](mailto:a@b.c)', '[m](mailto:a@b.c)'),
    ('[a](#anchor)', '[a](#anchor)'),
    ('[p](/en/products/js320/js320_datasheet.pdf)',
     f'[p]({ROOT}en/products/js320/js320_datasheet.pdf)'),
    ('[v]([https://a.b/](https://a.b))', '[v]([https://a.b/](https://a.b))'),
])
def test_absolute_links(text, expected):
    assert site_index.absolute_links(text, 'products/js320/fuse', BASE, ROOT) == expected


def test_toc_order_depth_and_orphans():
    env = types.SimpleNamespace(
        toctree_includes={'index': ['a', 'b'], 'a': ['a/x'], 'b': ['a']},
        found_docs={'index', 'a', 'a/x', 'b', 'orphan', '404', 'search'})
    assert site_index.toc(env, 'index') == [
        (0, 'index'), (1, 'a'), (2, 'a/x'), (1, 'b'), (0, 'orphan')]


def test_sitemap():
    xml = site_index._sitemap(BASE, [(0, 'index'), (1, 'a&b')])
    assert f'<loc>{BASE}index.html</loc>' in xml
    assert f'<loc>{BASE}a&amp;b.html</loc>' in xml
