# SPDX-FileCopyrightText: Copyright 2026 Jetperch LLC
# SPDX-License-Identifier: Apache-2.0

"""Build tooling for the unified Joulescope documentation.

See doc/build.md for usage and doc/architecture.md for the design.
"""

import pathlib
import tomllib

ROOT = pathlib.Path(__file__).resolve().parent.parent
SOURCE = ROOT / 'source'
MOUNT = SOURCE / 'software'  # project docs are mounted at software/<name>
INCLUDE = SOURCE / '_include'  # include-only project files, not built
BUILD = ROOT / 'build'
EXTERNAL = ROOT / 'external'
SITE = BUILD / 'site'
DOXYGEN_XML = BUILD / 'doxygen'


def load_projects(path=None):
    """Load projects.toml as {name: dict}, in file order."""
    path = ROOT / 'projects.toml' if path is None else pathlib.Path(path)
    with open(path, 'rb') as f:
        return tomllib.load(f)


def mounted(projects):
    """The projects whose Sphinx docs are part of the site (they have doc_dir)."""
    return {name: p for name, p in projects.items() if 'doc_dir' in p}


def load_archives(path=None):
    """Load archives.toml as {project: [version, ...]}, newest first."""
    path = ROOT / 'archives.toml' if path is None else pathlib.Path(path)
    if not path.exists():
        return {}
    with open(path, 'rb') as f:
        return {k: list(v.get('versions', [])) for k, v in tomllib.load(f).items()}
