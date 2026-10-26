// SPDX-FileCopyrightText: Copyright 2026 Jetperch LLC
// SPDX-License-Identifier: Apache-2.0
//
// CloudFront Function (viewer request): redirect / to the English site, and
// serve index.html for directory URLs.  The S3 REST origin behind Origin
// Access Control has no index documents, so /en/products/ must become
// /en/products/index.html.  See doc/deploy.md.

function handler(event) {
    var request = event.request;
    var uri = request.uri;
    if (uri === '/' || uri === '/index.html') {
        // Each language has its own tree.  302, not 301, so that browsers do
        // not cache it and a future language choice can take its place.
        return {
            statusCode: 302,
            statusDescription: 'Found',
            headers: {location: {value: '/en/'}},
        };
    }
    if (uri.endsWith('/')) {
        request.uri = uri + 'index.html';
    } else if (!/\.[A-Za-z][A-Za-z0-9]*$/.test(uri.substring(uri.lastIndexOf('/')))) {
        // No file extension (v0.19.1 is a version, not an extension):
        // redirect /js320 to /js320/ so relative links work.
        return {
            statusCode: 301,
            statusDescription: 'Moved Permanently',
            headers: {location: {value: uri + '/'}},
        };
    }
    return request;
}
