# Validation record — 2026-10-10

The GitHub source distribution is based on deployed explorer v0.3.0, source commit `6f4c2165497f2df90c313b64e7670e22bc723214`. Hosting-specific configuration and Git history were excluded. Documentation, CI and packaging utilities were added for portability.

| Check | Result |
| --- | --- |
| Demo suite | 20 groups passed, including 1,248 control combinations. |
| Custom project suite | 15 groups passed, including upload activation, clearing and actual Python request/result exchange. |
| Distribution validation | HTML IDs and labels, asset references and runner ZIP/source consistency passed. |
| Documentation/CI structure | Relative document links and read-only validation workflow checked. |
| Local runtimes | Node.js 24.19.0; Python 3.12.14. |
| Configured GitHub CI runtimes | Node.js 22; Python 3.11. First remote run pending repository upload. |

No native browser layout/file-dialog QA or actual SWMM engine execution was performed. The fixtures are fictional structural/accounting inputs, not calibrated models. Tests establish input/accounting behavior and the supported model-writing exchange, not engineering accuracy or hydraulic improvement.
