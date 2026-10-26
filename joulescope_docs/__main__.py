# SPDX-FileCopyrightText: Copyright 2026 Jetperch LLC
# SPDX-License-Identifier: Apache-2.0

"""Command line: python -m joulescope_docs <command>.  See doc/build.md."""

import argparse
import functools
import http.server
import importlib.metadata
import json
import os
import pathlib
import shutil
import socket
import subprocess
import sys

from . import BUILD, EXTERNAL, INCLUDE, MOUNT, ROOT, SITE, SOURCE, DOXYGEN_XML
from . import LANGUAGE, PDF_SITE, SITE_LANGUAGE
from . import URLS, load_archives, load_projects, published_urls
from . import doxygen, mount

TOOLS = BUILD / 'tools'
ARCHIVE = BUILD / 'archive'
ARCHIVE_ENV = 'JOULESCOPE_DOCS_ARCHIVE'
# Built per language, served once from the site root.
ROOT_FILES = ['404.html', 'llms.txt', 'llms-full.txt', 'robots.txt', 'sitemap.xml']
# / redirects to the English site; CloudFront redirects first (infra/).
ROOT_INDEX = f'''<!DOCTYPE html>
<html lang="{LANGUAGE}">
<head>
<meta charset="utf-8">
<title>Joulescope Documentation</title>
<link rel="canonical" href="https://docs.joulescope.com/{LANGUAGE}/">
<meta http-equiv="refresh" content="0; url={LANGUAGE}/">
</head>
<body><p><a href="{LANGUAGE}/">Joulescope Documentation</a></p></body>
</html>
'''


def _env(**kwargs):
    # A developer PYTHONPATH pointing at other checkouts would make autodoc
    # silently document the wrong code.
    env = {k: v for k, v in os.environ.items() if k != 'PYTHONPATH'}
    env.update(kwargs)
    return env


def _run(cmd, **kwargs):
    print('+ ' + ' '.join(str(c) for c in cmd), flush=True)
    subprocess.run([str(c) for c in cmd], check=True, **kwargs)


def _checkouts(args, projects):
    result = {name: EXTERNAL / name for name in projects}
    for item in args.source or []:
        name, _, path = item.partition('=')
        if name not in projects or not path:
            raise SystemExit(f'invalid --source {item!r}, expected NAME=PATH with NAME in '
                             f'{", ".join(projects)}')
        result[name] = pathlib.Path(path).resolve()
    return result


def _version(package):
    try:
        return importlib.metadata.version(package)
    except importlib.metadata.PackageNotFoundError:
        raise SystemExit(f'{package} is not installed: run "python -m joulescope_docs deps"')


def _mount(projects, checkouts):
    mount.mount(MOUNT, projects, checkouts)
    mount.mount(INCLUDE, projects, checkouts, key='include_dir')


def _doxygen(projects, checkouts, out_root):
    exe = doxygen.find(TOOLS)
    for name, p in projects.items():
        if 'breathe' in p:
            doxygen.generate(exe, checkouts[name], out_root / name, _version(p['package']))


def _sphinx(builder, srcdir, outdir, env, strict=True, doctrees=None):
    # -E: a fresh environment, so warnings from unchanged files are reported.
    cmd = [sys.executable, '-m', 'sphinx', '-E', '-b', builder, '-c', SOURCE,
           '-d', doctrees or BUILD / 'doctrees' / builder, srcdir, outdir]
    if strict:
        cmd[3:3] = ['-W', '--keep-going']
    _run(cmd, env=env)


def _clean_site():
    """Remove the previous output so moved or deleted pages cannot be deployed."""
    shutil.rmtree(SITE, ignore_errors=True)


def _merge_pdfs():
    """Add the PDFs from the last "pdf" build, at their published paths."""
    if PDF_SITE.is_dir() and SITE.is_dir():
        shutil.copytree(PDF_SITE, SITE, dirs_exist_ok=True)


def cmd_deps(args):
    projects = load_projects()
    checkouts = _checkouts(args, projects)
    pip = [sys.executable, '-m', 'pip', 'install']
    if args.pypi:
        _run(pip + [p['package'] for p in projects.values() if 'package' in p], env=_env())
        return
    # Order matters: pyjoulescope imports the other two.
    for name in ['joulescope_driver', 'jls', 'pyjoulescope']:
        _run(pip + ['--no-deps', '--no-build-isolation', checkouts[name]], env=_env())


def cmd_doxygen_install(args):
    print(doxygen.install(TOOLS))


def cmd_html(args):
    projects = load_projects()
    checkouts = _checkouts(args, projects)
    _mount(projects, checkouts)
    _doxygen(projects, checkouts, DOXYGEN_XML)
    _clean_site()
    _sphinx('html', SOURCE, SITE_LANGUAGE, _env(), strict=not args.no_strict)
    # <page>.md and llms-full.txt for agents, next to the HTML pages.  See
    # source/_ext/site_index.py.
    md = BUILD / 'markdown'
    shutil.rmtree(md, ignore_errors=True)
    _sphinx('markdown', SOURCE, md, _env(), strict=not args.no_strict)
    for path in md.rglob('*'):
        if path.suffix in ('.md', '.txt') and '_downloads' not in path.parts:
            dst = SITE_LANGUAGE / path.relative_to(md)
            dst.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(path, dst)
    for name in ROOT_FILES:
        shutil.move(SITE_LANGUAGE / name, SITE / name)
    (SITE / 'index.html').write_text(ROOT_INDEX, encoding='utf-8')
    _merge_pdfs()


def _pdf_env():
    """Reproducible PDFs: date them by the last commit unless already set."""
    env = _env(FORCE_SOURCE_DATE='1')
    if 'SOURCE_DATE_EPOCH' not in env:
        r = subprocess.run(['git', '-C', ROOT, 'log', '-1', '--format=%ct'],
                           capture_output=True, text=True)
        if r.returncode == 0 and r.stdout.strip():
            env['SOURCE_DATE_EPOCH'] = r.stdout.strip()
    return env


def cmd_pdf(args):
    projects = load_projects()
    checkouts = _checkouts(args, projects)
    _mount(projects, checkouts)
    _doxygen(projects, checkouts, DOXYGEN_XML)  # the LaTeX builder reads every page
    latex = BUILD / 'latex'
    env = _pdf_env()
    _sphinx('latex', SOURCE, latex, env)
    _run(['latexmk', '-xelatex', '-interaction=nonstopmode', '-halt-on-error'] +
         sorted(p.name for p in latex.glob('*.tex')), cwd=latex, env=env)
    shutil.rmtree(PDF_SITE, ignore_errors=True)
    pdf_paths = json.loads((latex / 'pdf_paths.json').read_text())  # from conf.py
    for tex, rel in sorted(pdf_paths.items()):
        dst = PDF_SITE / LANGUAGE / rel
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2((latex / tex).with_suffix('.pdf'), dst)
        print(dst)
    _merge_pdfs()


def cmd_linkcheck(args):
    projects = load_projects()
    _mount(projects, _checkouts(args, projects))
    _sphinx('linkcheck', SOURCE, BUILD / 'linkcheck', _env(), strict=False)


def cmd_archive(args):
    """Build one project at one tag into build/archive/<project>/<tag>."""
    projects = load_projects()
    p = projects.get(args.project)
    if p is None or 'doc_dir' not in p:
        raise SystemExit(f'unknown project or no Sphinx docs: {args.project}')
    checkout = _checkouts(args, projects)[args.project]
    version = args.tag.removeprefix('v')
    if args.install:  # autodoc documents the released package that matches the tag
        _run([sys.executable, '-m', 'pip', 'install', f'{p["package"]}=={version}'], env=_env())
    installed = _version(p['package'])
    if installed != version:
        raise SystemExit(f'autodoc needs {p["package"]}=={version}, found {installed}.\n'
                         f'Install it first, or use --install.')
    outdir = ARCHIVE / args.project / args.tag
    if outdir.exists():
        raise SystemExit(f'{outdir} exists; delete it to rebuild')
    # CI checks out submodules without their tags.
    if subprocess.run(['git', '-C', checkout, 'rev-parse', '-q', '--verify',
                       f'refs/tags/{args.tag}'], capture_output=True).returncode:
        _run(['git', '-C', checkout, 'fetch', '--tags', 'origin'])
    worktree = BUILD / 'worktrees' / f'{args.project}-{args.tag}'
    if worktree.exists():
        _run(['git', '-C', checkout, 'worktree', 'remove', '--force', worktree])
    _run(['git', '-C', checkout, 'worktree', 'add', '--detach', worktree, args.tag])
    try:
        if 'breathe' in p:
            out = BUILD / 'doxygen-archive' / args.project
            doxygen.generate(doxygen.find(TOOLS), worktree, out, version)
        env = _env(**{ARCHIVE_ENV: f'{args.project}:{args.tag}'})
        _sphinx('html', worktree / p['doc_dir'], outdir, env, strict=False,
                doctrees=BUILD / 'doctrees' / 'archive' / args.project / args.tag)
    finally:
        _run(['git', '-C', checkout, 'worktree', 'remove', '--force', worktree])
    print(f'Archive: {outdir}')


def cmd_archive_list(args):
    """Print "project tag" for every archives.toml entry, for CI."""
    for project, tags in load_archives().items():
        for tag in tags:
            print(project, tag)


def cmd_urls(args):
    """Rewrite urls.txt from build/site.  Review the diff: see CLAUDE.md."""
    if not (SITE_LANGUAGE / 'index.html').exists() or not PDF_SITE.is_dir():
        raise SystemExit('build the site first: python -m joulescope_docs html, then pdf')
    header = [line for line in URLS.read_text(encoding='utf-8').splitlines()
              if line.startswith('#')] if URLS.exists() else []
    URLS.write_text('\n'.join(header + [''] + published_urls(SITE)) + '\n', encoding='utf-8')
    print(f'Wrote {URLS}; review "git diff urls.txt".')


def cmd_serve(args):
    handler = functools.partial(http.server.SimpleHTTPRequestHandler, directory=str(args.dir))
    if args.host not in ('localhost', '127.0.0.1', '::1'):
        print(f'WARNING: serving on {args.host} makes the site visible to your network.',
              flush=True)
    url_host = socket.gethostname() if args.host in ('0.0.0.0', '::') else args.host
    print(f'Serving {args.dir} at http://{url_host}:{args.port}/', flush=True)
    http.server.ThreadingHTTPServer((args.host, args.port), handler).serve_forever()


def parser():
    p = argparse.ArgumentParser(prog='python -m joulescope_docs', description=__doc__)
    sub = p.add_subparsers(dest='command', required=True)

    def add(name, fn, help_):
        s = sub.add_parser(name, help=help_)
        s.add_argument('--source', action='append', metavar='NAME=PATH',
                       help='Use this project checkout instead of external/NAME.')
        s.set_defaults(fn=fn)
        return s

    add('deps', cmd_deps, 'Install the documented packages for autodoc.').add_argument(
        '--pypi', action='store_true', help='Install released wheels instead of building.')
    add('doxygen-install', cmd_doxygen_install, 'Install the pinned Doxygen (Linux x86_64).')
    add('html', cmd_html, 'Build the HTML site into build/site.').add_argument(
        '--no-strict', action='store_true', help='Do not treat warnings as errors.')
    add('pdf', cmd_pdf, 'Build the PDFs into build/pdf, merged into build/site.')
    add('linkcheck', cmd_linkcheck, 'Check external links (report only).')
    s = add('archive', cmd_archive, 'Build a standalone archive of one project tag.')
    s.add_argument('project')
    s.add_argument('tag')
    s.add_argument('--install', action='store_true',
                   help='First pip install the released package version for autodoc.')
    add('archive-list', cmd_archive_list, 'List the archives.toml entries.')
    add('urls', cmd_urls, 'Rewrite urls.txt from the built site.')
    s = add('serve', cmd_serve, 'Serve the built site locally.')
    s.add_argument('--port', type=int, default=8000)
    s.add_argument('--host', default='localhost',
                   help='Address to listen on.  Use 0.0.0.0 to serve to the LAN.')
    s.add_argument('--dir', type=pathlib.Path, default=SITE)
    return p


def main(argv=None):
    args = parser().parse_args(argv)
    os.chdir(ROOT)
    try:
        args.fn(args)
    except subprocess.CalledProcessError as ex:
        raise SystemExit(f'failed with exit code {ex.returncode}')


if __name__ == '__main__':
    main()
