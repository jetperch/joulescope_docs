# CLAUDE.md

Guidance for Claude Code in `joulescope_docs`, which builds
https://docs.joulescope.com.  Read `doc/architecture.md` first, and
`doc/authoring.md` before editing content.


## URLs are permanent

Printed guides, product labels, forum posts, search engines and LLM agents
link to this site.  A URL that changes breaks those links forever, so treat
every published URL as a public API.

`urls.txt` lists every published URL, and `tests/test_site.py` fails when
the built site differs from it.  This covers pages under `source/` and the
pages that come from the projects in `external/`, so a submodule update that
renames an upstream page fails too.

Never remove, rename or move a published URL on your own:

1. Stop and tell the user which URLs would change and why, before editing.
2. Only with their explicit approval: publish a redirect page at each old
   URL (for example with the `sphinx-reredirects` extension), so the old URL
   keeps working and stays in `urls.txt`.  Record the decision with its date
   in `doc/architecture.md`, "URL structure".
3. Never edit `urls.txt` by hand to make the test pass.

Adding pages is fine.  Run `python -m joulescope_docs urls` and commit the
new `urls.txt` lines with the change.

What counts as a URL:

* The structure in `doc/architecture.md`, "URL structure": the `/en/`
  language prefix and one directory per product,
  `/en/products/<model>/` with `guide/`, `datasheet.html`, the YAML and the
  PDFs.  New material goes inside this structure.
* Pages, at `<path>.html`, and their Markdown copies at `<path>.md`.
* Directory URLs such as `/en/products/js320/`, which serve `index.html`.
* `<model>_datasheet.yaml`, the PDFs, `/llms.txt`, `/llms-full.txt`,
  `/sitemap.xml`, `/robots.txt`, `/en/objects.inv`.
* `/en/archive/<project>/versions.json`, which archived releases read at
  run time, and `/en/archive/<project>/<tag>/`, which is never rebuilt or
  deleted.
* Section anchors that other sites or documents cite, listed in
  `anchors.txt` and checked by `tests/test_site.py`.  Keep each `(label)=`
  when you rename or move its heading, and never rename a heading whose
  text-derived anchor (such as `#measure-higher-voltages`) is listed there.
  When a new external link cites a section, add a permanent label if the
  section has none, and add the anchor to `anchors.txt`.

Not covered: `_static/`, `_images/`, `_downloads/` and `_modules/`.  The
theme and Sphinx may rename these.


## Checks before you finish

```bash
python -m joulescope_docs html    # warnings are errors
python -m pytest
```

Run `python -m joulescope_docs pdf` too when you change a user's guide or a
datasheet.  Pushes to `main` that pass CI deploy to the live site, so never
push to `main` unless asked.
