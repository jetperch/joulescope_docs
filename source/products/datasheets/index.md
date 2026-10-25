(datasheets)=

# Datasheets

Each datasheet is generated from a YAML file that holds the published
specification values.  The YAML files are available for tools and LLMs
that analyze Joulescope measurements.

| Instrument | Datasheet | Data |
|---|---|---|
| Joulescope JS320 | {doc}`js320` | [js320.yaml](/products/datasheets/js320.yaml) |
| Joulescope JS220 | {doc}`js220` | [js220.yaml](/products/datasheets/js220.yaml) |
| Joulescope JS220+ | {doc}`js220plus` | [js220plus.yaml](/products/datasheets/js220plus.yaml) |
| Joulescope JS110 | {doc}`js110` | [js110.yaml](/products/datasheets/js110.yaml) |

The JS220+ file contains only the differences from the JS220 and names it
with `inherits: js220`.  See {doc}`format` for the file format.

```{toctree}
:hidden:

js320
js220
js220plus
js110
format
```
