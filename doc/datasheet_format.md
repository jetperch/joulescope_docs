# Datasheet YAML format

Each instrument's specifications live in
`source/products/<model>/<model>_datasheet.yaml`.  The `{datasheet}`
directive (`source/_ext/datasheet.py`) renders the tables for HTML and PDF.
The YAML files are also published unchanged at
`https://docs.joulescope.com/en/products/<model>/<model>_datasheet.yaml`, so
tools and LLMs can read the specifications directly.

Values are stored exactly as published, with their published unit, so the
generated tables match the PDF datasheets.  Numbers are YAML numbers where
possible.  Text such as `Vref - 0.1` or `N/A (off)` is a string.  Quote a
number to keep trailing zeros: `"0.050"`.


## File

```yaml
schema: joulescope-datasheet/1   # required, exactly this value
model: JS320                     # model name; the file name is its lowercase form
title: Joulescope JS320 Precision DC Energy Analyzer
revision: "1.3"                  # the user's guide revision the values come from
inherits: js220                  # optional: start from another model's file
notes:                           # footnotes, referenced by key
  sustained_3a: Max 3 A sustained.
sections:                        # tables, in display order
  - ...
```


## Sections

```yaml
- id: current_ranges             # unique within the file
  title: Current measurement specifications
  columns:                       # ordered: key -> header
    range: Range
    accuracy: {label: Accuracy, notes: [accuracy]}   # header with footnote
    guaranteed: Guaranteed
  notes: [some_note]             # optional footnotes for the whole table
  rows:
    - id: range_10a              # unique within the section
      range: {value: 10, unit: A, notes: [sustained_3a]}
      accuracy: {gain_pct: 0.25, offset: {value: 500, unit: µA}}
      guaranteed: {value: 10.4, unit: A, symmetric: true}
```

* `columns` maps each row key to its header.  Use `""` for an empty header.
  When every header is empty, the table has no header row.
* Common column keys: `name` (the parameter), `condition`, `min`, `typ`,
  `max`, `unit`, `range`, `accuracy`, `impedance`, `guaranteed`, `value`.
* A row may only use keys from `columns`, plus `id` and `notes`.  Row
  `notes` attach to the first column.


## Cells

| YAML | Renders |
|---|---|
| `-0.3` | -0.3 |
| `"0.050"` | 0.050 |
| `N/A (off)` | N/A (off) |
| `{value: 10, unit: A}` | 10 A |
| `{value: 5, symmetric: true}` | ±5 |
| `{value: 10, notes: [inrush]}` | 10¹ |
| `{gain_pct: 0.25, offset: {value: 500, unit: µA}}` | ±0.25% ±500 µA |

Cell keys: `value`, `unit`, `symmetric`, `notes`; for accuracy cells,
`gain_pct`, `offset`, `notes`.  When a table has a `unit` column, leave the
unit out of the value cells.


## Footnotes

Footnotes are numbered per table in order of first use: column headers left
to right, then rows top to bottom.  The note text appears as a numbered list
below the table.


## Inheritance

`inherits: <model>` loads the other file first, then applies this file:

* `notes` are merged; this file wins.
* A section with a new `id` is appended.  A section with an existing `id`
  replaces the keys it gives (`title`, `columns`, `notes`), and its rows
  merge by `id`: an existing row's keys are replaced, a new row is appended.
* `remove: true` on a section or row deletes it.
* A row key set to `null` clears an inherited value, which leaves the cell
  empty.

The JS220+ file uses this to hold only its differences from the JS220.


## Directive

````markdown
```{datasheet} js320
:section: current_ranges
```
````

`:section:` takes one id or a comma-separated list.  Without it, every
section renders with its title as a heading.


## Validation

Loading checks the schema value, unknown keys, unique ids, row keys against
`columns`, and that every referenced note exists.  The build fails on an
invalid file, and `tests/test_datasheet.py` loads every published file.
