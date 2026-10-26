# Authoring guide

How to write documentation owned by this repository: the instrument user's
guides, the Joulescope UI user's guide and the datasheets.  The software
projects keep their own sources and conventions; see
[architecture.md](architecture.md).


## Format

* New content is MyST Markdown (`.md`).  Existing reStructuredText in the
  software projects stays reStructuredText.
* Line length: 100 characters maximum, with a goal of 80.  Tables and URLs
  may exceed it.
* Use the characters directly: µ, Ω, ±, °, ™, ®, →.  Do not use HTML.
* Do not use `sphinx-design` components or raw HTML.  The same sources
  produce the PDFs.


## Site layout

```
source/
├── index.md                  # landing page; top-level toctree
├── introduction.md
├── getting_started/          # unboxing, install_ui, first_steps
├── products/
│   ├── index.md              # product table: datasheet and user's guide
│   ├── datasheet_format.md   # the datasheet YAML format
│   └── js320/ js220/ js220plus/ js110/    # one directory per product
└── software/
    ├── index.md
    ├── joulescope_ui/        # UI user's guide
    └── joulescope_driver, pyjoulescope, jls   # mounted, see architecture.md
```

Everything about one product lives in its directory, published at
`/en/products/<model>/`.  Add new kinds of product material, such as
application notes, as siblings of `guide/`:

```
source/products/js320/
├── index.md              # product page: links the guide, datasheet, PDFs
├── datasheet.md          # datasheet page
├── js320_datasheet.yaml  # specification values (published as is)
├── _specifications.md    # include-only: headings + {datasheet} directives
└── guide/                # the user's guide
    ├── index.md          # label, title, revision, cover image, numbered toctree
    ├── overview.md       # one page per chapter, short snake_case names
    ├── ...
    ├── _key_features.md  # include-only fragments (excluded from the build)
    ├── _in_the_box.md
    └── media/            # images used by this guide only
```

The PDFs are published next to the product page:
`/en/products/js320/js320_users_guide.pdf` and `js320_datasheet.pdf`.  Link
published files that are not pages with the `site:` scheme, which adds the
language prefix: `[PDF](site:products/js320/js320_datasheet.pdf)`.

Pages common to all guides exist once, at the top level: `glossary.md`,
`contact.md` and `disclaimers.md`.  Guides link to them instead of having
their own copies, and `latex_appendices` in `conf.py` appends them to every
guide PDF.  Each guide keeps its own `changelog.md` chapter.

Text needed in more than one place lives once, in an include-only fragment
named `_*.md`, and the pages `{include}` it.  For example, the Getting
Started pages include `_in_the_box.md` from each guide and `_installation.md`
from the UI guide, and the JS320 and JS220 Quick start chapters include
`getting_started/_first_steps.md`.  Fragments contain no labels.  To
include a fragment with images from another directory, add
`:relative-images:`.

`index.md` starts with front matter that records the guide revision:

```markdown
---
revision: "1.3"
date: 2026-06-25
---

(js320)=

# Joulescope JS320 User's Guide
```

The toctree in `index.md` uses `:numbered:` so chapters and sections are
numbered as in the PDF guides.


## Labels and cross-references

* Labels are prefixed with the guide: `js110-`, `js220-`, `js220plus-`,
  `js320-`, `ui-`, and `datasheet-` for datasheet pages.  Every chapter has a
  label: `(js320-fuse)=` before `# Fuse`.  Add labels to other headings only
  when something links to them.
* Refer to a numbered section with `` {numref}`js320-fuse` ``, which renders
  "Section 13".  Use `` {ref}`text <label>` `` for other links within the
  site.  Never type a section number.
* Do not use the `{glossary}` directive.  Glossary terms are global in
  Sphinx and the guides share terms.  Use a definition list instead.


## Links between guides and to software documentation

Link to other guides and to the software documentation with `{doc}` or
`{ref}`, for example `` {doc}`/software/joulescope_ui/index` ``.  In a PDF,
links that leave the guide are rendered as text.  Name the guide in the
link text so the PDF reader knows where to look:
"see the {doc}`Joulescope UI User's Guide </software/joulescope_ui/index>`".

Replace old documentation URLs:

| Old | New |
|---|---|
| `download.joulescope.com/products/joulescope_ui/users_guide/...` | `` {doc}`/software/joulescope_ui/index` `` |
| `joulescope.readthedocs.io` | `` {doc}`/software/pyjoulescope/index` `` |
| `joulescope-driver.readthedocs.io` | `` {doc}`/software/joulescope_driver/index` `` |
| `jls.readthedocs.io` | `` {doc}`/software/jls/index` `` |

Other external URLs stay as they are.


## Supported platforms

Operating system and Python versions appear in one place only: the
"Supported platforms" section of `getting_started/install_ui.md`.  Everywhere
else, name the platforms without versions and link there with
`` {ref}`supported platforms <supported-platforms>` ``.  Change logs keep
their historical versions.


## Specifications and datasheets

Specification values live only in
`source/products/<model>/<model>_datasheet.yaml`
([datasheet_format.md](datasheet_format.md)).  Do not type specification
values into Markdown tables.

* `source/products/<model>/_specifications.md` is an include-only fragment
  with the specification headings, the `{datasheet}` directives and the
  explanatory prose.  It contains no labels.
* The guide chapter `source/products/<model>/guide/specifications.md` holds
  the chapter label and title, then includes the fragment.
* The datasheet page `source/products/<model>/datasheet.md` holds a short
  product summary, then includes the key-features fragment and the
  specifications fragment.

```markdown
(js320-specifications)=

# Specifications

```{include} ../_specifications.md
```
```


## Images

* Images live in the guide's `media/` directory, named with the guide's
  prefix: `js320_image5.png`, `ui_image10.svg`.  Image file names must be
  unique across the site.  Sphinx copies all images into one `_images/`
  directory and renames clashes in build order, so a duplicate name lets a
  cached URL show a different picture after pages move.  A test enforces
  this.
* Give every informative image short alt text.  Keep alt text on one line:
  a line break inside alt text is dropped in HTML, joining the words.
  Remove the Word placeholder "A screenshot of a computer Description
  automatically generated".
* Use PNG, JPEG or SVG.  EMF and WMF images are converted to PNG, for
  example by cropping the rendered PDF page.
* Images shared by several guides go in `source/_static/media/` only once
  they are actually shared.


## Equations, subscripts and warnings

* Equations use the math directive.  pandoc writes ```` ``` math ````; change
  it to ```` ```{math} ````.
* Subscripts use the `{sub}` role: ``V{sub}`MEASURED` `` (pandoc writes
  `V_(MEASURED)`).  Unicode subscript digits such as R₁ are fine.
* The Word guides show warnings as a one-row table with a ⚠️ cell.  Use an
  admonition instead:

  ```markdown
  :::{warning}
  The voltage from I+ to I- must never exceed ±20 V.
  :::
  ```

  Use `{note}` and `{tip}` the same way.


## Tables

* Use pipe tables for simple tables.  Use `{list-table}` when a cell needs
  more than one paragraph or a list.
* Merged cells are not supported.  Restructure the table, or split it.
* Every table needs a body.  pandoc turns Word layout tables (an icon next
  to a paragraph) into header-only tables, which break the PDF build.  Write
  the image, then the paragraph, or use an admonition for warnings.


## Content fidelity

The guides are imported from the Word originals in `import/`, which is not
committed.  Keep the technical content exactly.  When a value or statement
looks wrong or two places disagree, keep the published text and record the
issue in [plans/guide_import_review.md](plans/guide_import_review.md) for
review.  Fix spelling and obvious typos, and list those fixes too.


## Checking your work

```
python -m joulescope_docs html          # strict: warnings are errors
python -m joulescope_docs serve         # http://localhost:8000/
```

The build must finish without warnings.
