# SPDX-FileCopyrightText: Copyright 2026 Jetperch LLC
# SPDX-License-Identifier: Apache-2.0

import types

import pytest
from docutils import nodes
from sphinx import addnodes

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


def test_parents():
    env = types.SimpleNamespace(
        toctree_includes={'index': ['a', 'b'], 'a': ['a/x'], 'b': ['a']},
        found_docs={'index', 'a', 'a/x', 'b'})
    assert site_index.parents(env, 'index') == {'a': 'index', 'b': 'index', 'a/x': 'a'}


def test_clean_removes_comments_and_badges_outside_code():
    text = ('<!-- SPDX-License-Identifier: Apache-2.0 -->\n\n# Title\n\n'
            '[![b](https://img.shields.io/x.svg)](https://pypi.org/x)\n\n\n\nText.\n\n'
            '```html\n<!-- kept -->\n```\n')
    assert site_index.clean(text) == '# Title\n\nText.\n\n```html\n<!-- kept -->\n```\n'


def test_clean_multiline_comment():
    assert site_index.clean('a\n<!--\nnote\n-->\nb\n') == 'a\nb\n'


@pytest.mark.parametrize('text, limit, expected', [
    ('One.  Two.', 240, 'One. Two.'),
    ('First sentence here.  Second sentence.', 25, 'First sentence here.'),
    ('word ' * 100, 30, 'word word word word word word…'),
])
def test_summarize(text, limit, expected):
    assert site_index.summarize(text, limit) == expected


def _doc(*children):
    doc = nodes.document(None, None)
    section = nodes.section()
    section += nodes.title(text='Title')
    for c in children:
        section += c
    doc += section
    return doc


def test_describe_skips_short_and_lead_in_paragraphs():
    doc = _doc(nodes.paragraph(text='Short.'),
               nodes.paragraph(text='Applications include a long list of things:'),
               nodes.paragraph(text='The instrument measures current and voltage precisely.'))
    assert site_index.describe(doc) == 'The instrument measures current and voltage precisely.'


def test_describe_api_names():
    sigs = []
    for name in ['a', 'b', 'c', 'd', 'e']:
        desc = addnodes.desc()
        sig = addnodes.desc_signature()
        sig += addnodes.desc_name(text=name)
        desc += sig
        sigs.append(desc)
    assert site_index.describe(_doc(*sigs)) == 'API reference: a, b, c, d and 1 more.'


def test_yaml_quotes_any_text():
    assert site_index._yaml({'title': 'A: "b"', 'n': 1}) == '---\ntitle: "A: \\"b\\""\nn: "1"\n---\n'


def test_tokens():
    assert site_index._tokens('x' * 400) == '100'
    assert site_index._tokens('x' * 120_000) == '30k'
