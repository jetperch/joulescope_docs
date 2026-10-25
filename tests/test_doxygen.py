# SPDX-FileCopyrightText: Copyright 2026 Jetperch LLC
# SPDX-License-Identifier: Apache-2.0

import hashlib
import io
import pathlib
import re
import tarfile

import pytest

from joulescope_docs import EXTERNAL, doxygen

TEMPLATE = '''\
PROJECT_NUMBER = @VERSION@
OUTPUT_DIRECTORY = @CMAKE_CURRENT_BINARY_DIR@/doxygen
INPUT = @CMAKE_CURRENT_SOURCE_DIR@/../include
DOT_PATH = @DOXYGEN_DOT_PATH@
GENERATE_HTML = YES
'''


def test_render_substitutes_all_variables():
    text = doxygen.render(TEMPLATE, pathlib.Path('/src/doc'), pathlib.Path('/out'), '1.2.3')
    assert '@' not in text
    assert 'PROJECT_NUMBER = 1.2.3' in text
    assert 'OUTPUT_DIRECTORY = /out/doxygen' in text
    assert 'INPUT = /src/doc/../include' in text
    # Overrides come last, so they win over the template.
    assert text.rindex('GENERATE_HTML = NO') > text.index('GENERATE_HTML = YES')
    assert 'GENERATE_XML = YES' in text


@pytest.mark.parametrize('project', ['joulescope_driver', 'jls'])
def test_render_project_templates(project):
    """The real templates use no variables beyond the four we substitute."""
    path = EXTERNAL / project / 'doc' / 'doxygen' / 'Doxyfile.in'
    if not path.exists():
        pytest.skip(f'{project} checkout not present')
    text = doxygen.render(path.read_text(), path.parent.parent, pathlib.Path('/out'), '0')
    assert not re.findall(r'@[A-Z_]+@', text)


def test_find_prefers_environment(tmp_path, monkeypatch):
    exe = tmp_path / 'my_doxygen'
    exe.write_text('')
    monkeypatch.setenv('DOXYGEN', str(exe))
    assert doxygen.find(tmp_path) == exe


def test_find_installed(tmp_path, monkeypatch):
    monkeypatch.delenv('DOXYGEN', raising=False)
    exe = tmp_path / f'doxygen-{doxygen.DOXYGEN_VERSION}' / 'bin' / 'doxygen'
    exe.parent.mkdir(parents=True)
    exe.write_text('')
    assert doxygen.find(tmp_path) == exe


def _tarball(path):
    data = b'#!/bin/sh\n'
    with tarfile.open(path, 'w:gz') as t:
        info = tarfile.TarInfo(f'doxygen-{doxygen.DOXYGEN_VERSION}/bin/doxygen')
        info.size = len(data)
        t.addfile(info, io.BytesIO(data))
    return hashlib.sha256(path.read_bytes()).hexdigest()


def test_install_verifies_checksum(tmp_path, monkeypatch):
    monkeypatch.delenv('DOXYGEN', raising=False)
    src = tmp_path / 'doxygen.tar.gz'
    digest = _tarball(src)
    tools = tmp_path / 'tools'
    exe = doxygen.install(tools, url=src.as_uri(), sha256=digest)
    assert exe == tools / f'doxygen-{doxygen.DOXYGEN_VERSION}' / 'bin' / 'doxygen'


def test_install_rejects_bad_checksum(tmp_path):
    src = tmp_path / 'doxygen.tar.gz'
    _tarball(src)
    tools = tmp_path / 'tools'
    with pytest.raises(ValueError, match='checksum'):
        doxygen.install(tools, url=src.as_uri(), sha256='0' * 64)
    assert not list(tools.glob('*.tar.gz'))  # the bad download is removed
