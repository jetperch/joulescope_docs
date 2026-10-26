# SPDX-FileCopyrightText: Copyright 2026 Jetperch LLC
# SPDX-License-Identifier: Apache-2.0

import argparse
import importlib.util
import pathlib

import pytest

from joulescope_docs import (EXTERNAL, ROOT, SOURCE, load_archives, load_projects, load_urls,
                             mounted, published_urls)
from joulescope_docs import __main__ as cli


def _args(*sources):
    return argparse.Namespace(source=list(sources))


def test_projects_toml():
    projects = load_projects()
    assert list(projects) == ['joulescope_driver', 'pyjoulescope', 'jls', 'pyjoulescope_ui']
    assert list(mounted(projects)) == ['joulescope_driver', 'pyjoulescope', 'jls']
    for name, p in projects.items():
        assert {'title', 'repo'} <= set(p), name
        assert ('doc_dir' in p) != ('include_dir' in p), name
    for name, p in mounted(projects).items():
        assert 'package' in p, name


def test_checkouts_default_and_override(tmp_path):
    projects = load_projects()
    assert cli._checkouts(_args(), projects)['jls'] == EXTERNAL / 'jls'
    result = cli._checkouts(_args(f'jls={tmp_path}'), projects)
    assert result['jls'] == tmp_path.resolve()
    assert result['pyjoulescope'] == EXTERNAL / 'pyjoulescope'


@pytest.mark.parametrize('bad', ['nope=/tmp', 'jls', 'jls='])
def test_checkouts_invalid(bad):
    with pytest.raises(SystemExit):
        cli._checkouts(_args(bad), load_projects())


def test_env_drops_pythonpath(monkeypatch):
    monkeypatch.setenv('PYTHONPATH', '/somewhere/else')
    env = cli._env(EXTRA='1')
    assert 'PYTHONPATH' not in env
    assert env['EXTRA'] == '1'


def test_load_archives(tmp_path):
    assert load_archives(tmp_path / 'missing.toml') == {}
    path = tmp_path / 'archives.toml'
    path.write_text('[jls]\nversions = ["v0.20.0", "v0.19.1"]\n')
    assert load_archives(path) == {'jls': ['v0.20.0', 'v0.19.1']}


def test_archives_toml_names_known_projects():
    assert set(load_archives()) <= set(mounted(load_projects()))


def _conf():
    spec = importlib.util.spec_from_file_location('conf', SOURCE / 'conf.py')
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_conf_versions():
    conf = _conf()
    project = {'rtd': 'https://jls.readthedocs.io/'}
    entries = conf.versions('jls', project, {'jls': ['v0.20.0']})
    assert [e['version'] for e in entries] == ['latest', 'v0.20.0', 'rtd']
    assert entries[0] == {'name': 'latest', 'version': 'latest', 'url': '/en/software/jls/',
                          'preferred': True}
    assert entries[1]['url'] == '/en/archive/jls/v0.20.0/'
    assert conf.versions('x', {}, {})[-1]['version'] == 'latest'


def test_parser_commands():
    p = cli.parser()
    for cmd in ['deps', 'doxygen-install', 'html', 'pdf', 'linkcheck', 'serve', 'urls']:
        assert p.parse_args([cmd]).command == cmd
    args = p.parse_args(['archive', 'jls', 'v0.19.1'])
    assert (args.project, args.tag, args.install) == ('jls', 'v0.19.1', False)
    assert p.parse_args(['archive', 'jls', 'v0.19.1', '--install']).install
    assert p.parse_args(['archive-list']).command == 'archive-list'
    assert pathlib.Path(ROOT, 'projects.toml').is_file()


def test_pdf_env_respects_source_date_epoch(monkeypatch):
    monkeypatch.setenv('SOURCE_DATE_EPOCH', '123')
    env = cli._pdf_env()
    assert env['SOURCE_DATE_EPOCH'] == '123'
    assert env['FORCE_SOURCE_DATE'] == '1'


def test_clean_site_then_merge_pdfs(tmp_path, monkeypatch):
    site, pdf_site = tmp_path / 'site', tmp_path / 'pdf'
    (site / 'en' / 'old').mkdir(parents=True)
    (site / 'en' / 'old' / 'page.html').write_text('')
    (pdf_site / 'en' / 'products' / 'js320').mkdir(parents=True)
    (pdf_site / 'en' / 'products' / 'js320' / 'js320_datasheet.pdf').write_text('')
    monkeypatch.setattr(cli, 'SITE', site)
    monkeypatch.setattr(cli, 'PDF_SITE', pdf_site)
    cli._clean_site()
    assert not site.exists()
    site.mkdir()
    cli._merge_pdfs()
    assert (site / 'en' / 'products' / 'js320' / 'js320_datasheet.pdf').exists()


def test_serve_host():
    p = cli.parser()
    assert p.parse_args(['serve']).host == 'localhost'
    args = p.parse_args(['serve', '--host', '0.0.0.0', '--port', '8001'])
    assert (args.host, args.port) == ('0.0.0.0', 8001)



def test_archive_list(monkeypatch, capsys):
    monkeypatch.setattr(cli, 'load_archives', lambda: {'jls': ['v0.20.0', 'v0.19.1']})
    cli.cmd_archive_list(None)
    assert capsys.readouterr().out == 'jls v0.20.0\njls v0.19.1\n'


def test_urls_list_pdfs():
    """The PDF names in urls.txt match conf.py, without building them."""
    conf = _conf()
    assert sorted(conf.PDF_PATHS) == sorted(doc[1] for doc in conf.latex_documents)
    pdfs = sorted(f'en/{path}' for path in conf.PDF_PATHS.values())
    assert pdfs == [u for u in load_urls() if u.endswith('.pdf')]


def test_published_urls(tmp_path):
    for name in ['index.html', 'a/b.html', 'a/b.md', 'pdf/x.pdf', '_static/s.css',
                 '_images/i.html', 'archive/p/versions.json', 'searchindex.js', 'llms.txt']:
        (tmp_path / name).parent.mkdir(parents=True, exist_ok=True)
        (tmp_path / name).write_text('')
    assert published_urls(tmp_path) == ['a/b.html', 'archive/p/versions.json', 'index.html',
                                        'llms.txt', 'pdf/x.pdf']
    path = tmp_path / 'urls.txt'
    path.write_text('# comment\n\nb.html\na.html\n')
    assert load_urls(path) == ['a.html', 'b.html']
