# V14.5 RC operational UAT

The approved clean report template is bundled with the repository/tool at:

```text
templates/Post-MIC limit_20260911.xlsx
```

Template identity:

```text
SHA-256: a556aa066b9412fb17512bb4f992d26909676c5bc53a138616e2cebef2925724
```

Normal users do **not** browse for or manually install the template. The tool locates
the packaged template automatically and verifies its SHA-256 before processing.

For operational UAT, launch the Windows BAT tool, select `ARUBA_MIC` and/or
`ARUBA_PREMIC` archives, and optionally select `RawData_RD`. V13.6 normalization
and V14.5 report generation must run end-to-end in the same operation.

Expected outputs are the discovered `summary_*.xlsx` and matching
`report_*.xlsx` files.

Acceptance checks include:

- MIC only;
- PREMIC only;
- MIC + PREMIC together;
- RawData present;
- RawData absent;
- Online / Offline automatic discovery;
- no manual summary workbook selection;
- no manual template selection;
- reports open in Microsoft Excel without repair/recovery warnings;
- formulas recalculate;
- six curve-chart DUT legends show SN only;
- Noise Floor chart opens without the logarithmic-axis popup.

Factory inputs and generated reports remain local operational data and must not be
committed to the public repository.

PR #4 stays Draft until the user explicitly passes operational UAT.
