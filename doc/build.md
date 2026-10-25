# Building the documentation

All commands run from the repository root and need no AWS credentials.
Linux is the supported build platform; macOS should work.  Windows needs
Developer Mode for symlinks, or the build falls back to directory junctions.


## One-time setup

System packages (Ubuntu):

```bash
sudo apt install libusb-1.0-0-dev libudev-dev doxygen \
    texlive-xetex texlive-latex-recommended texlive-latex-extra \
    texlive-fonts-recommended tex-gyre fonts-freefont-otf fonts-dejavu \
    fonts-noto-cjk latexmk librsvg2-bin poppler-utils
```

The TeX packages, fonts and `librsvg2-bin` are only needed for PDFs.  CI uses
a pinned Doxygen release instead of the apt package: on Linux x86_64, run
`python -m joulescope_docs doxygen-install`.  Set `DOXYGEN` to use another
binary.

Python 3.13 or newer:

```bash
git clone --recurse-submodules <joulescope_docs repository>
cd joulescope_docs
python3 -m venv .venv
. .venv/bin/activate
pip install -r requirements.txt
python -m joulescope_docs deps          # build the documented packages for autodoc
```

`deps --pypi` installs the released packages instead of building them, which
is faster but may not match unreleased sources.


## Build

| Command | Result |
|---|---|
| `python -m joulescope_docs html` | `build/site/`; warnings are errors |
| `python -m joulescope_docs pdf` | `build/site/pdf/*.pdf` |
| `python -m joulescope_docs serve` | http://localhost:8000/ serving `build/site/`; add `--host 0.0.0.0` to serve to the LAN |
| `python -m joulescope_docs linkcheck` | `build/linkcheck/output.txt` (external links, not in CI) |
| `python -m pytest` | Tooling tests, plus site checks when `build/site/` exists |

To preview changes to a project's documentation, mount another checkout:

```bash
python -m joulescope_docs html --source joulescope_driver=../joulescope_driver
```

Each command prints the commands it runs.  `html` and `pdf` always rebuild
from scratch (`sphinx-build -E`), so warnings in unchanged files are never
hidden.


## Updating dependencies

Python packages: edit `requirements.in` (the exact pins are the Sphinx
toolchain), then re-lock.  `--upgrade` also moves every unpinned package to
its newest compatible release:

```bash
pip install uv
uv pip compile --universal --python-version 3.13 --upgrade \
    requirements.in -o requirements.txt
```

Check the diff: the Windows-only `colorama` entry and `setuptools` must stay.
Dependabot does not update this file, because its pip-compile re-lock drops
those entries; see `.github/dependabot.yml`.

GitHub Actions use major version tags (`actions/checkout@v7`), so they pick
up fixes within a major version.  Dependabot proposes new major versions and
submodule updates; each runs the full CI.

Doxygen for CI is pinned in `joulescope_docs/doxygen.py` (version and
SHA-256).  Doxygen 1.18.0 breaks Breathe 5.1.0, so it stays at 1.17.0 until a
Breathe release fixes that.


## Release archives

To keep the documentation of a project release online, add its tag to
`archives.toml` (newest first).  CI builds every listed archive into
`/archive/<project>/<tag>/`, and the version switcher lists it.  Removing a
tag removes the archive at the next deploy.

To preview one locally:

```bash
pip install pyjls==0.19.1          # autodoc must import the released package
python -m joulescope_docs archive jls v0.19.1
```

The archive is written to `build/archive/<project>/<tag>/`.  `archive --all`
builds every `archives.toml` entry the way CI does: it installs each released
package version into the current environment, so use a separate venv.


## Importing a Word guide

The user's guides were imported once from the Word files in `import/` (not
committed).  For another document:

1. `pandoc GUIDE.docx -t gfm-raw_html --wrap=auto --columns=78
   --extract-media=OUT -o OUT/raw.md`
2. Split it into one page per chapter, add the chapter labels, and replace
   "Section N" with `{numref}` (see [authoring.md](authoring.md)).
3. Rebuild the `[TABLE]` placeholders, which are tables with merged cells,
   from the PDF text (`pdftotext -layout`).
4. Convert EMF/WMF images to PNG, for example by cropping the rendered PDF
   page (`pdftoppm -x -y -W -H`).
5. Move specification tables to `source/products/datasheets/<model>.yaml`, then
   compare every rendered value with the PDF.
