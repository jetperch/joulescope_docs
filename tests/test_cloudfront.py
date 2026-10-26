# SPDX-FileCopyrightText: Copyright 2026 Jetperch LLC
# SPDX-License-Identifier: Apache-2.0

import json
import shutil
import subprocess

import pytest

from joulescope_docs import ROOT

CASES = {
    '/': '302 /en/',
    '/index.html': '302 /en/',
    '/en/': '/en/index.html',
    '/en': '301 /en/',
    '/en/products/js320/': '/en/products/js320/index.html',
    '/en/products/js320': '301 /en/products/js320/',
    '/en/products/js320/guide/fuse.html': '/en/products/js320/guide/fuse.html',
    '/en/products/js320/js320_datasheet.yaml': '/en/products/js320/js320_datasheet.yaml',
    '/en/archive/jls/v0.19.1': '301 /en/archive/jls/v0.19.1/',
    '/en/archive/jls/v0.19.1/': '/en/archive/jls/v0.19.1/index.html',
    '/en/_static/font.woff2': '/en/_static/font.woff2',
    '/llms.txt': '/llms.txt',
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
