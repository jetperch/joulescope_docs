# SPDX-FileCopyrightText: Copyright 2026 Jetperch LLC
# SPDX-License-Identifier: Apache-2.0

import os
import pathlib
import subprocess
import sys
import textwrap

import pytest

from joulescope_docs import mount

PROJECTS = {'proj': {'doc_dir': 'doc/sphinx'}}


@pytest.fixture
def checkout(tmp_path):
    root = tmp_path / 'checkout'
    (root / 'doc' / 'sphinx').mkdir(parents=True)
    return root


def test_mount_creates_relative_link(tmp_path, checkout):
    src = tmp_path / 'source'
    src.mkdir()
    result = mount.mount(src, PROJECTS, {'proj': checkout})
    link = src / 'proj'
    assert link.is_symlink()
    assert not os.path.isabs(os.readlink(link))
    assert result == {'proj': (checkout / 'doc' / 'sphinx').resolve()}


def test_mount_is_idempotent_and_retargets(tmp_path, checkout):
    src = tmp_path / 'source'
    src.mkdir()
    mount.mount(src, PROJECTS, {'proj': checkout})
    mount.mount(src, PROJECTS, {'proj': checkout})
    other = tmp_path / 'other'
    (other / 'doc' / 'sphinx').mkdir(parents=True)
    mount.mount(src, PROJECTS, {'proj': other})
    assert (src / 'proj').resolve() == (other / 'doc' / 'sphinx').resolve()


def test_mount_missing_doc_dir(tmp_path):
    with pytest.raises(FileNotFoundError):
        mount.mount(tmp_path, PROJECTS, {'proj': tmp_path / 'missing'})


def test_mount_refuses_to_replace_real_directory(tmp_path, checkout):
    (tmp_path / 'proj').mkdir()
    with pytest.raises(FileExistsError):
        mount.mount(tmp_path, PROJECTS, {'proj': checkout})


@pytest.mark.parametrize('patch', [True, False])
def test_sphinx_build_through_mount(tmp_path, checkout, patch):
    """The include and link patterns the upstream projects use.

    Without the patch, the page-to-page links fail.  If that ever stops being
    true, Sphinx no longer resolves symlinks and the patch can go.
    """
    (checkout / 'README.md').write_text('# Readme\n\nSee [the guide](doc/guide.md).\n')
    (checkout / 'doc' / 'topics.json').write_text('{"a": 1}\n')
    sphinx_dir = checkout / 'doc' / 'sphinx'
    (sphinx_dir / 'index.md').write_text(textwrap.dedent('''\
        # Project

        Next: [page two](two.md).

        ```{toctree}
        readme
        two
        ```
        '''))
    (sphinx_dir / 'readme.md').write_text('```{include} ../../README.md\n```\n')
    (sphinx_dir / 'two.md').write_text(textwrap.dedent('''\
        # Two

        Back to [the index](index.md).

        ```{literalinclude} ../topics.json
        ```
        '''))
    src = tmp_path / 'source'
    src.mkdir()
    (src / 'index.md').write_text('# Root\n\n```{toctree}\nproj/index\n```\n')
    (src / 'conf.py').write_text(textwrap.dedent(f'''\
        import sys
        sys.path.insert(0, {str(pathlib.Path(mount.__file__).parents[1])!r})
        from joulescope_docs import mount
        extensions = ['myst_parser']
        def setup(app):
            if {patch!r}:
                mount.patch_relfn2path({str(src)!r}, ['proj'])
        '''))
    mount.mount(src, PROJECTS, {'proj': checkout})
    out = tmp_path / 'html'
    env = {k: v for k, v in os.environ.items() if k != 'PYTHONPATH'}
    r = subprocess.run([sys.executable, '-m', 'sphinx', '-E', '-q', '-b', 'html',
                        str(src), str(out)], capture_output=True, text=True, env=env)
    # README links to a non-document path, which is reported; nothing else is.
    warnings = [w for w in r.stderr.splitlines() if 'WARNING' in w]
    if not patch:
        assert sum('Unknown source document' in w for w in warnings) == 2, r.stderr
        return
    assert len(warnings) == 1 and 'doc/guide.md' in warnings[0], r.stderr
    two = (out / 'proj' / 'two.html').read_text()
    assert 'href="index.html"' in two
    assert '&quot;a&quot;' in two or '"a"' in two
    assert 'href="two.html"' in (out / 'proj' / 'index.html').read_text()


def test_mount_by_key_skips_other_projects(tmp_path, checkout):
    (checkout / 'docs').mkdir()
    projects = {'proj': {'doc_dir': 'doc/sphinx'}, 'other': {'include_dir': 'docs'}}
    checkouts = {'proj': checkout, 'other': checkout}
    assert list(mount.mount(tmp_path / 'software', projects, checkouts)) == ['proj']
    result = mount.mount(tmp_path / '_include', projects, checkouts, key='include_dir')
    assert result == {'other': (checkout / 'docs').resolve()}
    assert (tmp_path / '_include' / 'other').is_symlink()
