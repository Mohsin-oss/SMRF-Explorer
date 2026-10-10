# SMRF — SWMManywhere Model Refinement Explorer

A working prototype for **Mohsin Ahmad’s SWMManywhere ecosystem**: inspect a synthetic drainage model, preview practical refinements and apply supported surface changes to your own SWMM model through a local Python runner.

**Version:** 0.3.0 · **Status:** research prototype · **Repository visibility:** private

[Open the private workspace](https://smrf-model-explorer.mr-hydrogen-bond.chatgpt.site/?v=3#project) · [User guide](docs/USER_GUIDE.md) · [Data formats](docs/DATA_FORMATS.md) · [Runner guide](runner/README.md)

## What works

| Capability | Current behavior |
| --- | --- |
| Synthetic drainage explorer | Inspect six fictional subcatchments, eight nodes and seven pipes over an illustrative 18 ha district. |
| Demo refinements | Change impervious inputs, street widths, parking and known green classification errors; see live surface accounting. |
| Scenario comparison | Save browser-local demo scenarios and exchange portable JSON plans. |
| Custom model import | Load a baseline INP, optional matching GeoJSON and prepared surface CSVs locally. |
| Customization controls | Visible on the opening screen; enabled after a valid INP upload. |
| Real-data refinements | Keep baseline fractions with mapped corrections, replace them with mapped roofs/roads, or edit percentages manually. |
| Local processing | Export a fingerprinted request and write a separate refined INP with the Python runner. |
| Checked result import | Match the baseline, settings, returned fractions, file fingerprints and other INP fields before downloading the result. |
| Geometry changes | DTM redelineation and street-graph regeneration are recorded as pending requests; geometry remains unchanged. |
| Hydraulic execution | Optional user-supplied SWMM CLI hook runs locally. The hosted site does not execute SWMM. |

This is an independent SMRF prototype, not an official SWMManywhere release. No calibration accuracy or improved flood performance is inferred from changing surface inputs.

## Quick start on your computer

Use **Python 3.11 or newer**. Node.js 22 is needed only to run the regression tests. No npm package installation, JavaScript build step or GIS dependency installation is required for the current surface-table workflow.

Extract the project ZIP or clone the private repository:

```powershell
git clone https://github.com/Mohsin-oss/SMRF-Explorer.git
cd SMRF-Explorer
python -m http.server 8000 --bind 127.0.0.1 --directory dist
```

Open **http://localhost:8000/**. Use **Upload & customize** for your own model or **Demo explorer** for fictional data. Stop the server with `Ctrl+C`.

Your existing `swmm-env` can run the Python surface workflow. Alternatively, a normal Python installation works because the runner uses only the standard library. You can also open `dist/index.html` directly for a quick look; serving it on localhost is the recommended route for consistent browser file and cryptography behavior.

## A small practice run

1. In **Upload & customize**, choose `tests/fixtures/custom_model.inp` and `tests/fixtures/surfaces.csv`.
2. Review the two catchments: 5 ha total, with area-weighted baseline imperviousness of **46.0%**.
3. Confirm the surface assumptions and enable parking, green correction and street-width refinement at 8 m. The proposed fraction becomes **55.2%**.
4. Export the Python processing request and run:

```powershell
python runner/smrf_runner.py --request "path/to/smrf-processing-request.json" --output "path/to/smrf-output/run_01"
```

5. Import `smrf-result.json` with the same loaded baseline and settings. Download the returned `refined.inp`.

These fixtures are fictional and intended for structural/accounting validation. They do not contain a complete rainfall setup for hydraulic simulation. Each run needs a new output directory to preserve earlier outputs.

## Bring your own data

The required input is one SWMM `.inp`. Optional GeoJSON supplies matching display geometry. A surface CSV supplies prepared roof, road, parking and verified green-error areas in hectares, plus baseline road width in metres.

```csv
catchment_id,roof_ha,road_ha,parking_ha,green_correction_ha,baseline_road_width_m
C1,0.5,0.2,0.1,0.04,6
```

Prepare spatial clipping, overlap resolution, coverage and CRS checks in QGIS or a separate adapter. The current app does not perform polygon union/intersection, raster classification or terrain processing. Missing values remain explicit rather than becoming zero. Read [the data guide](docs/DATA_FORMATS.md) before using corrections on a real model.

## Verification

From the repository root:

```powershell
npm test
python scripts/check_distribution.py
```

The **35 validation groups** cover parsing, SI/US conversion, 1,248 demo control combinations, accounting bounds, navigation, upload/clear behavior, scenario persistence and an actual production-handler → Python-runner → result-import exchange. Native browser visual QA and actual SWMM engine execution were unavailable during preparation.

The GitHub Actions workflow runs these checks on pushes and pull requests using Node.js 22 and Python 3.11. It has no website publishing step. Its first remote run will be verifiable after the repository upload.

After editing the runner or its guide, refresh its downloadable ZIP:

```powershell
python scripts/package_runner.py
python scripts/check_distribution.py
```

## Project files

| Path | Purpose |
| --- | --- |
| `dist/` | Complete static app and downloadable runner ZIP; use this as a website root. |
| `runner/` | Standard-library Python processor and execution instructions. |
| `tests/` | Regression checks, DOM harness and explicitly fictional fixtures. |
| `scripts/` | Runner packaging and distribution validation. |
| `docs/` | User guide, schemas/accounting, architecture and deployment paths. |
| `.github/workflows/ci.yml` | Automated tests; no public deployment. |
| `CHANGELOG.md` | Implemented version history. |
| `CONTRIBUTING.md` | Development and pull-request guidance. |

## Privacy and hosting

Custom files are read in browser memory and are not sent to a server by this app. Closing or reloading the page clears the custom workspace. Demo scenarios use localStorage. Exported processing requests and result packs contain model data; keep them outside the repository.

The source distribution excludes hosting-specific project configuration, Git metadata and credentials. Repository visibility and website access control are separate. The existing private website remains the working deployment; this GitHub package does not automatically update it. See [deployment guidance](docs/DEPLOYMENT.md) for the current private route and alternatives.

No open-source license has been selected. Keep the repository private; select a license and approve publication separately if you decide to release it publicly.

## References

- [SWMManywhere documentation](https://imperialcollegelondon.github.io/SWMManywhere/)
- [SWMManywhere configuration guide](https://imperialcollegelondon.github.io/SWMManywhere/config_guide/)
- [EPA SWMM](https://www.epa.gov/water-research/storm-water-management-model-swmm)

The prototype models an SMRF design proposal. Confirm integration details against your installed SWMManywhere version.
