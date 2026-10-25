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
pip install --require-hashes -r requirements.txt
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
| `python -m joulescope_docs linkcheck` | `build/linkcheck/output.txt` (external links) |
| `python -m pytest` | Tooling tests, plus site checks when `build/site/` exists |

To preview changes to a project's documentation, mount another checkout:

```bash
python -m joulescope_docs html --source joulescope_driver=../joulescope_driver
```

Each command prints the commands it runs.  `html` and `pdf` always rebuild
from scratch (`sphinx-build -E`), so warnings in unchanged files are never
hidden.


## Updating dependencies

Edit `requirements.in`, then:

```bash
uv pip compile --universal --generate-hashes --python-version 3.13 \
    requirements.in -o requirements.txt
```

Dependabot proposes updates to `requirements.txt`, the GitHub Actions and the
submodules.  Each runs the full CI.


## Release archives

When a project releases, archive the documentation of the previous release
before the current site moves on:

```bash
pip install pyjls==0.19.1          # autodoc must import the released package
python -m joulescope_docs archive jls v0.19.1
```

The archive is written to `build/archive/<project>/<tag>/` and refuses to
overwrite an existing one.  Add the tag to `archives.toml` (newest first) so
the version switcher lists it.  In CI, run the `archive` workflow, then
`deploy` with its run id.


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
