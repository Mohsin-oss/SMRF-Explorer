# Input files and surface accounting

## Baseline INP

The browser reads subcatchments; junctions, outfalls, storage and dividers; and conduits, pumps, weirs, orifices and outlets. It retains the original INP text.

`CMS`, `LPS` and `MLD` use SI lengths and hectares. `CFS`, `GPM` and `MGD` use feet and acres, normalized internally to metres and hectares. A missing `FLOW_UNITS` setting is assumed to be CFS and is reported as a warning. Inspect that assumption before continuing.

INP coordinates, vertices and polygons support display. IDs are matched case-insensitively within the INP. The writer changes only the fifth token (%Imperv) in `[SUBCATCHMENTS]` and preserves other text and comments in a separate file.

## GeoJSON

Use FeatureCollections containing Point, LineString, Polygon or MultiPolygon geometry. Set `properties.id` or `properties.name` to the corresponding model object ID. Features with unmatched IDs are ignored for display; duplicate matched IDs are rejected.

Prepare all geometry in one verified coordinate space. Declared conflicting CRS metadata is rejected, but the importer cannot infer or verify an undeclared CRS. GeoJSON replaces the INP display geometry as a set to avoid mixing coordinate spaces. Neither INP polygons nor GeoJSON are used to calculate area in this release.

## Surface CSV

```csv
catchment_id,roof_ha,road_ha,parking_ha,green_correction_ha,baseline_road_width_m
C1,0.5,0.2,0.1,0.04,6
C2,0.8,0.4,0.3,0.1,6
```

These rows are fictional, matching the bundled fixture.

| Column | Meaning |
| --- | --- |
| `catchment_id` | Exact ID from the loaded model. Use the generated template. |
| `roof_ha` | Prepared roof area for the replacement method. |
| `road_ha` | Prepared road area at the baseline width. |
| `parking_ha` | Incremental parking absent from all surfaces already counted. |
| `green_correction_ha` | Known false impervious area to subtract, not all green land. |
| `baseline_road_width_m` | Positive width corresponding to `road_ha`. |

Area columns always use hectares, including for US-unit INP files. Blank fields are unavailable; enter explicit zero where valid. Unknown/duplicate catchment IDs, negative areas and areas exceeding gross catchment area are rejected. Missing data required by a chosen correction block its preview/export.

## Formulas

For catchment gross area `A`, baseline fraction `p` and proposed road width `w`:

```text
baseline impervious area = A × p / 100
road adjustment = road_ha × (w / baseline_road_width_m − 1)
baseline method = baseline impervious area + road adjustment + added parking − green correction
inventory method = roof_ha + road_ha + road adjustment + added parking
manual method = A × manual_percentage / 100
proposed percentage = 100 × proposed impervious area / A
```

Only selected corrections are applied. Width scaling assumes constant road length and no new overlap. Total percentages are area-weighted; proposed areas must stay between zero and the gross area. The verification checkbox records the user's preprocessing assertion, not automated spatial validation.

## Request and result packs

- Request schema: `smrf-processing-request/v1`.
- Result schema: `smrf-processing-result/v1`.
- Requests include baseline INP text, its SHA-256 fingerprint, surface totals, settings, assumptions and the browser preview.
- Results include request identity/settings, baseline fingerprint, verified catchment fractions, refined INP text and fingerprint, pending operations and reported engine status.
- Import checks compare baseline/settings/fractions and reject changes to INP fields beyond %Imperv. Result import is restricted to the supported surface-writing pathway.

Treat exported packs as model data. Fingerprints verify consistency; they are not signatures proving who produced a result.
