# SPDX-FileCopyrightText: Copyright 2026 Jetperch LLC
# SPDX-License-Identifier: Apache-2.0

"""Command line: python -m joulescope_docs <command>.  See doc/build.md."""

import argparse
import functools
import http.server
import importlib.metadata
import os
import pathlib
import shutil
import socket
import subprocess
import sys

from . import BUILD, EXTERNAL, INCLUDE, MOUNT, ROOT, SITE, SOURCE, DOXYGEN_XML, load_projects
from . import doxygen, mount

TOOLS = BUILD / 'tools'
ARCHIVE = BUILD / 'archive'
ARCHIVE_ENV = 'JOULESCOPE_DOCS_ARCHIVE'


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
    """Remove the previous HTML output so moved or deleted pages cannot be
    deployed.  The PDFs, built separately by "pdf", are kept."""
    if SITE.exists():
        for path in SITE.iterdir():
            if path.name != 'pdf':
                shutil.rmtree(path) if path.is_dir() and not path.is_symlink() else path.unlink()


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
    _sphinx('html', SOURCE, SITE, _env(), strict=not args.no_strict)


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
    out = SITE / 'pdf'
    out.mkdir(parents=True, exist_ok=True)
    for tex in sorted(latex.glob('*.tex')):  # skip the converted SVG images
        pdf = tex.with_suffix('.pdf')
        shutil.copy2(pdf, out / pdf.name)
        print(out / pdf.name)


def cmd_linkcheck(args):
    projects = load_projects()
    _mount(projects, _checkouts(args, projects))
    _sphinx('linkcheck', SOURCE, BUILD / 'linkcheck', _env(), strict=False)


def cmd_archive(args):
    """Build one project at one tag as a standalone archive."""
    projects = load_projects()
    p = projects.get(args.project)
    if p is None or 'doc_dir' not in p:
        raise SystemExit(f'unknown project or no Sphinx docs: {args.project}')
    checkout = _checkouts(args, projects)[args.project]
    version = args.tag.removeprefix('v')
    installed = _version(p['package'])
    if installed != version:
        raise SystemExit(f'autodoc needs {p["package"]}=={version}, found {installed}.\n'
                         f'Install it first, for example: pip install {p["package"]}=={version}')
    outdir = ARCHIVE / args.project / args.tag
    if outdir.exists():
        raise SystemExit(f'{outdir} exists; archives are immutable (delete it to rebuild)')
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
    print(f'Archive: {outdir}\nAdd "{args.tag}" to archives.toml [{args.project}] versions.')


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
    add('pdf', cmd_pdf, 'Build the PDF guides into build/site/pdf.')
    add('linkcheck', cmd_linkcheck, 'Check external links (report only).')
    s = add('archive', cmd_archive, 'Build a standalone archive of one project tag.')
    s.add_argument('project')
    s.add_argument('tag')
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
