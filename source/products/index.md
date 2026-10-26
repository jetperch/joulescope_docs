(products)=

# Products

Each product has its own section, at `/en/products/<model>/`, with its
user's guide, datasheet and PDFs.

| Product | Datasheet | User's guide |
|---|---|---|
| {doc}`Joulescope JS320 <js320/index>` | {doc}`JS320 datasheet <js320/datasheet>` | {doc}`JS320 user's guide <js320/guide/index>` |
| {doc}`Joulescope JS220 <js220/index>` | {doc}`JS220 datasheet <js220/datasheet>` | {doc}`JS220 user's guide <js220/guide/index>` |
| {doc}`Joulescope JS220+ <js220plus/index>` | {doc}`JS220+ datasheet <js220plus/datasheet>` | {doc}`JS220+ user's guide <js220plus/guide/index>` |
| {doc}`Joulescope JS110 <js110/index>` | {doc}`JS110 datasheet <js110/datasheet>` | {doc}`JS110 user's guide <js110/guide/index>` |

The specification values behind each datasheet are also available as YAML
for tools and LLMs, next to the datasheet.  The JS220+ file contains only
the differences from the JS220 and names it with `inherits: js220`.  See
{doc}`datasheet_format` for the file format.

```{toctree}
:hidden:

JS320 <js320/index>
JS220 <js220/index>
JS220+ <js220plus/index>
JS110 <js110/index>
Datasheet YAML format <datasheet_format>
```
