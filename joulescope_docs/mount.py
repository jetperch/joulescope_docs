# SPDX-FileCopyrightText: Copyright 2026 Jetperch LLC
# SPDX-License-Identifier: Apache-2.0

"""Mount project directories into the unified source tree.

Each project's Sphinx directory (doc_dir) is symlinked to
source/software/<name>.  A project's include_dir is symlinked to
source/_include/<name>, which is not built, so owned pages can {include}
files that stay in that project.  The upstream
{include} and literalinclude paths that leave the Sphinx directory (README,
CHANGELOG, topic JSON) keep working because the OS resolves ".." against
the real location.  See doc/architecture.md.
"""

import os
import pathlib
import sys


def _is_link(path):
    return path.is_symlink() or (sys.platform == 'win32' and path.is_junction())


def _link(target, link):
    if sys.platform == 'win32':
        try:
            os.symlink(target, link, target_is_directory=True)
        except OSError:  # symlinks need Developer Mode; junctions do not
            import _winapi
            _winapi.CreateJunction(str(target), str(link))
    else:
        os.symlink(os.path.relpath(target, link.parent), link, target_is_directory=True)


def mount(source_dir, projects, checkouts, key='doc_dir'):
    """Create or update source_dir/<name> links.

    :param source_dir: The directory that holds the links.
    :param projects: {name: project} from projects.toml.  Only projects
        with the key are linked.
    :param checkouts: {name: checkout path}.
    :param key: The project field naming the directory to link.
    :return: {name: resolved directory}.
    :raise FileNotFoundError: A project directory does not exist.
    :raise FileExistsError: A non-link file blocks a mount point.
    """
    source_dir = pathlib.Path(source_dir)
    source_dir.mkdir(parents=True, exist_ok=True)
    result = {}
    for name, project in projects.items():
        if key not in project:
            continue
        target = (pathlib.Path(checkouts[name]) / project[key]).resolve()
        if not target.is_dir():
            raise FileNotFoundError(f'{name}: {key} not found: {target}')
        link = source_dir / name
        if _is_link(link):
            if link.resolve() == target:
                result[name] = target
                continue
            link.unlink()
        elif link.exists():
            raise FileExistsError(f'{name}: {link} exists and is not a link')
        _link(target, link)
        result[name] = target
    return result


def patch_relfn2path(source_dir, names):
    """Keep paths inside mounted projects relative to the source tree.

    Sphinx resolves symlinks in BuildEnvironment.relfn2path, so a relative
    Markdown link between two pages of a mounted project resolves outside
    the source directory and fails with "Unknown source document".  Map the
    resolved path back through its mount.  Paths that leave the mounted
    directory, such as README and CHANGELOG includes, are unchanged.
    """
    from sphinx.environment import BuildEnvironment
    source_dir = pathlib.Path(source_dir).absolute()
    mounts = {n: (source_dir / n).resolve() for n in names if _is_link(source_dir / n)}
    original = getattr(BuildEnvironment.relfn2path, '_original', BuildEnvironment.relfn2path)

    def relfn2path(self, filename, docname=None):
        rel_fn, abs_fn = original(self, filename, docname)
        path = pathlib.Path(abs_fn)
        for name, target in mounts.items():
            if path.is_relative_to(target):
                link = (source_dir / name).relative_to(pathlib.Path(self.srcdir))
                rel = pathlib.PurePosixPath(*link.parts, *path.relative_to(target).parts)
                return str(rel), os.fspath(pathlib.Path(self.srcdir, rel))
        return rel_fn, abs_fn

    relfn2path._original = original
    BuildEnvironment.relfn2path = relfn2path
