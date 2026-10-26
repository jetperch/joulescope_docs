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
│   ├── products/  js320/ (guide/, datasheet) ... │ symlinks
│   └── software/  joulescope_ui/ ────────────────┘
│                  joulescope_driver -> ../../external/joulescope_driver/doc/sphinx
└── joulescope_docs/  (build tooling)
        │
        ▼  one sphinx-build
build/site/en/  ──▶ S3 + CloudFront (ci.yml, every green push to main)
build/pdf/en/    (LaTeX builder, same sources; merged into build/site/)
```

The site has four top-level sections: Introduction, Getting Started,
Products (`/en/products/<model>/`: each instrument's guide, datasheet and
PDFs) and Software (`/en/software/`: the UI guide and the mounted
projects).


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

Specification values live once, in `source/products/<model>/<model>_datasheet.yaml`
([datasheet_format.md](datasheet_format.md)).  The `datasheet` directive
(`source/_ext/datasheet.py`, the only custom Sphinx extension) renders the
tables in the user's guide, the datasheet page and the PDFs.  The YAML is
published unchanged at the same path under `/en/` and listed in `/llms.txt`
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
"archive mode" and published under `/en/archive/<project>/<tag>/`.  Each is
built once and kept: on a push to `main`, CI's `archive` job builds and
uploads only the `archives.toml` entries missing from S3, and the site
deploy never touches `/archive/` except the version lists.
Each archive has its own search index, so searching an archive searches only
that version.  A per-project version switcher
(`/en/archive/<project>/versions.json`, generated from `archives.toml`) links
the current site, the archives, and Read the Docs, which remains the
reference for releases made before this site (decision D3).

### URL structure

URLs are permanent once published (rules in `CLAUDE.md`).  `urls.txt` lists
them and a test compares every build with it.  The structure, decided
2026-10-26 before the site was announced:

| URL | Content |
|---|---|
| `/` | Redirects (302) to `/en/` |
| `/en/`, `/en/introduction.html`, ... | Site-wide pages |
| `/en/getting_started/<page>.html` | Getting Started |
| `/en/products/<model>/` | Product page |
| `/en/products/<model>/guide/<chapter>.html` | User's guide |
| `/en/products/<model>/datasheet.html` | Datasheet |
| `/en/products/<model>/<model>_datasheet.yaml` | Datasheet values |
| `/en/products/<model>/<model>_users_guide.pdf`, `<model>_datasheet.pdf` | PDFs |
| `/en/software/<project>/<path>.html` | UI guide and project docs; `<path>` is the page's path in the project's own docs, so Read the Docs URLs map by prefix |
| `/en/archive/<project>/<tag>/` | Release archives, never rebuilt |
| `/llms.txt`, `/llms-full.txt`, `/sitemap.xml`, `/robots.txt`, `/404.html` | Site-wide files |

* **Language prefix.**  Each language has its own tree, so translations can
  be added as `/zh/` and so on without moving anything.  The root redirect
  is a 302, not a 301, so browsers do not cache it and it can later choose
  a language.  The CloudFront Function redirects; `/index.html` also has a
  meta refresh for local previews.
* **One directory per product.**  Everything about a product lives under
  `/en/products/<model>/`, so new material, such as application notes, goes
  beside `guide/` without moving anything.
* Names are lowercase with underscores, matching the repository and package
  names.  Pages end in `.html` (the Sphinx default, as on Read the Docs),
  and directory URLs serve `index.html`.

### Indexes for agents

`source/_ext/site_index.py` publishes, for search engines and LLM agents:

* `<page>.md` next to every `<page>.html`: the rendered page as Markdown
  (`sphinx-markdown-builder`), with includes and datasheet tables expanded
  and every link absolute.  Each HTML page names it with
  `<link rel="alternate" type="text/markdown">`.
* `/llms.txt` ([llmstxt.org](https://llmstxt.org)): how to read the site, the
  datasheet YAML and PDFs, and the full table of contents in reading order,
  linking the Markdown pages.
* `/llms-full.txt`: every Markdown page in one file, in the same order.
* `/sitemap.xml` and `/robots.txt`.

The raw MyST sources (`_sources/`) are not published: they contain
unexpanded includes and directives that agents cannot follow.

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
