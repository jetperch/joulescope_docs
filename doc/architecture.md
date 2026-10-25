# Architecture

`joulescope_docs` builds and publishes https://docs.joulescope.com: the
Joulescope instrument user's guides, the datasheets, the Joulescope UI user's
guide, and the documentation of the software projects.  The implementation
plan with the audit behind these decisions is in
[plans/implementation.md](plans/implementation.md).


## Overview

```
joulescope_docs/                          external/ (one per software project)
├── source/                              ├── joulescope_driver/doc/sphinx/
│   ├── conf.py, index.md                ├── pyjoulescope/docs/
│   ├── introduction.md                  └── jls/doc/sphinx/
│   ├── getting_started/                          ▲
│   ├── products/  js320/ ... datasheets/         │ symlinks
│   └── software/  joulescope_ui/ ────────────────┘
│                  joulescope_driver -> ../../external/joulescope_driver/doc/sphinx
└── joulescope_docs/  (build tooling)
        │
        ▼  one sphinx-build
build/site/  ──▶ S3 + CloudFront (deploy.yml, manual approval)
build/site/pdf/  (LaTeX builder, same sources)
```

The site has four top-level sections: Introduction, Getting Started,
Products (`/products/`: the instrument guides and datasheets) and Software
(`/software/`: the UI guide and the mounted projects).


## Decisions

### One Sphinx build with one configuration

All current documentation is one Sphinx project with one global search
index.  `source/conf.py` is the only configuration used.  The projects'
own `conf.py` files keep working for their standalone and Read the Docs
builds, but the unified build ignores them.

### The projects own their sources; this repository mounts them

Each project keeps its documentation in its own repository.  This repository
holds them as git submodules in `external/` (during initial development,
plain clones) and symlinks each project's Sphinx directory to
`source/software/<project>/`.  Nothing is copied into Git.

Symlinking, rather than copying, keeps the projects' existing relative
`{include}` and `literalinclude` paths working (`../../README.md`,
`../js320.json`), because the operating system resolves `..` from the real
location.  Copying would need path rewriting.

Sphinx resolves symlinks in `BuildEnvironment.relfn2path`, which breaks
relative Markdown links between pages of a mounted project.
`joulescope_docs.mount.patch_relfn2path` maps those paths back through the
mount.  `tests/test_mount.py` builds a fixture both with and without the
patch, so a Sphinx change that makes it unnecessary is noticed.

Each project is served under `/software/<project>/` with its pages at the
same relative paths as on Read the Docs, so old URLs map to new ones by
prefix.

A project can also lend single documents without becoming a site section.
Its `include_dir` (in `projects.toml`) is linked at `source/_include/<name>`,
which Sphinx does not build, and owned pages `{include}` files from it.  The
UI guide's Plugin Support chapter includes `pyjoulescope_ui/docs/plugin.md`
this way, so the plugin documentation stays next to the plugin code.

### C API documentation

Doxygen XML is generated from each project's own `doc/doxygen/Doxyfile.in`.
`joulescope_docs.doxygen` substitutes the four CMake variables instead of
running CMake, which would also build the C library.  Breathe renders it.

### Python API documentation

autodoc imports the documented packages.  CI builds them from the submodule
sources (`python -m joulescope_docs deps`), so the API pages match the
sources.  All build tooling clears `PYTHONPATH`, so a developer setting
cannot make autodoc document another checkout.

### MyST for owned content

The guides and datasheets are MyST Markdown.  The projects' existing
reStructuredText is unchanged.  Conventions: [authoring.md](authoring.md).

### Datasheets from YAML

Specification values live once, in `source/products/datasheets/<model>.yaml`
([datasheet_format.md](datasheet_format.md)).  The `datasheet` directive
(`source/_ext/datasheet.py`, the only custom Sphinx extension) renders the
tables in the user's guide, the datasheet page and the PDFs.  The YAML is
published unchanged at `/products/datasheets/<model>.yaml` and listed in `/llms.txt`
for tools and LLMs.  The JS220+ file inherits from the JS220 file.

### PDFs from the same sources

The Sphinx LaTeX builder produces one PDF per user's guide and per
datasheet (`latex_documents` in `conf.py`), with XeLaTeX for Unicode.  The
software projects' API references are not built as PDFs (decision D6).
PDF builds are reproducible: `SOURCE_DATE_EPOCH` defaults to the last
commit time.

### Versions

The current site always documents the latest sources.  Release archives are
standalone builds of one project tag, made with the same configuration in
"archive mode", published under `/archive/<project>/<tag>/` and never
rebuilt.  Each archive has its own search index, so searching an archive
searches only that version.  A per-project version switcher
(`/archive/<project>/versions.json`, generated from `archives.toml`) links
the current site, the archives, and Read the Docs, which remains the
reference for releases made before this site (decision D3).

### Navigation

The PyData theme is used with one override.  The header bar links the four
top-level sections.  The left sidebar shows the whole site tree from the root
on every page (`source/_templates/sidebar-nav-full.html`,
`html_sidebars` in `conf.py`).  PyData's own sidebar starts below the current
top-level section, which leaves the home page and single-page sections such
as the Introduction without a sidebar.  sphinx-book-theme was considered: it
has the same full-tree sidebar but pins an older PyData release and drops the
header section links.

### Hosting

Static files in a private S3 bucket behind CloudFront with Origin Access
Control, like download.joulescope.com.  A CloudFront Function
(`infra/cloudfront-index.js`) serves `index.html` for directory URLs.  There
are no servers, external search services, or hosting subscriptions.
Deployment is a manual GitHub Actions workflow that needs a reviewer's
approval: [deploy.md](deploy.md).
