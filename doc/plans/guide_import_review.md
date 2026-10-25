# Guide import review

Status: OPEN.  Items found while converting the Word guides in `import/` to
MyST (2026-10-24).  Each needs a maintainer decision.  "Kept" means the
published text was preserved; "Changed" means the conversion changed it.


## Decisions needed across all guides

* **License of published content.**  The guides say "No part of this User's
  Guide may be reproduced ... without prior written consent".  The datasheet
  YAML is published for tools and LLMs.  Decide the license for the YAML (and
  the site), then add `SPDX-License-Identifier` lines.  The YAML files
  currently carry only a copyright line.
* **Publisher address.**  RESOLVED: the shared Contact and Disclaimers pages
  use Rockville (JS320 2026 and JS220 2025 guides); the Olney address in the
  JS110, JS220+ and UI guides was stale.
* **"Most up-to-date version" link.**  The guides point to
  `http://www.joulescope.com/`; it could now be `https://docs.joulescope.com/`.
* **Section numbers.**  The Word "Table of contents" chapter is gone, so
  every chapter number is lower than in the PDF.  The JS320 overview
  chapters (1-3 in the PDF) are merged into one "Overview" chapter.
* **Guide revisions.**  The converted guides keep their published revision
  numbers.  Decide whether the online version starts a new revision.


## JS320 (`source/js320/`, `source/datasheets/js320.yaml`)

* Kept: Key features says "±10A current pulses (<10 ms, < 3A average per
  second)", but Recommended operating conditions gives ±10 A for < 50 ms and
  ±5 A for < 250 ms.
* Kept: Key benefits says "measures current and voltage 2 million times per
  second", while General specifications gives 1000000 sps (per channel).
* Changed: Voltage measurement "Guaranteed" values had no unit (±15.5,
  ±2.05).  The YAML adds V.
* Changed: General specifications had two rows named "Sampling frequency".
  The second (±5 ppm) is now "Sampling frequency accuracy".
* Changed: "CMMR" → "CMRR" (parasitic table row and voltage accuracy note).
  The row "CMMR on voltage input / Common mode rejection ratio" is now
  "CMRR on voltage input (common mode rejection ratio)".
* Changed: multi-line table labels joined, for example "Shunt switching time,
  Over-range, < 200 ns rise time".
* Changed (typos): "do not active the device" → "activate" (`meet.md`);
  "coloumb" → "coulomb" ×2 (`glossary.md`); "**View **→" bold markup.
* Kept: `theory.md` image25 is a JS220 screenshot (device JS220-000027).
* Changed: the two validation spreadsheets were EMF images; they are now PNG
  crops of the PDF pages (`media/js320_*_validation.png`).  Consider
  replacing them with tables or a downloadable spreadsheet.
* Changed: the isolation component table and the host software repository
  table were rebuilt from the PDF (pandoc could not convert them).


## Joulescope UI (`source/joulescope_ui/`)

* **Personal information:** `media/image39.png` and `media/image40.png`
  (Windows Settings screenshots) show a personal name and email address.
  They are in the published PDF, but consider redacting them for the web.
* Kept: `guide_info.md` copyright says "this Joulescope JS220 User's Guide".
* Kept: `plugins.md` link text "doc/plugin.md", but the URL is
  `docs/plugin.md`.
* Kept: `meet_ui.md` says **Accumulate**, the screenshots say "Accrue".
* Stale (kept): only JS110 and JS220 are mentioned, no JS320
  (`introduction.md`, `key_benefits.md`, `source_code.md`).
* Stale (kept): "2,000,000 samples per second" for all Joulescopes
  (`meet_ui.md`).
* Stale (kept): Windows 10 & 11, macOS 12-15, "only Ubuntu 22.04 LTS",
  Python 3.10+ (`key_benefits.md`, `installation.md`, `source_code.md`).
  The JS320 guide says Ubuntu 26.04 LTS and Python 3.11+.
* Stale (kept): UI 1.1 / 1.1.11 references (`meet_ui.md` triggers, `i18n.md`,
  `plugins.md`); OpenGL settings path (`graphics.md`); CREDITS links use
  htmlpreview and the `master` branch (`source_code.md`).
* Changed (typos): "coulombs I" → "coulombs (C)"; "the SI standard
  prefixes" → "uses the SI standard prefixes"; "adjust" → "adjusts"; split
  bold "marke**rs"; "as need" → "as needed"; "graphics drive" → "driver";
  "coloumb" → "coulomb"; "a one or more" → "one or more"; "merchantability
  of fitness" → "or fitness"; change log "i8n" → "i18n".
* Changed: the toolbar SVG icons had no `viewBox`; they now have
  `width="24" height="24" viewBox="0 0 100 100"` so they render at icon
  size.


## JS220, JS220+ and JS110

The import agents for these guides were stopped before they reported their
review lists.  The pages and YAML were then completed and checked: every
rendered datasheet cell was compared with the PDF text, and the JS220+ merged
tables were compared row by row.  A prose errata review like the JS320 and UI
ones above has **not** been done for these three guides.

* JS220+: the page footer reads "Revision 1.0" in the revision 1.1 PDF.
* JS220, JS220+: Voltage measurement "Guaranteed" values had no unit.  The
  YAML adds V (as for the JS320).
* JS220: `isolation.md` part number "TLP2361(TPL,E" has an unbalanced
  parenthesis in the original.
* JS220: the validation spreadsheet images are identical to the JS320 ones,
  including the 10 A range "Expected Accuracy" of 0.00.
* JS220: "coloumb" → "coulomb" ×2 (`glossary.md`).
* JS110 (`js110.yaml`): the second "Sampling frequency" row is the frequency
  accuracy; a published min of "4.4V" repeated the unit in the cell.
* JS220+: the datasheet YAML removes and re-adds the JS220 current ranges to
  keep the published row order after the new "10 A (≤ 2 A)" row.
* Changed: inline fuse icons (`image30.svg` in the JS220 and JS320 guides)
  had no `viewBox` and rendered at 100 px; now 24 px.  The WEEE symbols
  rendered 597 px tall; now about 60 px.
* Changed: the JS220 guide's 31 images had no alt text (the agent stopped
  before that pass); alt text added after viewing the images.
* Changed (2026-10-24, Matt): OS and Python versions now appear only in
  Getting Started → Installing the Joulescope UI → Supported platforms
  (Windows 11; macOS 26 and 27; Ubuntu 26.04 LTS; Python 3.12+).  The UI
  guide, the JS320/JS220/JS110 host software chapters and box-contents lists
  link there.  The JS110 guide's old Installation section (Windows 7 WinUSB
  steps, "Catalina", Ubuntu 18.04, Python 3.6+) was replaced by a link to
  the shared instructions.  The UI pip instructions now use a venv and
  `python`.
* Changed (2026-10-24, Matt): one shared Glossary, Contact and Disclaimers
  page (formerly each guide's "User's guide information") replaces the five
  per-guide copies; each guide's change log is its own chapter.  Merged from
  the newest text: Rockville address, support@joulescope.com (the JS110
  guide said support@jetperch.com), the EU GPSR contact, "merchantability or
  fitness".  The JS320 compliance link pointed at the js220 page; the Contact
  page lists all three.  The UI guide's copyright notice named the JS220
  guide.  The Disclaimers copyright notice is scoped to the user's guides and
  datasheets, so it does not claim the Apache-2.0 software documentation.
  Datasheet PDFs (Sphinx "howto" class) get no appendices.
* Changed (2026-10-24, Matt): one quick start for all instruments,
  `getting_started/_first_steps.md`, based on the JS320 quick start (the JS220
  one was identical).  First steps and the JS320, JS220 and JS110 Quick start
  chapters include it.  It covers the JS320 connections (front panel and
  wiring diagram), which the JS220 and JS220+ share.  The obsolete JS110 has
  a short own quick start (IN/OUT wiring, two photos) that First steps links
  to; its screenshots of the old UI and the "Oscilloscope Default" menu name
  are gone, as are five now-unused images.  The low-side wiring diagrams in
  JS320/JS220 "How to Connect" had alt text saying "target device
  consumption"; now "current in the low-side wire".
