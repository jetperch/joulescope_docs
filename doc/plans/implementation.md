# Joulescope Unified Documentation: Implementation Plan

Status: IN PROGRESS.  M1-M6 implemented locally, uncommitted (2026-10-24).
M7-M8 (AWS, DNS, cutover) wait for approval.  See section 0.

Target: `https://docs.joulescope.com`, built by this repository (`joulescope_docs`).

The repository was `joulescope_doc` until 2026-10-25, when it was renamed
`joulescope_docs` to match docs.joulescope.com.


## 0. Implementation status and changes from this plan

Done locally; nothing is committed or pushed.

* **M1-M2**: `joulescope_docs` tooling (`mount`, `doxygen`, CLI), the unified
  `source/conf.py`, tests (57), CI workflows (`ci`, `weekly`, `archive`,
  `deploy`), Dependabot.  The strict HTML build has no warnings.  HTML and
  PDF builds are byte-for-byte reproducible.
* **M3-M4**: all five guides imported to MyST; datasheet YAML for the JS110,
  JS220, JS220+ (inherits JS220) and JS320, checked cell by cell against the
  PDFs; datasheet pages; `/llms.txt`.  Open review items:
  [guide_import_review.md](guide_import_review.md).
* **M5**: nine PDFs (five guides, four datasheets) with no LaTeX warnings.
* **M6**: archive mode tested with `jls v0.19.1`, including the switcher and
  the archive's own search.  `archives.toml` is empty.

Changes from the plan below:

* **D3**: there is no backfill.  Read the Docs remains the reference for old
  releases and is listed in each project's version switcher.
* **D5**: the projects are temporary clones in `external/` (gitignored) on
  branch `feature/unified_docs`.  They are not submodules yet.  After the
  upstream changes are committed and pushed, replace them with submodules
  (`git submodule add`); CI already expects submodules.
* **No hashes in the lock (2026-10-25, Matt).**  `requirements.txt` keeps
  exact versions but not SHA-256 hashes, matching the other Jetperch repos.
* **Warning baseline dropped.**  The upstream fixes (U1-U3, U5, U7) made the
  build warning-free, so plain `-W` replaces `known_warnings.txt`.
* **U4 not needed.**  The combined-build link failures came from Sphinx
  resolving symlinks, not from the include wrappers.  They are fixed in
  `mount.patch_relfn2path`, and the driver files stay where they are.
* **Cross-guide links** use `{doc}`/`{ref}` instead of absolute URLs.  In
  PDFs they render as text naming the guide.
* **Datasheet pages** are at `/datasheets/<model>.html`, next to
  `/datasheets/<model>.yaml`, rather than `/<model>/datasheet.html`.
* **Upstream changes made** (documentation only) in the clones:
  * driver: labels, `:project:`, README and getting_started links, docstrings.
  * jls: labels, `:project:`, README link, docstrings, the duplicate
    `@defgroup`.
  * pyjoulescope: labels, the `.txt` suffix, README and install links.
  * all three: their own standalone builds now have no warnings.
  * pyjoulescope_ui (new clone, include only): `docs/plugin.md` typos,
    absolute `capabilities.py` link, and the "no plugin discovery" known
    issue moved there from the UI guide, which now includes the file.
  * driver README, pyjoulescope `intro.rst`/`install.rst`: OS and Python
    versions replaced by absolute links to
    `docs.joulescope.com/getting_started/install_ui.html#supported-platforms`.
    These links are dead until the site is live, so push the clones at
    cutover (doc/deploy.md).
* No non-documentation issues were found in the three repositories, so no
  plans were added to their `doc/plans/`.
* **Site structure (2026-10-24, Matt):** the top level is Introduction,
  Getting Started (Unboxing, Installing the Joulescope UI, First steps),
  Products and Software.  Guides and datasheets moved to `/products/`, the
  UI guide and the mounted projects to `/software/<project>/`, and the raw
  YAML to `/products/datasheets/`.  This supersedes the URL map in 3.2.
  Shared text (box contents, UI installation) moved to include-only
  fragments so it lives once.  The three project index pages got real
  titles (upstream).


## 1. Summary

* One Sphinx build.  The source tree is this repository's `source/` plus
  each project's existing Sphinx directory mounted (symlinked) at build time
  under a URL prefix.  Nothing is copied into Git.
* Project repositories are Git submodules pinned to commit SHAs.  This gives
  deterministic inputs and Dependabot can propose updates.
* The authoritative `conf.py` lives here.  Project `conf.py` files are ignored
  by the combined build.  They keep working for standalone and RTD builds.
* Doxygen runs from each project's own `Doxyfile.in`.  A small Python step
  substitutes the template values, so no Doxygen configuration is duplicated.
* Product user's guides (JS110, JS220, JS220+, JS320, UI) are converted once
  from the staged `.docx` files to MyST Markdown.  They are owned here.
* Datasheet values live in `source/datasheets/<model>.yaml`.  One small
  Sphinx directive renders the tables for HTML and LaTeX.  The raw YAML is
  also published for tools and LLMs.
* PDFs come from the Sphinx LaTeX builder with one `latex_documents` entry per
  guide and per datasheet, built with XeLaTeX in a pinned container.
* Historical archives are standalone, single-project builds of a Git tag.
  They use the same `conf.py` in "archive mode", so each archive has its own
  search index and a PyData version switcher.  Archives are immutable.
* Deployment is S3 + CloudFront from GitHub Actions using OIDC.  Deploying
  requires a manual approval step.  Nothing is published until you approve.


## 2. Audit findings

All findings below were measured on the workspace checkouts on 2026-10-24.
A throwaway prototype of the combined build (scratchpad only, nothing added
to any repository) confirmed the assembly approach in section 3.

### 2.1 Sphinx versions, extensions, themes, dependencies

| | joulescope_driver | jls | pyjoulescope |
|---|---|---|---|
| Latest tag | v2.5.4 | v0.19.1 | v1.7.3 |
| Sphinx root | `doc/sphinx/` | `doc/sphinx/` | `docs/` |
| Theme | sphinx_rtd_theme | sphinx_rtd_theme | alabaster |
| Extensions | E + breathe | E + breathe | E |
| Requirements | R + breathe | R + breathe | `sphinx>=3.1.0`, myst-parser |
| RTD project | `joulescope-driver` | `jls` | `joulescope` |
| RTD image | Ubuntu 24.04, py3.13 | Ubuntu 22.04, py3.11 | Ubuntu 24.04, py3.13 |
| RTD steps | ext + doxygen, PDF | ext + doxygen, PDF | ext, PDF |

* E = autodoc, intersphinx, todo, viewcode, myst_parser.
* R = unpinned sphinx, myst-parser, sphinx_rtd_theme.  pyjoulescope does not
  list its theme (alabaster is built in).
* ext = `python setup.py build_ext --inplace`.  doxygen = CMake `doxygen`
  target.

* Every `conf.py` does `sys.path.insert(0, <repo>)` and imports the package
  to read its version.  Building needs an importable package, which means a
  compiled Cython extension for `pyjoulescope_driver` and `pyjls`, plus numpy.
* `source_suffix` maps `.txt` to Markdown in all three.  As a result
  `pyjoulescope/docs/requirements.txt` is parsed as a document
  (`toc.not_included` warning).  The combined build drops `.txt`.
* No `intersphinx_mapping` is configured anywhere.  The extension is loaded
  but unused.
* Standalone builds with Sphinx 9.2.0, myst-parser 5.1.0, breathe 5.1.0 and
  docutils 0.22.4 on Python 3.14 succeed.  Remaining warnings are listed in
  2.5.

### 2.2 Source layouts and entry points

* **joulescope_driver**: `doc/sphinx/index.rst` has a flat toctree with 11
  entries and 23 pages.  Six `.md` pages are thin MyST wrappers that
  `{include}` content from outside the Sphinx root: `../../README.md`,
  `../../CHANGELOG.md`, `../getting_started.md`, `../streaming_topics.md`,
  `../js320_cal.md`, `../js320_fwup.md`.  Two pages `literalinclude`
  `../js220.txt` and `../js320.json`.  The C API uses 7 `doxygengroup`
  directives.
* **jls**: `doc/sphinx/index.rst` has 12 pages.  `readme.md` and
  `changelog.md` include `../../README.md` and `../../CHANGELOG.md`.  The C
  API uses 5 `doxygengroup` directives.
* **pyjoulescope**: `docs/index.rst` links to `user/index` and `api/index`
  (22 pages).  `user/changelog.md` includes `../../CHANGELOG.md`.
  `api/transition_to_v1.rst` uses `csv-table :file:` in the same directory.
* Breathe directives do not specify `:project:`.  Each project relies on
  `breathe_default_project`.  In one build, two Breathe projects need a
  per-document default (see 3.4).

### 2.3 Conflicting labels, filenames and configuration

Duplicate labels in the combined build, confirmed by Sphinx warnings:

| Label | Defined in |
|---|---|
| `changelog` | driver `changelog.md`, jls `changelog.md`, pyjoulescope `user/changelog.md` |
| `readme` | driver `readme.md`, jls `readme.md` |
| `c_api`, `py_api`, `h_time` | driver and jls |

* The only cross-reference that hits a duplicate is pyjoulescope
  `user/intro.rst` → `` :ref:`Changelog <changelog>` ``.  In the prototype it
  resolved to the right page, but which instance wins depends on read order.
  It must be fixed or pinned by a test.
* Generic labels will collide once the product guides are added: `install`,
  `quickstart`, `intro`, `license`, `api`, `user_guide`, `driver`,
  `program`, `record`.  New content uses prefixed labels (see 3.7).
* Filenames overlap (`index`, `readme`, `changelog`, `c_api`, `py_api`,
  `h_time`), but URL prefixes keep them unique.  Each project's `_static/`
  holds the same favicon and icons.  They are unused in the combined build.
* Breathe: the Doxygen group names are already prefixed and unique (`jsdrv_*`
  vs `jls_*`).  No duplicate C declarations appeared in the prototype.  jls
  defines `@defgroup jls_format` twice in its own headers, which is an
  upstream issue.
* Config conflicts to resolve in the unified `conf.py`: three themes, three
  `project`/`version` values, two Breathe projects.  `html_logo`,
  `html_favicon` and `html_static_path` are per-project today.

### 2.4 Generated API docs and custom build steps

* **autodoc**: driver `py_api.rst` (`pyjoulescope_driver`), jls `py_api.rst`
  (`pyjls`), pyjoulescope `api/*.rst` (`joulescope`, `joulescope.v1`).  Each
  needs the matching package version importable.  autosummary and apidoc
  stubs are not used.
* **Doxygen → Breathe**: CMake `configure_file` turns
  `doc/doxygen/Doxyfile.in` into a Doxyfile.  It uses 4 variables:
  `CMAKE_CURRENT_SOURCE_DIR`, `CMAKE_CURRENT_BINARY_DIR`, `DOXYGEN_DOT_PATH`
  and `VERSION`.  The CMake `doxygen` target for the driver depends on
  building the `jsdrv` library, which is not needed for XML.  Substituting
  the 4 variables in Python and running `doxygen -` with
  `GENERATE_HTML/LATEX=NO` was verified with Doxygen 1.14.0.  It produced
  complete XML for both projects (73 files each), and Breathe rendered every
  group.
* Includes from outside the Sphinx root: README, CHANGELOG, `doc/*.md`, JSON
  and TXT.  This is the main constraint on assembly (3.2).

### 2.5 Links and cross-references needing attention

Present in the standalone builds today (upstream issues):

* Driver `README.md` links to repository files that are not docs:
  `doc/getting_started.md`, `doc/streaming_topics.md`, `third-party/README.md`,
  `example/quickstart.c`, `REUSE.toml`, `LICENSES/Apache-2.0.txt`, and anchor
  `ubuntu-2204-lts`.  These links render broken in Sphinx, and on PyPI.  The
  fix is absolute GitHub URLs in the README.
* `doc/getting_started.md` links to `../README.md`, which does not resolve.
* Docstring RST errors: `pyjoulescope_driver.binding.TimeMap.time_map_get`,
  `pyjls.binding.Reader.time_map_get` and `pyjls.binding.Reader.fsr_statistics`.

New in the combined build:

* `getting_started.md` ↔ `streaming_topics.md` relative Markdown links
  (3 links) fail with `myst.xref_missing`.  These pages are included through
  wrappers.  MyST resolves the link against the real (symlink-resolved)
  path, which is outside the Sphinx source directory.  The upstream fix is to
  move `doc/*.md` into `doc/sphinx/` and drop the wrappers, or to use
  `{doc}` links.  Until then the warnings go on the warning baseline.
* Duplicate labels (2.3).

External URLs that must keep working (printed PDFs, PyPI pages, READMEs):

* `joulescope.readthedocs.io`: pyjoulescope README, plus 4 places in the
  JS110/JS220/JS320 guides.  Plan: RTD redirect to `/pyjoulescope/`.
* `joulescope-driver.readthedocs.io`: driver README, plus 2 places in the
  guides.  Plan: RTD redirect to `/joulescope_driver/`.
* `jls.readthedocs.io`: jls README.  Plan: RTD redirect to `/jls/`.
* `download.joulescope.com/products/joulescope_ui/users_guide/index.html`:
  4 places in the guides; live today (HTTP 200).  Plan: keep it, or replace
  it with a redirect stub (needs approval).
* `download.joulescope.com/docs/validation/index.html`: 3 places in the
  guides.  Out of scope; keep.
* `raw.githubusercontent.com/.../99-joulescope.rules` and `joulescope.inf`:
  guides.  Unchanged.

* RTD has only `latest`/`stable` for `joulescope-driver` and `jls`.  For
  `joulescope`, it also has v0.8.8 to v0.9.4.  RTD is not a usable archive
  source, so archives must be built from tags.
* External hosts referenced (GitHub, joulescope.com, PyPI, Wikipedia and
  others) are checked by `linkcheck` on a schedule, not on every PR.  That
  keeps PR builds deterministic.

### 2.6 Dependencies for one combined build

* Python 3.14 (verified here).  The packages already support 3.15.
* Pinned: `sphinx==9.2.0`, `myst-parser==5.1.0`,
  `breathe==5.1.0`, `pydata-sphinx-theme==0.23.0`, `sphinx-design==0.7.0`
  (optional), `docutils==0.22.4`, `PyYAML==6.0.3`, `numpy`, `pytest`, and
  `sphinxcontrib-svg2pdfconverter` for PDF.  Versions are the latest
  available on 2026-10-24.  The lock file is produced with
  `uv pip compile --universal`.
* For autodoc, the three packages are installed from the submodule sources
  (`pip install ./external/joulescope_driver ...`) in CI.  That needs a C
  compiler, `libusb-1.0-0-dev`/`libudev-dev` and Cython (build-time
  dependencies already declared in each `pyproject.toml`).  For quick local
  builds, `--pypi` installs the latest released wheels instead.  The API docs
  may then lag unreleased source changes, and the build prints a notice.
* Doxygen 1.14.0: the official release binary, verified by SHA-256.  Ubuntu's
  apt version varies by runner image.
* PDF: TeX Live (XeLaTeX, latexmk) and `rsvg-convert`, from a container image
  pinned by digest.
* One-time guide import only: pandoc plus LibreOffice or Inkscape for EMF/WMF
  conversion.  These are not part of the regular build.

### 2.7 Simplest robust assembly approach

Options considered:

1. **Copy `doc/sphinx/` into a build tree**: this breaks every `../../README.md`
   include and both `literalinclude`s, because the paths leave the copied
   directory.  Rewriting the paths would be a custom framework.  Rejected.
2. **Mount the full repository** (`source/joulescope_driver` → repo root):
   includes work, but URLs become `/joulescope_driver/doc/sphinx/c_api.html`
   and need many exclude patterns.  Rejected.
3. **Separate builds joined with intersphinx**: breaks the "one global search
   index" decision.  Rejected.
4. **Symlink each project's Sphinx root under a prefix** (chosen):
   `source/joulescope_driver` → `external/joulescope_driver/doc/sphinx`.
   Sphinx follows directory symlinks.  The OS resolves `..` against the real
   location, so the existing `{include}` and `literalinclude` paths keep
   working.  This was verified in the prototype for all includes, including
   `js320.json` and `js220.txt`.  The relative URL paths are identical to the
   RTD sites, so redirects are a pure prefix mapping.

The one known side effect is the 3 MyST link warnings described in 2.5.

On Windows, a directory symlink needs Developer Mode.  The mount helper falls
back to a directory junction, which needs no privileges.  Windows builds are
best effort; Linux and macOS are the supported local platforms.

### 2.8 Historical version build challenges

* **Tag coverage**: tags with a Sphinx configuration are driver 96/99
  (v1.1+), jls 30/54 (v0.7+) and pyjoulescope 46/71 (v0.9+).  Building all
  172 is wasteful.  Proposal: build the latest patch of each minor release,
  about 50 archives, and add more on request.
* **Toolchain drift**: pyjoulescope v0.9.x through v1.0.8 use `recommonmark`,
  which modern Sphinx no longer supports.  The archive build uses the
  current toolchain and conf.py ("archive mode") and does not use the tag's
  own configuration.  MyST reads their CommonMark.  Any warnings are logged,
  not fatal.
* **autodoc needs the exact historical package**: the archive build installs
  `<package>==<tag version>` from PyPI into a throwaway virtual environment.
  Old releases only have wheels for old Python versions and numpy 1.x, so
  each archive records its Python version in `archives.toml`.  When no wheel
  works, the archive builds with autodoc failing loudly.  The API pages are
  then empty and the archive is flagged.  An alternative is to skip that
  tag.
* **Doxygen**: modern Doxygen with each tag's own `Doxyfile.in`.  Low risk.
  Older tags may lack groups that the pages reference, which shows up as a
  warning.
* **Immutability**: archives go under a separate prefix (`/archive/`) so the
  sync of the current site can never delete them.  Each archive gets an
  `_archive.json` recording the tag SHA, toolchain lock hash and build date.
* **Version switcher**: PyData fetches the switcher JSON at runtime from an
  absolute URL.  Old archives therefore list newer versions without being
  rebuilt.  The JSON is generated from the committed `archives.toml`, so it
  is deterministic and reviewable.
* **Local preview** of archives needs the site served from the root (absolute
  JSON URL).  `python -m joulescope_docs serve` handles this.

### 2.9 Standalone PDF risks

* **Section numbers in prose**: the Word guides cite numbers such as
  "Section 7.5", and the JS220+ guide cites JS220 section numbers.  These
  become `{ref}` or `{numref}` links with `:numbered:` toctrees per guide.
  Each case needs manual review during import.
* **Cross-guide references**: a `{ref}` to a page outside a PDF's toctree
  renders as plain text in LaTeX.  The rule is that guides cite other guides
  by title plus a full URL (`latex_show_urls = "footnote"`).  A LaTeX build
  run with `-W` catches undefined labels.
* **Shared content** (host software sections common to the JS220 and JS320):
  shared fragments go in `_shared/` (excluded from the toctree) and are
  pulled in with `{include}`.  Fragments must not define labels, because
  including them twice would duplicate the labels.
* **Unicode** (µ, Ω, ±, °, ™): requires `latex_engine = "xelatex"` and a font
  with full coverage (for example DejaVu or Noto, license checked).
* **Images**: `architecture.svg` needs SVG to PDF conversion.  The docx
  imports contain 6 EMF/WMF images, which are converted once at import.  The
  pyjoulescope index uses remote images (logo, pepy badge), so the API docs
  are excluded from the product PDFs or wrapped in `{only} html`.
* **Wide specification tables** need `longtable` and explicit column widths.
  The datasheet directive emits both.
* **`sphinx-design`** (cards, tabs) has limited LaTeX support.  Guides avoid
  it outside `{only} html`.
* **Determinism and toolchain size**: TeX Live is several GB, so a pinned
  container is used.  `SOURCE_DATE_EPOCH` is taken from the guide's revision
  commit.  Revision number and date come from per-guide metadata, not from
  the build date.
* **Revision control**: each guide keeps its own revision (for example "JS320
  User's Guide Revision 1.4") and a revision history page.  This is separate
  from Git history.


## 3. Proposed implementation

### 3.1 Repository layout (`joulescope_docs`)

```
joulescope_docs/
├── README.md                    # quick start: clone, build, serve
├── pyproject.toml               # tooling package + pytest config
├── requirements.in              # direct deps (unpinned intent)
├── requirements.txt             # uv pip compile --universal output
├── projects.toml                # mounted projects: prefix, doc dir, package, breathe
├── archives.toml                # archived (project, tag, python) entries
├── .gitmodules
├── external/                    # submodules, pinned SHAs (never edited here)
│   ├── joulescope_driver/
│   ├── jls/
│   └── pyjoulescope/
├── source/                      # Sphinx srcdir; owned content only
│   ├── conf.py                  # THE authoritative configuration
│   ├── index.md                 # landing page + top-level toctree
│   ├── _static/  _templates/
│   ├── _ext/datasheet.py        # YAML → table directive (only custom ext)
│   ├── _shared/                 # include-only fragments (excluded)
│   ├── datasheets/              # js110.yaml js220.yaml js220plus.yaml js320.yaml
│   ├── js110/ js220/ js220plus/ js320/ joulescope_ui/   # MyST user's guides
│   ├── joulescope_driver -> (generated symlink, gitignored)
│   ├── jls               -> (generated symlink, gitignored)
│   └── pyjoulescope      -> (generated symlink, gitignored)
├── joulescope_docs/              # build tooling (python -m joulescope_docs ...)
│   ├── __main__.py              # argparse CLI
│   ├── mount.py                 # create/verify symlinks from projects.toml
│   ├── doxygen.py               # Doxyfile.in substitution + run
│   ├── warnings.py              # compare sphinx warnings to baseline
│   └── archive.py               # tag worktree + archive-mode build + switcher json
├── known_warnings.txt           # regex baseline of upstream warnings, each with an owner
├── tests/                       # pytest for all tooling + a fixture mini-project
├── .github/workflows/
│   ├── ci.yml                   # PR/push: tests, html (-W w/ baseline), pdf artifact
│   ├── linkcheck.yml            # weekly external link check, report only
│   ├── archive.yml              # manual: build one (project, tag) archive artifact
│   └── deploy.yml               # manual + environment approval: S3 sync + invalidation
├── import/                      # staged docx/pdf — NOT committed (see 3.9)
└── doc/
    ├── architecture.md          # decisions (ADR-style sections)
    ├── build.md                 # local + CI build procedures
    ├── authoring.md             # MyST style, label prefixes, PDF-safe rules
    └── plans/implementation.md  # this file
```

`projects.toml` holds data, not code:

```toml
[joulescope_driver]
doc_dir = "doc/sphinx"
package = "pyjoulescope_driver"
breathe = "jsdrv"            # doxygen from doc/doxygen/Doxyfile.in
title = "Joulescope Driver"

[jls]
doc_dir = "doc/sphinx"
package = "pyjls"
breathe = "jls"
title = "JLS File Format"

[pyjoulescope]
doc_dir = "docs"
package = "joulescope"
title = "pyjoulescope"
```

### 3.2 URL map

| Path | Content |
|---|---|
| `/` | Landing page: products, software, search |
| `/js110/`, `/js220/`, `/js220plus/`, `/js320/` | User's guides (HTML) |
| `/<model>/datasheet.html` | Datasheet page generated from YAML |
| `/datasheets/<model>.yaml` | Raw datasheet data (`html_extra_path`) |
| `/joulescope_ui/` | UI user's guide |
| `/joulescope_driver/`, `/jls/`, `/pyjoulescope/` | Project docs, same relative paths as RTD |
| `/pdf/<name>.pdf` | Generated PDFs |
| `/archive/<project>/<version>/` | Immutable historical builds |
| `/archive/<project>/versions.json` | Version switcher data |
| `/llms.txt` | Plain index of guides and raw YAML for LLM tools |

### 3.3 Build commands (no AWS credentials needed)

```
git clone --recurse-submodules <joulescope_docs>
python -m venv .venv && .venv/bin/pip install -r requirements.txt
python -m joulescope_docs deps          # pip install ./external/* (or --pypi)
python -m joulescope_docs html          # mount + doxygen + sphinx-build -W (baseline)
python -m joulescope_docs pdf           # latexpdf (or via the pinned container)
python -m joulescope_docs linkcheck     # sphinx linkcheck builder
python -m joulescope_docs archive joulescope_driver v2.5.4
python -m joulescope_docs serve         # http.server rooted at build/site/
python -m pytest
```

Use `--source joulescope_driver=../joulescope_driver` to mount a sibling
checkout, for example to preview unpushed upstream doc changes.  The CLI is
a thin wrapper around `sphinx-build`, `doxygen` and `git worktree`.  Each
command prints the underlying command it runs.

### 3.4 Unified `conf.py` essentials

* `extensions`: autodoc, intersphinx, todo, viewcode, myst_parser, breathe,
  plus `_ext.datasheet`.  `sphinx_design` is added only if needed.
* `source_suffix = {".rst": "restructuredtext", ".md": "markdown"}` (no `.txt`).
* `exclude_patterns`: `_shared/**`, `**/_build`, and each project's `_static`.
* `html_theme = "pydata_sphinx_theme"`, with a navbar listing products and
  software.
* `nitpicky = True` for owned content.  Upstream noise is handled by the
  warning baseline, not `nitpick_ignore`.
* Breathe: `breathe_projects` comes from `projects.toml`.  A `source-read`
  handler sets `breathe_default_project` from the document prefix (verified
  in the prototype).  It goes away if the projects add `:project:` (U3).
* Per-project version switcher: an `html-page-context` handler with
  priority below 500 sets `context["theme_switcher"]` from the page prefix.
  PyData reads that per page (`pydata_sphinx_theme/__init__.py`, 0.23.0).
  Owned guides get no switcher.
* Archive mode (environment variable `JOULESCOPE_DOCS_ARCHIVE=<project>:<version>`):
  the project's doc directory is the srcdir directly, the switcher shows that
  version, and the version warning banner is on.
* `latex_documents`: one entry per guide and per datasheet; see 3.8.
* `SOURCE_DATE_EPOCH` is respected.  `html_last_updated_fmt` is not used.

### 3.5 Validation

* `sphinx-build -W --keep-going -n` output is filtered by
  `joulescope_docs/warnings.py` against `known_warnings.txt`.  The build fails
  on any warning that is not in the baseline, and also on any baseline entry
  that no longer occurs (stale entries).  Each entry names the upstream fix
  that will remove it.
* `linkcheck` runs weekly and on demand.  It reports but does not block,
  because external sites are nondeterministic.
* An offline redirect-map test checks that every document in each mounted
  project produces `/<prefix>/<docname>.html`.  This guarantees the RTD
  prefix redirects land on real pages.
* A label test checks that `:ref:` targets in owned content resolve inside
  the intended prefix.  It uses `objects.inv` from the build.
* A reproducibility check builds twice and requires byte-identical output.
  It runs weekly in CI.

### 3.6 Datasheet YAML

The YAML stores values exactly as published (value plus unit string), so
tables round-trip with no floating-point reformatting.  LLMs read `µA`
directly.

```yaml
schema: joulescope-datasheet/1
model: JS320
revision: "1.3"
inherits: null                 # js220plus.yaml: inherits: js220 + overrides
conditions:
  temperature: "23 °C ± 10 °C"
  humidity: "20% to 80% RH, non-condensing"
sections:
  - id: absolute_maximum_ratings
    title: Absolute maximum ratings
    columns: [min, max, unit]
    rows:
      - id: usb_voltage
        name: USB voltage
        min: -0.3
        max: 6
        unit: V
  - id: current_ranges
    title: Current measurement specifications
    columns: [range, accuracy, impedance, guaranteed]
    rows:
      - id: range_10a
        range: {value: 10, unit: A, notes: [sustained_3a]}
        accuracy: {gain_pct: 0.25, offset: {value: 500, unit: µA}}
        impedance: {value: 0.01, unit: Ω}
        guaranteed: {value: 10.4, unit: A, symmetric: true}
notes:
  sustained_3a: Max 3 A sustained. See the recommended operating conditions...
```

* Cells take a number, a string (verbatim, for example `"Vref - 0.1"` or
  `"N/A (off)"`), or `{value, unit, symmetric, notes}`.
* `inherits` merges by section and row `id`.  The JS220+ is a JS220 delta:
  its guide says "all other specifications remain the same as the JS220".
* Usage: ```` ```{datasheet} js320 ```` renders all sections, and
  `:sections: current_ranges` renders a subset inside the user's guide.  Both
  the guide and the standalone datasheet render from the same YAML.  Notes
  become table footnotes.
* Validation is plain Python in the loader: known keys, ids unique,
  referenced notes exist, units from an allowed list.  There is no schema
  framework.
* The import surfaced data issues to confirm before publication:
  * The JS220+ v1.1 footer reads "Revision 1.0".
  * JS320 §7.7 has two "Sampling frequency" rows (the second is accuracy in
    ppm).
  * JS320 §7.6 "Guaranteed" values have no unit.
  * JS320 "CMMR" should be "CMRR".

### 3.7 Authoring rules (`doc/authoring.md`)

* New content is MyST.  Existing reStructuredText stays as it is.
* Labels are prefixed by area: `js320-spec-current`, `ui-quickstart`.
  `myst_heading_anchors = 3` gives in-page anchors.
* Rules for content that must also work in PDF: no remote images, no
  `sphinx-design` outside `{only} html`, cite other guides with a full URL,
  no labels in `_shared/` fragments.
* Markdown line length follows the workspace rule: 100 characters maximum,
  with a goal of 80.

### 3.8 PDFs

* `latex_engine = "xelatex"`, plus `latex_documents` entries:
  * `js110/index`, `js220/index`, `js220plus/index`, `js320/index` and
    `joulescope_ui/index`, giving one PDF per user's guide.
  * `js110/datasheet` through `js320/datasheet`, giving one PDF per datasheet.
  * The API references are optional and decided in M5.  RTD builds them as
    PDF today.
* Title page, revision and "last revised" come from per-guide metadata in
  `conf.py`, kept in a single dictionary.
* PDFs are built in a container image pinned by digest
  (`texlive/texlive:<TL year>` or the Sphinx LaTeX image).  They are copied
  into `build/site/pdf/` before deployment.

### 3.9 Product guide import (one-time)

1. `pandoc --extract-media` converts each docx to GFM.  The result is
   cleaned up by hand into MyST pages split at chapter level.  EMF/WMF
   images are converted to SVG or PNG.
2. Specification tables are moved to YAML; the guide uses `{datasheet}`.
3. Hard-coded section numbers are replaced with `{ref}`.
4. The result is compared with the PDF page by page (M4 acceptance).
5. The staged `import/` files (36 MB of binaries) are **not committed**.
   They are listed in `.gitignore` and the docx files are archived outside
   Git.  The repository has no commits yet, so nothing needs removing.
   The import tooling is a documented command sequence in `doc/build.md`,
   not kept code.

### 3.10 Deployment (requires explicit approval, M7)

* S3 bucket (private) behind CloudFront with Origin Access Control, using an
  ACM certificate for `docs.joulescope.com`.
* One CloudFront Function rewrites `/dir/` to `/dir/index.html`.  The S3
  REST origin does not resolve directory indexes; the alternative is a
  public S3 website endpoint.  It is a viewer-request function: no servers,
  no subscription.  Decision D4.
* `deploy.yml`: `workflow_dispatch` only, gated by a GitHub `production`
  environment with required reviewers.  It authenticates with a GitHub OIDC
  role (no stored keys) and syncs `build/site/` with `--delete` excluding
  `archive/*`.  Archives upload with `--no-overwrite` semantics (the workflow
  checks that each key is absent first).  It then invalidates the changed
  paths.
* A staging prefix or distribution is deployed first.  DNS changes are last,
  and only with approval.
* Infrastructure is described in one CloudFormation template, or as
  documented console steps.  You create it; this repository never holds AWS
  credentials.


## 4. Upstream change requests (need your authorization)

None of these are required for M1 to M3.  The baseline tolerates them.  Each
is a small, separate commit in its own repository.

* **U1** (all 3): rename the duplicate labels (`jsdrv-changelog`,
  `jls-changelog`, `pyjoulescope-changelog`, `jls-c-api`, ...) and update the
  one reference.  Removes the duplicate-label warnings and the ambiguous
  `:ref:`.
* **U2** (driver): use absolute GitHub URLs for non-doc links in
  `README.md`, and fix `../README.md` in `doc/getting_started.md`.  Removes
  9 `myst.xref_missing` warnings and fixes the PyPI rendering.
* **U3** (driver, jls): add `:project: jsdrv` / `:project: jls` to the
  `doxygengroup` directives.  Removes the `source-read` Breathe hook.
* **U4** (driver): move `doc/*.md` into `doc/sphinx/` and drop the wrappers,
  or use `{doc}` links.  Removes 3 combined-build link warnings.
* **U5** (driver, jls): fix the 3 binding docstring RST errors.
* **U6** (all 3, after cutover): point the `.readthedocs.yaml` redirects and
  the package `project_urls` at `docs.joulescope.com`.
* **U7** (pyjoulescope): drop `.txt` from `source_suffix` or exclude
  `requirements.txt`.  Removes `toc.not_included`.


## 5. Risks

* **Compiled packages for autodoc.**  Building from source needs a C
  toolchain, which makes CI more complex and local builds slower.
  Mitigation: install from submodule source in CI, offer a `--pypi` fast path
  locally, and cache wheels per submodule SHA.
* **Historical wheels unavailable for any working Python.**  Archives would
  have empty API pages.  Mitigation: a per-archive Python version in
  `archives.toml`; flag or skip the tag; build only the latest patch per
  minor release.
* **Symlink mount relies on OS `..` resolution and Sphinx following
  links.**  A future Sphinx or MyST change could break it.  Mitigation: a
  fixture integration test covers the include patterns used upstream, and
  versions are pinned.
* **Upstream doc changes break the combined build.**  CI goes red after a
  submodule bump.  Mitigation: Dependabot submodule PRs run the full CI, and
  the baseline makes new warnings visible.
* **Generic labels collide as content grows.**  Links point to the wrong
  page.  Mitigation: the label-prefix rule, and duplicate-label warnings are
  fatal for owned content.
* **Docx conversion fidelity** (tables, equations, numbering).  The guides
  could contain errors.  Mitigation: manual page-by-page review against the
  PDF, and the YAML datasheets are reviewed against the PDF tables.
* **TeX Live size and determinism.**  PDF builds are slow and
  nondeterministic.  Mitigation: a container pinned by digest,
  `SOURCE_DATE_EPOCH`, and PDFs built only on main and on release.
* **The global search index grows large.**  The first search gets slower.
  Mitigation: measure the size at each milestone.  It is 265 KB today for the
  3 projects.
* **The CloudFront Function counts as "server-side".**  That would conflict
  with the architecture rule.  Mitigation (D4): use the S3 website endpoint
  instead and accept a public bucket.
* **RTD redirects depend on the RTD projects staying active.**  Otherwise
  old links die.  Mitigation: keep the RTD projects with a redirect-only
  config, and confirm in M8 that RTD supports redirects to an external
  domain.
* **Printed PDFs link to `download.joulescope.com/.../users_guide/`.**
  Customers would lose the UI guide.  Mitigation: keep the existing page, or
  replace it with a meta-refresh stub (needs approval).
* **UI guide ownership.**  The UI guide could drift from UI releases.  See
  D2.


## 6. Acceptance tests

M1 (combined HTML):
* A clean clone plus the documented commands produces `build/site/` on Linux
  with no AWS credentials.
* No warnings outside `known_warnings.txt`, and no stale baseline entries.
* Every upstream document exists at `/<prefix>/<same relative path>.html`
  (redirect-map test).
* Search from `/search.html` returns results from all three projects for
  `jsdrv_open`, `Reader`, `scan`.  Checked by a Playwright smoke test; the
  pre-installed Chromium is available.
* Breathe pages contain the expected C symbols (for example `jsdrv_open`,
  `jls_rd_open`).

M2 (CI and validation):
* The PR workflow runs pytest, the HTML build and the baseline check, and
  uploads the site as an artifact.
* Two consecutive builds are byte-identical, excluding `.doctrees`.
* `linkcheck` produces a report artifact.

M3 (datasheets):
* Unit tests cover the loader, validation errors, `inherits` merge and
  footnote numbering.
* The generated JS320 tables match the published PDF tables cell by cell.
  This is a test fixture transcribed and checked once by a human.
* `/datasheets/js320.yaml` is served byte-identical to the source.

M4 (guides): each guide is reviewed against its PDF, and its links and
labels resolve.

M5 (PDFs): every `latex_documents` entry builds with `-W` in the pinned
container, has no `??` references, and embeds the expected fonts
(`pdffonts`).

M6 (archives):
* `archive joulescope_driver v2.5.4` produces a standalone site with its own
  `searchindex.js`.  Its search finds nothing from the other projects.
* The switcher lists the versions in `archives.toml` and marks the current
  one.
* Rebuilding an existing archive key is refused.

M7 (deploy, approved): staging serves `/`, `/js320/`,
`/joulescope_driver/h_jsdrv.html` and an archive.  The `--delete` sync
leaves `archive/` untouched (tested with a dry run).

M8 (cutover): sampled old RTD URLs redirect to the equivalent new page.


## 7. Milestones

Each milestone builds, passes tests and can be reviewed on its own.  Work
goes on feature branches.

* **M0**: this plan is approved and decisions D1–D6 are made.
* **M1** (after M0): skeleton.  Includes pyproject, the lock file,
  submodules, `projects.toml`, `conf.py`, `mount.py`, `doxygen.py`,
  `warnings.py`, the landing page, `doc/architecture.md`, `doc/build.md` and
  tests.  Result: combined HTML for the 3 projects.
* **M2** (after M1): `ci.yml`, `linkcheck.yml`, the reproducibility check,
  and Dependabot for pip and gitsubmodule.
* **M3** (after M1): the datasheet directive, the JS320 YAML and tests; then
  JS220, JS220+ (inherits) and JS110, one model per commit.
* **M4** (after M3): guide import, one guide per stage in the order JS320,
  JS220, JS220+, JS110, UI.  Each is reviewed against its PDF.
* **M5** (after the first M4 guide): PDF builds in the pinned container,
  published as a CI artifact.
* **M6** (after M2): archive mode, `archive.py`, `archives.toml`, the
  switcher JSON and `archive.yml`; backfill per D3.
* **M7** (after M2, **requires your approval**): AWS template, `deploy.yml`
  and a staging deploy.  No AWS action happens before approval.
* **M8** (after M7, **requires your approval**): production cutover, DNS,
  RTD redirects, download.joulescope.com stubs and the U1–U7 upstream
  changes.


## 8. Decisions needed

* **D1 URL prefixes**: repository names for software (`/joulescope_driver/`,
  `/jls/`, `/pyjoulescope/`) and model names for hardware (`/js320/`).
  Accept? Yes
* **D2 UI guide ownership**: here (as instructed) or in `pyjoulescope_ui`
  (mounted like the other projects)?  The plan assumes here.
  Use joulescope_docs. Many UI concepts are shared, so we probably get a
  better document structure by keeping it out of pyjoulescope_ui.
* **D3 Archive backfill scope**: latest patch per minor (about 50) or every
  tagged release (172)?
  Do not worry about backporting to historical versions. ReadTheDocs can
  be our historical reference for a couple of years until it is obsolete.
* **D4 Directory index**: CloudFront Function (private bucket) or S3 website
  endpoint (public bucket)?
  CloudFront, just like download.joulescope.com
* **D5 Upstream changes U1–U7**: authorize now, or after M2?
  Authorize. For this work, it probably makes sense to have temporary
  separate clones under joulescope_docs. Once everything is working, we
  can commit the changes in these clones and delete them.
  This keeps the ~/repos/Jetperch/ clones working and correct while we
  deal with documentation.
* **D6 API PDFs**: keep generating PDFs of the driver, jls and pyjoulescope
  references, which RTD does today?
  No, I don't see the value.  Let's skip for now.
