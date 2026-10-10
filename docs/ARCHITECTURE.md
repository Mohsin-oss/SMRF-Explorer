# Architecture and development

SMRF is a static browser app with a separate local Python runner. The hosted UI does not execute Python or SWMM and has no remote model storage endpoint.

| Component | Responsibility |
| --- | --- |
| `dist/core.js` | Immutable fictional model, demo accounting, workflow and checks. |
| `dist/app.js` | Demo rendering, navigation, browser-local scenarios and plan exchange. |
| `dist/project.js` | INP/CSV/GeoJSON adapters, real-data accounting, diagnostics and request schema. |
| `dist/project-ui.js` | Custom uploads, map/inspector, refinement controls and checked result import. |
| `runner/smrf_runner.py` | Fingerprint validation, independent surface accounting, separate INP writing and optional local CLI engine execution. |
| `tests/` | Fictional fixtures and production-handler regression checks, including a real Python subprocess exchange. |
| `scripts/package_runner.py` | Reproducible ZIP generation for the UI download. |
| `scripts/check_distribution.py` | Asset references, package/source consistency and export hygiene. |

Demo scenarios use localStorage. Custom models and surface data stay in browser memory; exports are portable checkpoints. Custom project data are never added to demo scenarios.

The runner independently validates inputs and recalculates fractions. It copies the baseline and changes %Imperv in a separate output. Geometry and topology are preserved. An optional engine hook launches the supplied executable without a shell, running both baseline and refined models with the same external input directory.

The source has no build step, external map tiles, analytics, fonts or JavaScript runtime dependencies. Serve `dist/` over localhost for development. After a source change, run the checks and deploy that directory through a host with verified access control.

## Planned adapters

GIS union/intersection and raster aggregation should produce audited, non-overlapping subcatchment surface totals. Terrain and graph changes should produce new model versions, with structural and hydraulic checks before adoption. Benchmark comparison and 1D–2D coupling require separate workflows; they are not implemented here.

## Verification limits

The 35 regression groups cover accounting, parsing, event handlers, scenario exchange, custom uploads and a real Python processing round trip. The DOM harness does not verify browser layout, native file dialogs or full accessibility. Native browser visual QA and actual SWMM execution were unavailable during preparation.
