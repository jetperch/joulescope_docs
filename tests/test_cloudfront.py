# SPDX-FileCopyrightText: Copyright 2026 Jetperch LLC
# SPDX-License-Identifier: Apache-2.0

import json
import shutil
import subprocess

import pytest

from joulescope_docs import ROOT

CASES = {
    '/': '/index.html',
    '/js320/': '/js320/index.html',
    '/js320': '301 /js320/',
    '/js320/fuse.html': '/js320/fuse.html',
    '/datasheets/js320.yaml': '/datasheets/js320.yaml',
    '/archive/jls/v0.19.1': '301 /archive/jls/v0.19.1/',
    '/archive/jls/v0.19.1/': '/archive/jls/v0.19.1/index.html',
    '/_static/font.woff2': '/_static/font.woff2',
}


@pytest.mark.skipif(shutil.which('node') is None, reason='node not installed')
def test_cloudfront_index_function():
    script = (ROOT / 'infra' / 'cloudfront-index.js').read_text() + '''
const out = {};
for (const uri of %s) {
    const r = handler({request: {uri: uri}});
    out[uri] = r.uri || (r.statusCode + ' ' + r.headers.location.value);
}
console.log(JSON.stringify(out));
''' % json.dumps(list(CASES))
    r = subprocess.run(['node', '-e', script], capture_output=True, text=True, check=True)
    assert json.loads(r.stdout) == CASES
