# SPDX-FileCopyrightText: Copyright 2026 Jetperch LLC
# SPDX-License-Identifier: Apache-2.0

import textwrap

import pytest
from docutils import nodes

import datasheet

BASE = '''\
schema: joulescope-datasheet/1
model: BASE
notes:
  n1: First note.
  n2: Second note.
sections:
  - id: ranges
    title: Ranges
    columns:
      range: Range
      accuracy: {label: Accuracy, notes: [n2]}
    rows:
      - id: r1
        range: {value: 10, unit: A, notes: [n1]}
        accuracy: {gain_pct: 0.25, offset: {value: 500, unit: µA}}
      - id: r2
        range: {value: 18, unit: mA}
        accuracy: {gain_pct: 0.1, offset: {value: 5, unit: µA}}
  - id: limits
    title: Limits
    columns: {name: "", min: Min, max: Max, unit: Unit}
    rows:
      - {id: v, name: Voltage, min: -0.3, max: 6, unit: V}
'''


def write(tmp_path, name, text):
    (tmp_path / f'{name}.yaml').write_text(textwrap.dedent(text))


def test_load(tmp_path):
    write(tmp_path, 'base', BASE)
    data, paths = datasheet.load('base', tmp_path)
    assert [s['id'] for s in data['sections']] == ['ranges', 'limits']
    assert paths == [tmp_path / 'base.yaml']


@pytest.mark.parametrize('old, new, match', [
    ('schema: joulescope-datasheet/1', 'schema: other/1', 'schema'),
    ('model: BASE', 'model: BASE\ncolour: red', 'unknown keys'),
    ('      - id: r2', '      - id: r1', 'duplicate'),
    ('notes: [n1]', 'notes: [missing]', 'undefined notes'),
    ('{id: v, name: Voltage,', '{id: v, typ: 1, name: Voltage,', 'not in columns'),
    ('{label: Accuracy, notes: [n2]}', '{label: Accuracy, colour: red}', 'unknown keys'),
    ('offset: {value: 500, unit: µA}}', 'offset: {value: 500, unit: µA}, x: 1}', 'unknown keys'),
])
def test_validation_errors(tmp_path, old, new, match):
    assert old in BASE
    write(tmp_path, 'base', BASE.replace(old, new, 1))
    with pytest.raises(datasheet.DatasheetError, match=match):
        datasheet.load('base', tmp_path)


def test_inherits(tmp_path):
    write(tmp_path, 'base', BASE)
    write(tmp_path, 'child', '''\
        schema: joulescope-datasheet/1
        model: CHILD
        inherits: base
        notes:
          n3: Third note.
        sections:
          - id: ranges
            rows:
              - id: r2
                accuracy: {gain_pct: 0.1, offset: {value: 3, unit: nA}, notes: [n3]}
              - id: r3
                range: {value: 18, unit: µA}
          - id: limits
            remove: true
          - id: extra
            title: Extra
            columns: {name: ""}
            rows: [{id: e, name: E}]
        ''')
    data, paths = datasheet.load('child', tmp_path)
    assert data['model'] == 'CHILD'
    assert 'inherits' not in data
    assert [s['id'] for s in data['sections']] == ['ranges', 'extra']
    ranges = data['sections'][0]
    assert [r['id'] for r in ranges['rows']] == ['r1', 'r2', 'r3']
    assert ranges['rows'][1]['range'] == {'value': 18, 'unit': 'mA'}  # kept from base
    assert ranges['rows'][1]['accuracy']['offset'] == {'value': 3, 'unit': 'nA'}
    assert set(data['notes']) == {'n1', 'n2', 'n3'}
    assert paths == [tmp_path / 'child.yaml', tmp_path / 'base.yaml']


def test_inherits_null_clears_value(tmp_path):
    write(tmp_path, 'base', BASE)
    write(tmp_path, 'child', """\
        schema: joulescope-datasheet/1
        inherits: base
        sections:
          - id: limits
            rows: [{id: v, min: null}]
        """)
    data, _ = datasheet.load('child', tmp_path)
    row = data['sections'][1]['rows'][0]
    assert datasheet.format_cell(row['min'])[0] == ''
    assert row['max'] == 6


def test_inherits_cycle(tmp_path):
    write(tmp_path, 'a', 'schema: joulescope-datasheet/1\ninherits: b\n')
    write(tmp_path, 'b', 'schema: joulescope-datasheet/1\ninherits: a\n')
    with pytest.raises(datasheet.DatasheetError, match='cycle'):
        datasheet.load('a', tmp_path)


@pytest.mark.parametrize('cell, expect', [
    (None, ''),
    (-0.3, '-0.3'),
    (5.0, '5.0'),
    ('0.050', '0.050'),
    ('N/A (off)', 'N/A (off)'),
    ({'value': 10, 'unit': 'A'}, '10 A'),
    ({'value': 5, 'symmetric': True}, '±5'),
    ({'value': 10.4, 'unit': 'A', 'symmetric': True}, '±10.4 A'),
    ({'gain_pct': 0.25, 'offset': {'value': 500, 'unit': 'µA'}}, '±0.25% ±500 µA'),
])
def test_format_cell(cell, expect):
    assert datasheet.format_cell(cell)[0] == expect


def test_format_rejects_bool():
    with pytest.raises(datasheet.DatasheetError):
        datasheet.format_cell(True)


def test_section_table_notes(tmp_path):
    write(tmp_path, 'base', BASE)
    data, _ = datasheet.load('base', tmp_path)
    table, notes = datasheet.section_table(data['sections'][0], data['notes'])
    assert isinstance(table, nodes.table)
    header = table.next_node(nodes.thead)
    # Header notes number first, then rows in order.
    assert header.astext().split() == ['Range', 'Accuracy1']
    first_row = table.next_node(nodes.tbody).children[0]
    assert first_row.children[0].astext() == '10 A2'
    assert [i.astext() for i in notes.children] == ['Second note.', 'First note.']


def test_section_table_without_header(tmp_path):
    write(tmp_path, 'base', BASE)
    data, _ = datasheet.load('base', tmp_path)
    section = {**data['sections'][1], 'columns': {'name': '', 'max': ''}}
    result = datasheet.section_table(section, data['notes'])
    assert len(result) == 1
    assert result[0].next_node(nodes.thead) is None


def test_published_datasheets_are_valid():
    models = sorted(p.stem for p in datasheet.DATASHEET_DIR.glob('*.yaml'))
    assert 'js320' in models
    for model in models:
        data, _ = datasheet.load(model)
        assert data['model'].lower().replace('+', 'plus') == model
