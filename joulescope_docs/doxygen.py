# SPDX-FileCopyrightText: Copyright 2026 Jetperch LLC
# SPDX-License-Identifier: Apache-2.0

"""Generate Doxygen XML for Breathe from each project's own Doxyfile.in.

The projects configure doc/doxygen/Doxyfile.in with CMake configure_file.
Substituting its four @VARIABLE@ values here avoids both duplicating the
Doxygen configuration and building the C library first.
"""

import hashlib
import os
import pathlib
import shutil
import subprocess
import tarfile
import urllib.request

# Pinned Doxygen release for Linux x86_64, used by CI.  Update together.
DOXYGEN_VERSION = '1.14.0'
DOXYGEN_URL = ('https://github.com/doxygen/doxygen/releases/download/'
               f'Release_{DOXYGEN_VERSION.replace(".", "_")}/'
               f'doxygen-{DOXYGEN_VERSION}.linux.bin.tar.gz')
DOXYGEN_SHA256 = 'e5d6ae24d0bf3f0cdc4d8f146726b89ca323922f19441af99b1872d503665ad6'

# Appended overrides: XML only, quiet.  Later Doxyfile assignments win.
_OVERRIDES = """
GENERATE_HTML = NO
GENERATE_LATEX = NO
GENERATE_XML = YES
QUIET = YES
WARNINGS = NO
"""


def render(template, doc_dir, out_dir, version):
    """Render a CMake Doxyfile.in template.

    :param template: The Doxyfile.in text.
    :param doc_dir: The project doc/ directory (CMAKE_CURRENT_SOURCE_DIR).
    :param out_dir: The output directory (CMAKE_CURRENT_BINARY_DIR).
        XML is written to out_dir/doxygen/xml.
    :param version: The project version string.
    :return: The Doxyfile text.
    """
    values = {
        'CMAKE_CURRENT_SOURCE_DIR': pathlib.Path(doc_dir).as_posix(),
        'CMAKE_CURRENT_BINARY_DIR': pathlib.Path(out_dir).as_posix(),
        'DOXYGEN_DOT_PATH': '',
        'VERSION': version,
    }
    for key, value in values.items():
        template = template.replace(f'@{key}@', value)
    return template + _OVERRIDES


def xml_dir(out_dir):
    return pathlib.Path(out_dir) / 'doxygen' / 'xml'


def generate(doxygen, checkout, out_dir, version):
    """Run Doxygen for one project.

    :return: The XML directory.
    """
    doc_dir = pathlib.Path(checkout).resolve() / 'doc'
    out_dir = pathlib.Path(out_dir).resolve()
    text = render((doc_dir / 'doxygen' / 'Doxyfile.in').read_text(), doc_dir, out_dir, version)
    if out_dir.exists():
        shutil.rmtree(out_dir)  # stale XML from removed headers would linger
    out_dir.mkdir(parents=True)
    print(f'+ {doxygen} - < {doc_dir / "doxygen" / "Doxyfile.in"} (rendered)', flush=True)
    subprocess.run([str(doxygen), '-'], input=text.encode('utf-8'), cwd=doc_dir, check=True)
    return xml_dir(out_dir)


def find(tools_dir):
    """Find Doxygen: $DOXYGEN, then the installed pinned copy, then PATH."""
    candidates = [os.environ.get('DOXYGEN'),
                  pathlib.Path(tools_dir) / f'doxygen-{DOXYGEN_VERSION}' / 'bin' / 'doxygen',
                  shutil.which('doxygen')]
    for c in candidates:
        if c and pathlib.Path(c).is_file():
            return pathlib.Path(c)
    raise FileNotFoundError('doxygen not found: set DOXYGEN, install it, or run '
                            '"python -m joulescope_docs doxygen-install" (Linux x86_64)')


def install(tools_dir, url=DOXYGEN_URL, sha256=DOXYGEN_SHA256):
    """Download and unpack the pinned Doxygen release into tools_dir."""
    tools_dir = pathlib.Path(tools_dir)
    tools_dir.mkdir(parents=True, exist_ok=True)
    archive = tools_dir / url.rsplit('/', 1)[-1]
    if not archive.exists():
        with urllib.request.urlopen(url) as r, open(archive.with_suffix('.part'), 'wb') as f:
            shutil.copyfileobj(r, f)
        archive.with_suffix('.part').rename(archive)
    digest = hashlib.sha256(archive.read_bytes()).hexdigest()
    if digest != sha256:
        archive.unlink()
        raise ValueError(f'doxygen checksum mismatch: {digest}')
    with tarfile.open(archive) as t:
        t.extractall(tools_dir, filter='data')
    return find(tools_dir)
