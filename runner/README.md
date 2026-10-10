# SMRF local Python runner v0.2

This runner is for the Upload & customize workspace at the private SMRF explorer. It applies verified surface fractions to a separate SWMM INP file and returns a result pack. No GIS package is needed for the current surface-table workflow.

1. Upload a baseline `.inp` in Upload & customize. Optional matching GeoJSON is used for display only.
2. Download the CSV template if you have mapped surface totals. Prepare those values in QGIS, clipped to the model subcatchments, with overlaps resolved.
3. Choose refinements, verify the surface assumptions and export `smrf-processing-request.json`.
4. Extract this ZIP. Open a terminal in the extracted folder and run with Python 3.11 or newer:

```powershell
python smrf_runner.py --request "D:/research/smrf-processing-request.json" --output "D:/research/smrf-output/run_01"
```

Your existing `swmm-env` environment is a suitable starting point. Alternatively, a normal Python installation can run the surface-processing workflow because it uses only the standard library.

5. Import `smrf-result.json` into the same custom workspace. Keep the baseline and refinement choices unchanged while the runner is working.

Outputs: `baseline.inp`, `refined.inp`, `surface-comparison.csv` and `smrf-result.json`. Existing outputs are never overwritten; choose a new run directory for each scenario. The request includes model contents, so store it as you would the original project.

## CSV fields

`catchment_id,roof_ha,road_ha,parking_ha,green_correction_ha,baseline_road_width_m`

All area fields are hectares, even for a US-unit INP. Blank means unavailable; enter zero only when verified. Parking must be a new, nonoverlapping addition absent from the baseline. Green correction is a known false impervious area, not total green space. Width scaling needs the mapped road area and its original assumed width.

Baseline correction method: baseline impervious area + road-width area increment + parking addition - verified green correction.

Inventory replacement method: mapped roof + mapped road + selected parking; green correction is disabled. Manual fractions replace the total directly.

## Optional SWMM simulation

The downloaded runner does not include an engine. If you have an EPA SWMM command-line executable and complete rainfall/input files, explicitly request execution:

```powershell
python smrf_runner.py --request "D:/research/smrf-processing-request.json" --output "D:/research/smrf-output/run_02" --swmm-executable "C:/SWMM/swmm5.exe" --engine-cwd "D:/research/original_project"
```

This invokes the provided executable separately for baseline and refined inputs and writes `.rpt` and `.out` files. Inspect the reports, external-file resolution, rainfall comparability and continuity errors yourself. The result pack reports execution status; the explorer does not infer hydraulic improvement or calculate a flooding comparison. The authoring environment had no SWMM engine, so actual engine execution was not tested here.

## Boundaries

Only %Imperv fields change. Terrain redelineation, polygon union/intersection, raster aggregation, network regeneration, pipe resizing and 2D coupling are not implemented. Selected terrain/network changes are retained as pending operations, never reported as completed. Surface preprocessing belongs in QGIS until its Python GIS adapter is added.

The baseline fingerprint is checked before processing. Returned text and surface fractions are validated before writing. Model files, processing and optional engine execution remain on your computer; there is no remote Python endpoint in this release.
