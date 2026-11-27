# Plan: API reference gaps that mislead agents

Status: proposed 2026-11-27, not started.  The fixes are docstring changes
in the upstream projects; this site picks them up when the submodules are
updated for the next docs release.

The site now recommends `pyjoulescope_driver` as the default Python package
(`software/index.md`, "Which Python package to use"), so its reference comes
first.  Each item names what an agent cannot learn from the rendered page
today, found by reading the generated Markdown, `software/*.md`.

## joulescope_driver (`pyjoulescope_driver/binding.pyx`, `doc/sphinx/`)

1. **The subscribe callback signature is missing.**  `Driver.subscribe()`
   says `fn` is "the function to call on each publish", but not that it is
   called as `fn(topic: str, value)` on the driver thread, so it must not
   block and must publish with `timeout=0` (as `fuse.py` in
   pyjoulescope_examples notes).  State the signature, the thread, and link
   `streaming_topics` for the value of `!data` and statistics topics.
2. **Enumeration members are not rendered.**  `ElementType`, `Field`,
   `ErrorCode`, `LogLevel` and `SubscribeFlags` show only "The ... enumeration."
   Their members are documented with `#:` comments, which autodoc cannot read
   from a compiled Cython module.  List the members in each class docstring,
   or document them in `driver.rst` with `autoattribute`.
3. **`query()` and `publish()` value types.**  "The value for the topic"
   does not say that the Python type follows the topic's `dtype` metadata
   (int, float, str, bytes, or dict for JSON).  Say so and link the
   JS320 and JS220 topic pages.
4. **`Driver` methods vs `DeviceContext` methods.**  `DeviceContext` methods
   take topics relative to the device; `Driver` methods take full topics.
   Add one sentence and a two-line example to the `Driver` class docstring,
   since agents mix the two.
5. **JS110 topics.**  JS320 and JS220 have topic pages; the JS110 has none,
   though the driver supports it.  Generate `js110_topics` the same way as
   the JS320 page (`python -m pyjoulescope_driver metadata`), or say on the
   JS220 page which topics the JS110 shares.
6. **Statistics value example.**  `streaming_topics.md` describes the
   statistics value; add one complete example dict (as pyjoulescope's
   `api/statistics` has), which agents copy reliably.

## pyjoulescope (`joulescope/v1/device.py`, `docs/`)

7. **`Device.info()`** returns "the device information structure".  Give its
   keys, or an example.
8. **Quick Start Guide** (`docs/user/quickstart.rst`): "coammand" typo, and
   the examples link points at `tree/master/bin`.  Link
   https://docs.joulescope.com/en/software/pyjoulescope_examples/index.html
   and say that new code should use `pyjoulescope_driver`.
9. **Introduction** (`docs/user/intro.rst`) and `docs/index.rst` welcome the
   reader to "the Joulescope driver", which agents confuse with
   joulescope_driver.  Call it "the joulescope package (pyjoulescope)".

## pyjoulescope_examples

10. The README "download the latest" link points at `archive/master.zip`; the
    branch is `main`.

## Order

Items 1 to 4 first: they change what an agent writes.  Then 5 and 6, then
the pyjoulescope items, which matter less now that the site recommends
`pyjoulescope_driver`.
