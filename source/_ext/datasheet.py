# SPDX-FileCopyrightText: Copyright 2026 Jetperch LLC
# SPDX-License-Identifier: Apache-2.0

"""Render datasheet tables from source/products/datasheets/<model>.yaml.

The YAML format is described in doc/datasheet_format.md.  Usage::

    ```{datasheet} js320
    :section: current_ranges
    ```

Without :section:, every section renders with its title as a rubric.
The YAML files are also published unchanged at /products/datasheets/<model>.yaml.
"""

import copy
import pathlib
import shutil

import yaml
from docutils import nodes
from docutils.parsers.rst import directives
from sphinx.util.docutils import SphinxDirective

SCHEMA = 'joulescope-datasheet/1'
DATASHEET_DIR = pathlib.Path(__file__).resolve().parent.parent / 'products' / 'datasheets'
_TOP_KEYS = {'schema', 'model', 'title', 'revision', 'inherits', 'notes', 'sections'}
_SECTION_KEYS = {'id', 'title', 'columns', 'rows', 'notes', 'remove'}
_CELL_KEYS = {'value', 'unit', 'symmetric', 'notes'}
_ACCURACY_KEYS = {'gain_pct', 'offset', 'notes'}


class DatasheetError(ValueError):
    pass


def _merge(base, child):
    """Merge child sections and notes over base, matching by id."""
    result = copy.deepcopy(base)
    result.update({k: v for k, v in child.items() if k not in ('sections', 'notes', 'inherits')})
    result['notes'] = {**base.get('notes', {}), **child.get('notes', {})}
    sections = {s['id']: s for s in result.get('sections', [])}
    order = [s['id'] for s in result.get('sections', [])]
    for s in child.get('sections', []):
        sid = s['id']
        if s.get('remove'):
            sections.pop(sid, None)
            order.remove(sid)
            continue
        if sid not in sections:
            sections[sid] = copy.deepcopy(s)
            order.append(sid)
            continue
        merged = sections[sid]
        merged.update({k: v for k, v in s.items() if k != 'rows'})
        rows = {r['id']: r for r in merged.get('rows', [])}
        row_order = [r['id'] for r in merged.get('rows', [])]
        for r in s.get('rows', []):
            if r.get('remove'):
                rows.pop(r['id'], None)
                row_order.remove(r['id'])
            elif r['id'] in rows:
                rows[r['id']] = {**rows[r['id']], **r}
            else:
                rows[r['id']] = r
                row_order.append(r['id'])
        merged['rows'] = [rows[i] for i in row_order]
    result['sections'] = [sections[i] for i in order]
    return result


def _validate(data, where):
    def fail(msg):
        raise DatasheetError(f'{where}: {msg}')

    if data.get('schema') != SCHEMA:
        fail(f'schema must be {SCHEMA!r}')
    if extra := set(data) - _TOP_KEYS:
        fail(f'unknown keys {sorted(extra)}')
    notes = data.get('notes', {})
    section_ids = set()
    for s in data.get('sections', []):
        sid = s.get('id')
        if not sid or sid in section_ids:
            fail(f'section id missing or duplicate: {sid!r}')
        section_ids.add(sid)
        if extra := set(s) - _SECTION_KEYS:
            fail(f'{sid}: unknown keys {sorted(extra)}')
        columns = s.get('columns')
        if not isinstance(columns, dict) or not columns:
            fail(f'{sid}: columns must be a non-empty mapping of key: header')
        used = list(s.get('notes', []))
        for key, header in columns.items():
            if isinstance(header, dict):
                if extra := set(header) - {'label', 'notes'}:
                    fail(f'{sid}.columns.{key}: unknown keys {sorted(extra)}')
                used += header.get('notes', [])
        row_ids = set()
        for r in s.get('rows', []):
            rid = r.get('id')
            if not rid or rid in row_ids:
                fail(f'{sid}: row id missing or duplicate: {rid!r}')
            row_ids.add(rid)
            if extra := set(r) - set(columns) - {'id', 'notes'}:
                fail(f'{sid}.{rid}: keys not in columns {sorted(extra)}')
            used += r.get('notes', [])
            for key, cell in r.items():
                if isinstance(cell, dict):
                    allowed = _ACCURACY_KEYS if 'gain_pct' in cell else _CELL_KEYS
                    if extra := set(cell) - allowed:
                        fail(f'{sid}.{rid}.{key}: unknown keys {sorted(extra)}')
                    used += cell.get('notes', [])
        if missing := set(used) - set(notes):
            fail(f'{sid}: undefined notes {sorted(missing)}')


def load(model, directory=DATASHEET_DIR, _seen=()):
    """Load, merge inherited data and validate one datasheet.

    :return: (data, [paths read]).
    """
    path = pathlib.Path(directory) / f'{model}.yaml'
    if model in _seen:
        raise DatasheetError(f'{path}: inheritance cycle {_seen + (model,)}')
    with open(path, encoding='utf-8') as f:
        data = yaml.safe_load(f)
    paths = [path]
    if parent := data.get('inherits'):
        base, base_paths = load(parent, directory, _seen + (model,))
        data = _merge(base, data)
        paths += base_paths
    _validate(data, path)
    return data, paths


def format_number(v):
    if isinstance(v, bool):
        raise DatasheetError(f'boolean is not a datasheet value: {v}')
    return str(v)  # as written; quote values that need trailing zeros


def format_cell(cell):
    """Format a cell as (text, [note keys])."""
    if cell is None:
        return '', []
    if not isinstance(cell, dict):
        return format_number(cell), []
    notes = list(cell.get('notes', []))
    if 'gain_pct' in cell:
        offset, _ = format_cell({**cell['offset'], 'symmetric': True})
        return f'±{format_number(cell["gain_pct"])}% {offset}', notes
    text = format_number(cell['value']) if 'value' in cell else ''
    if cell.get('symmetric'):
        text = '±' + text
    if unit := cell.get('unit'):
        text = f'{text} {unit}'
    return text, notes


def section_table(section, notes):
    """Build a docutils table plus a footnote list for one section."""
    columns = section['columns']
    order = []  # note keys in order of first use, numbered from 1

    def mark(keys):
        result = []
        for k in keys:
            if k not in order:
                order.append(k)
            result.append(str(order.index(k) + 1))
        return ','.join(result)

    table = nodes.table(classes=['datasheet', 'colwidths-auto'])
    tgroup = nodes.tgroup(cols=len(columns))
    table += tgroup
    tgroup.extend(nodes.colspec(colwidth=1) for _ in columns)
    head = nodes.row()
    for header in columns.values():
        header = header if isinstance(header, dict) else {'label': header}
        para = nodes.paragraph(text=str(header.get('label') or ''))
        if keys := header.get('notes'):
            para += nodes.superscript(text=mark(keys))
        head += nodes.entry('', para)
    if any(entry.astext() for entry in head.children):
        tgroup += nodes.thead('', head)
    body = nodes.tbody()
    for r in section.get('rows', []):
        row = nodes.row()
        for i, key in enumerate(columns):
            text, keys = format_cell(r.get(key))
            if i == 0:
                keys = list(r.get('notes', [])) + keys
            para = nodes.paragraph(text=text)
            if keys:
                para += nodes.superscript(text=mark(keys))
            row += nodes.entry('', para)
        body += row
    tgroup += body
    result = [table]
    for k in section.get('notes', []):
        mark([k])
    if order:
        items = nodes.enumerated_list(enumtype='arabic', classes=['datasheet-notes'])
        items.extend(nodes.list_item('', nodes.paragraph(text=notes[k])) for k in order)
        result.append(items)
    return result


class DatasheetDirective(SphinxDirective):
    required_arguments = 1
    option_spec = {'section': directives.unchanged_required}

    def run(self):
        model = self.arguments[0]
        try:
            data, paths = load(model)
        except (OSError, DatasheetError) as ex:
            raise self.error(f'datasheet {model}: {ex}')
        for p in paths:
            self.env.note_dependency(str(p))
        sections = {s['id']: s for s in data['sections']}
        if wanted := self.options.get('section'):
            ids = [s.strip() for s in wanted.split(',')]
            if unknown := [i for i in ids if i not in sections]:
                raise self.error(f'datasheet {model}: unknown sections {unknown}')
            return [n for i in ids for n in section_table(sections[i], data['notes'])]
        result = []
        for s in data['sections']:
            result.append(nodes.rubric(text=s['title']))
            result.extend(section_table(s, data['notes']))
        return result


def _publish(app, exception):
    if exception or app.builder.format != 'html':
        return
    rel = DATASHEET_DIR.relative_to(DATASHEET_DIR.parent.parent)
    if not (pathlib.Path(app.srcdir) / rel).is_dir():  # archive builds
        return
    out = pathlib.Path(app.outdir) / rel
    out.mkdir(parents=True, exist_ok=True)
    for path in sorted(DATASHEET_DIR.glob('*.yaml')):
        load(path.stem)  # never publish an invalid file
        shutil.copyfile(path, out / path.name)


def setup(app):
    app.add_directive('datasheet', DatasheetDirective)
    app.connect('build-finished', _publish)
    return {'parallel_read_safe': True, 'parallel_write_safe': True}
