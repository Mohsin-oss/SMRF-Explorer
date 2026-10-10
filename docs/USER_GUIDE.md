# Using the SMRF explorer

## Start with the demo

Choose **Demo explorer** to inspect the fictional 18 ha district. Its six subcatchments, eight nodes and seven pipes are schematic. The map is not an area-measuring GIS view, and none of the objects represent Bellinge.

Select a catchment, node or pipe to inspect it. Change the impervious-area method, street width, parking or green correction and inspect the area totals and requested workflow stages. Save a scenario in the browser or export a demo plan. Demo plans do not apply to uploaded projects.

## Load your model

The opening screen is **Upload & customize**. Controls are visible but disabled before upload.

1. Click **Choose files** or drop a baseline `.inp` into the upload panel.
2. Optionally include matching GeoJSON and one prepared surface CSV. You may add these later to the loaded model.
3. Review the imported units, map, object inspector and diagnostics. Geometry without verified CRS is a coordinate display, not evidence of coverage or correct positioning.
4. Choose the surface method and corrections. In **Manual by subcatchment**, select each catchment in the inspector to set its percentage. Catchments without a manual override retain their baseline fraction.

The importer accepts at most eight files, 20 MiB per file and 50 MiB per batch. Failed imports preserve the previously loaded model. Reloading or closing the page loses custom session data; export a processing request to retain a checkpoint.

## Prepare mapped surface values

Use QGIS or an equivalent GIS workflow to validate geometry, use a suitable projected CRS, clip surfaces to subcatchments and resolve overlaps. Download the surface CSV template after loading the INP. Every row must match a catchment ID; explicit zero means none, while a blank means unavailable.

- **Baseline + mapped corrections:** keep the original impervious area, adjust roads, add omitted parking and subtract a verified green classification error.
- **Replace with mapped roofs + roads:** replace the original area with the roof and road inventory, plus chosen road-width/parking adjustments. Green subtraction is disabled for this method.
- **Manual by subcatchment:** replace selected percentages directly; additive surface corrections are disabled.

Confirm coverage, clipping and overlaps before using mapped corrections. The runner validates numbers and bounds; it does not verify your GIS preprocessing.

## Apply refinements locally

1. Click **Export Python processing request**. The JSON contains the baseline model and proposed settings.
2. Download and extract the Python runner, or use `runner/smrf_runner.py` from this repository.
3. Run from the repository root:

```powershell
python runner/smrf_runner.py --request "D:/research/smrf-processing-request.json" --output "D:/research/smrf-output/run_01"
```

4. Import `smrf-result.json` into the matching loaded baseline with the same choices. Download the returned `refined.inp` after the fingerprint and fraction checks pass.

The output directory contains `baseline.inp`, `refined.inp`, `surface-comparison.csv` and `smrf-result.json`. Select a new directory for each run; the runner refuses to overwrite its output files.

## Optional hydraulic execution

An external EPA SWMM command-line executable and complete model inputs are required. See [the runner guide](../runner/README.md) for `--swmm-executable` and `--engine-cwd`. The bundled fixture lacks a complete rainfall configuration and is intended for structural/accounting checks only.

Inspect reports, continuity errors, runoff, flows and flooding before judging hydraulic performance. The site displays the runner's execution status and validates the returned surface model; it does not compute a hydraulic comparison or establish calibration accuracy.

DTM redelineation, street-graph regeneration, raster processing and polygon union/intersection remain future adapters. Their toggles record requests while retaining existing geometry.
