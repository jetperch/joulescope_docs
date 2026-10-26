# Joulescope documentation

Source and build tooling for https://docs.joulescope.com:

* User's guides for the Joulescope JS320, JS220, JS220+ and JS110, and
  for the Joulescope UI (`source/`).
* Datasheets generated from YAML (`source/products/<model>/`).
* The documentation of
  [joulescope_driver](https://github.com/jetperch/joulescope_driver),
  [pyjoulescope](https://github.com/jetperch/pyjoulescope) and
  [jls](https://github.com/jetperch/jls), which stays in those repositories
  and is mounted here at build time (`external/`).

Quick start:

```bash
git clone --recurse-submodules <this repository>
cd joulescope_docs
python3 -m venv .venv && . .venv/bin/activate
pip install -r requirements.txt
python -m joulescope_docs deps
python -m joulescope_docs html
python -m joulescope_docs serve     # http://localhost:8000/
```

Documentation:

* [doc/build.md](doc/build.md): setup and build commands
* [doc/architecture.md](doc/architecture.md): design decisions
* [doc/authoring.md](doc/authoring.md): writing guides and datasheets
* [doc/datasheet_format.md](doc/datasheet_format.md): datasheet YAML
* [doc/deploy.md](doc/deploy.md): AWS and publishing
