# SPDX-FileCopyrightText: Copyright 2026 Jetperch LLC
# SPDX-License-Identifier: Apache-2.0

import argparse
import importlib.util
import pathlib

import pytest

from joulescope_docs import EXTERNAL, ROOT, SOURCE, load_archives, load_projects, mounted
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
    assert entries[0] == {'name': 'latest', 'version': 'latest', 'url': '/software/jls/',
                          'preferred': True}
    assert entries[1]['url'] == '/archive/jls/v0.20.0/'
    assert conf.versions('x', {}, {})[-1]['version'] == 'latest'


def test_parser_commands():
    p = cli.parser()
    for cmd in ['deps', 'doxygen-install', 'html', 'pdf', 'linkcheck', 'serve']:
        assert p.parse_args([cmd]).command == cmd
    args = p.parse_args(['archive', 'jls', 'v0.19.1'])
    assert (args.project, args.tag, args.all) == ('jls', 'v0.19.1', False)
    args = p.parse_args(['archive', '--all'])
    assert (args.project, args.all) == (None, True)
    assert pathlib.Path(ROOT, 'projects.toml').is_file()


def test_pdf_env_respects_source_date_epoch(monkeypatch):
    monkeypatch.setenv('SOURCE_DATE_EPOCH', '123')
    env = cli._pdf_env()
    assert env['SOURCE_DATE_EPOCH'] == '123'
    assert env['FORCE_SOURCE_DATE'] == '1'


def test_clean_site_keeps_pdfs(tmp_path, monkeypatch):
    site = tmp_path / 'site'
    (site / 'pdf').mkdir(parents=True)
    (site / 'pdf' / 'guide.pdf').write_text('')
    (site / 'old').mkdir()
    (site / 'old' / 'page.html').write_text('')
    (site / 'index.html').write_text('')
    monkeypatch.setattr(cli, 'SITE', site)
    cli._clean_site()
    assert [p.name for p in site.iterdir()] == ['pdf']
    assert (site / 'pdf' / 'guide.pdf').exists()


def test_serve_host():
    p = cli.parser()
    assert p.parse_args(['serve']).host == 'localhost'
    args = p.parse_args(['serve', '--host', '0.0.0.0', '--port', '8001'])
    assert (args.host, args.port) == ('0.0.0.0', 8001)


@pytest.mark.parametrize('argv', [['archive'], ['archive', 'jls'], ['archive', '--all', 'jls']])
def test_archive_invalid_args(argv):
    with pytest.raises(SystemExit):
        cli.cmd_archive(cli.parser().parse_args(argv))


def test_archive_all_skips_built_and_copies(tmp_path, monkeypatch):
    archive, site = tmp_path / 'archive', tmp_path / 'site'
    (archive / 'jls' / 'v0.19.1').mkdir(parents=True)
    (archive / 'jls' / 'v0.19.1' / 'index.html').write_text('')
    (site / 'archive' / 'jls').mkdir(parents=True)
    (site / 'archive' / 'jls' / 'versions.json').write_text('[]')
    monkeypatch.setattr(cli, 'ARCHIVE', archive)
    monkeypatch.setattr(cli, 'SITE', site)
    monkeypatch.setattr(cli, 'load_archives', lambda: {'jls': ['v0.19.1']})
    monkeypatch.setattr(cli, '_run', lambda *a, **k: pytest.fail('nothing to build'))
    cli.cmd_archive(cli.parser().parse_args(['archive', '--all']))
    assert (site / 'archive' / 'jls' / 'v0.19.1' / 'index.html').exists()
    assert (site / 'archive' / 'jls' / 'versions.json').exists()
