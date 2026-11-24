# Decision Record 02: Primary Study Boundary

**Status:** APPROVED by the project author on 2026-11-24
**Decision:** The **2025 PMC electoral ward boundary** (41 wards, ID field `qwr`) is the primary study area. The 2017 boundary is kept as an archived comparison only.

Labels: **[Verified]** computed from the repo files; **[Reported]** from the project handover or earlier script output; **[External]** from web sources, not independently checked; **[Open]** unresolved.

---

## 1. Files

| | 2025 boundary | 2017 boundary |
|---|---|---|
| Path | `data/raw/boundaries/PMC Electoral Wards 2025.kml` | `data/raw/boundaries/Pune Electoral Wards Map - 2017.kml` |
| Layer name | `final_41wardboundary` [Verified] | `puneelectoralwards_2017` [Verified] |
| ID field | `qwr` (float, values 1 to 41, no gaps or duplicates) [Verified] | `ward` (integer, values 1 to 41, no gaps or duplicates) [Verified] |
| Ward names | None in the file [Verified] | `name-mr` (Marathi) [Verified] |
| Polygons / CRS | 41, EPSG:4326, valid MultiPolygon [Reported] | 41, EPSG:4326, valid MultiPolygon [Reported] |
| Source | data.opencity.in; resource page [Open] | data.opencity.in, credit Nikhil VJ, Public Domain, updated 2023-03-15 [External] |
| Total area | 479.943 km² [Reported] | 256.600 km² [Reported] |

## 2. Evidence that the files are not interchangeable

- Overall intersection over union is 0.5339; 223.588 km² of the 2025 area lies outside the 2017 area, and only 0.244 km² of the 2017 area lies outside the 2025 area [Reported].
- **Ward numbers do not correspond.** Comparing ward N in 2025 with ward N in 2017 (UTM 43N areas), only wards 5 (0.93), 11 (0.95) and 32 (0.83) overlap strongly; most others score 0.00 [Verified, 2026-11-24].
- Example: ward 25 is 2.11 km² in the 2025 file and 5.97 km² in the 2017 file [Verified].
- The 2025 file has several large outer wards (ward 33 is 58.49 km²; wards 3, 9, 15, 38 and 41 are roughly 30 to 40 km²) [Verified].

## 3. Reasons for choosing 2025

1. It is the current, larger PMC extent. Reports describe a final ward structure announced in October 2025 [External].
2. The OSM roads and healthcare facilities were already extracted with this boundary, so no re-extraction is needed [Reported].
3. Its ID field name `qwr` matches the ward identifier in the original project's ward layer (`PMC_Wards_Population`). This suggests, but does not prove, that the original study used the same or a related file [Recovered clue, not proof].
4. Because 2017 lies almost entirely inside 2025 (0.244 km² outside), nothing is lost for the old core area.

## 4. Rules that follow from this decision

- Never join, merge or compare the two files by ward number.
- Any 2017 versus 2025 comparison must use area-weighted overlay, and is out of scope unless requested.
- Both original KML files stay unmodified in `data/raw/boundaries/`.
- Original-study results (for example "Ward 25, index 11.23") cannot be matched to a ward in either file until the original ward map or names are recovered. They stay labelled as unmatched history.
- Large wards (for example ward 33) mean a single centroid can misrepresent where residents live. Population-weighted origins from the WorldPop raster will be tested after the ward-centroid baseline.
- All reports must state: "Study area: PMC 2025 electoral ward boundary (41 wards), data.opencity.in."

## 5. Consequences and open items

| Item | Status |
|---|---|
| Ward names for the 2025 `qwr` numbers | [Open] Find an official list of the 41 prabhags and match names to polygons by location, not by number alone |
| OpenCity page, licence and date for the 2025 file | [Open] Needed for the data inventory and README |
| Boundary dates versus data dates | [Open] OSM data was extracted 2026-11-23; population raster is 2025; document the mismatch as a limitation |
| Edge effect of extracting roads and facilities with the polygon | [Open] Test whether small disconnected road components lie along the boundary; ask approval before any buffered re-extraction |
| Wards near the boundary | Residents may use facilities just outside; consider a supply buffer in the accessibility model |
