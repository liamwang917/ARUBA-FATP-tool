# Changelog

This file tracks the ARUBA FATP tool's version history. Filenames no longer
embed version numbers (see the `chore/restructure-repo-layout` cleanup,
2026-09-08) — use this file plus git/PR history for version context.

## v13 — planned

Not yet implemented. Prioritized backlog from `docs/review_2026-09-07.md`:

1. Separate `Station Result` (from the FR filename) and `APx Section Result`
   (from the CSV's internal `Test Result:` field) instead of collapsing them
   into one filename-derived `Result` column.
2. Add an Import Log / Data QC sheet (missing files, malformed sections,
   duplicates).
3. Validate every DUT's frequency axis instead of trusting only the first
   header encountered.
4. Fix `RawData_RD` section-boundary detection so prefix-matched section
   names cannot bleed into adjacent sections.
5. Preserve station metadata: operator, station, tester, software version,
   start/end time, sensitivity, SNR.
6. Add automatic N / Mean / Max / Min / Range / STDEV statistics per
   frequency.
7. Convert 14-digit timestamps to real Excel datetimes; add freeze panes,
   AutoFilter, sensible column widths, number formats, and PASS/FAIL
   conditional formatting.
8. Add a dashboard/charts once the data model above is stable.

## v12 — current (`src/build_summary.py`)

Calculation-friendly version based on v9 logic.

- Writes Frequency/data values as real Excel numbers so pasted data
  participates in Excel's own Mean/Max/Min/STDEV.
- Keeps SN / Time / Result as text.
- Fixes the `FR_1_3` frequency bug present in earlier versions.
- SN parsing keeps only the `AP...` prefix up to the first underscore.

**Known issue** (see `docs/review_2026-09-07.md`): FR/THD/Phase `Result` is
derived from the FR filename (e.g. `FR_PASS`), which can disagree with the
CSV's internal APx `Test Result:` field. Not yet fixed in v12 — tracked as
v13 item 1 above.

## v9 and earlier

Earlier internal iterations preceding the snapshot first tracked in this
repository (2026-09-07). Not individually preserved here.
