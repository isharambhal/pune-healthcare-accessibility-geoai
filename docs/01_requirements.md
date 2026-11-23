# Milestone 1: Project Reconstruction and Requirements

**Project:** GeoAI Spatial Accessibility and Decision-Support Framework: Healthcare Services in Pune Municipal Corporation (PMC)
**Status:** DRAFT for approval. No analysis code has been written.
**Evidence base:** the original defence presentation and the reconstruction brief. The dissertation, original data, ArcGIS Pro project and `app1.py` are NOT available.

Labels used throughout:
- **[Recovered]** stated in the original presentation or brief
- **[Assumed]** a working assumption that must be confirmed
- **[Proposed]** a new design choice that needs approval
- **[Verify]** must be checked against real data before use

---

## 1. Decisions already made

| Decision | Choice |
|---|---|
| Study area | PMC only, 41 wards (continuity with the original study) |
| Facility focus (first version) | Clinics and primary care first; hospitals as a second layer [Assumed: not yet confirmed] |
| ML component | Allowed and wanted |
| Scope | Restore the original study, then add extensions |
| Hosting | Public GitHub repo, live Streamlit Community Cloud app |
| Development environment | GitHub Codespaces, Python 3.11 (laptop blocks compiled libraries) |

## 2. Recovered vs. available vs. missing

| Item | Recovered historical information | Currently available | Still missing |
|---|---|---|---|
| Ward boundaries | 41 PMC wards; CRS WGS 1984 UTM 43N [Recovered] | Nothing | Boundary file, source, date; confirm it has 41 wards [Verify] |
| Facilities | About 880 mapped from OpenStreetMap [Recovered] | Nothing | Facility file, OSM tags used, extraction date, type breakdown |
| Road network | OSM roads in ArcGIS Network Analyst [Recovered] | Nothing | Network dataset; rebuild from OSM |
| Population | WorldPop-derived ward population; layer `PMC_Wards_Population` [Recovered] | Nothing | WorldPop year and resolution; ward totals |
| Network analysis | Closest Facility; facilities as Facilities, ward centroids as Incidents [Recovered] | Nothing | Impedance (distance or time); the reason only 12 routes succeeded |
| Accessibility Index | Relative ward index; higher = more accessible; average 4.06; best ward Ward 25 at 11.23 [Recovered] | Nothing | **Formula, weights, normalisation** |
| Hotspots | Gi* on the index; 9 significant wards in central Pune at 95-99% confidence; peripheral wards Not Significant [Recovered] | Nothing | Spatial weights definition |
| Planning priority | 0-100 score, High/Medium/Low, from index, facility count, population, hotspot status [Recovered] | Nothing | Weights and thresholds |
| Dashboard and assistant | Streamlit, KPI cards, ward explorer, rule-based assistant [Recovered] | Nothing | Source code |
| Tooling | Python 3.11 venv in Codespaces; GeoPandas smoke test passes [available] | Repo skeleton, `CLAUDE.md`, test | n/a |

## 3. Known inconsistencies to resolve

1. **Route coverage.** The presentation says routes were produced "for every ward"; the brief says only 12 routes succeeded. **[Verify]** against the dissertation before any claim is made about network coverage.
2. **Result labels.** The numbers 9, 4.06, 41 and 880 lost their labels when the slide was extracted. The pairing used here (9 hotspot wards, 4.06 average index) is the most likely reading. **[Verify]** against the slide image.
3. **Ward count.** The ward boundary file actually obtained must be checked; official ward counts and boundaries can change. **[Verify]**

## 4. Questions that block later milestones

1. Clinics and primary care first, or hospitals first? (Default used: clinics and primary care.)
2. Can the dissertation methodology pages (index formula, planning score) be found?
3. Does the first network analysis use distance or travel time as impedance? (Proposed: both, reported separately.)
4. Is public hosting of derived ward-level results acceptable to the supervisor or institute?

## 5. Scope

### Phase A: Faithful restoration
- Ward boundaries, facilities, population, ward-level counts
- Accessibility Index and rank (formula recovered if possible; otherwise a documented replacement, **approved before use**) [Proposed]
- Getis-Ord Gi* with documented weights and significance levels
- Planning priority score (documented, explainable)
- Streamlit dashboard and rule-based assistant

### Phase B: Extensions [Proposed]
1. OSMnx network travel times to the nearest facility for all 41 wards, with failed routes logged
2. Two-Step Floating Catchment Area (2SFCA)
3. Population-weighted access and equity metrics (population within 10/15/30 minutes; Gini or Lorenz curve)
4. Moran's I and LISA alongside Gi*
5. Flood or disruption stress test (which wards lose access first)
6. Method comparison and sensitivity analysis of index weights
7. Explainable ML with spatial cross-validation and SHAP (drivers of accessibility, not clinical outcomes)
8. "What if" scenario tool for adding a facility (later phase)

## 6. Methodological rules

- No result is reported unless it was computed from real data in this repo.
- Facility count is not healthcare capacity.
- Network-based and straight-line accessibility stay separate.
- Rebuilt values will be compared with the original deck's pattern as a **sanity check only**. They must not be tuned to reproduce the original numbers.
- Any replacement formula is labelled "reconstruction" and needs approval.

## 7. Architecture

```
Offline pipeline (laptop/Codespaces)         Live app (Streamlit Cloud)
raw data -> clean -> analyse -> results  -->  loads small result files
                                              maps, tables, assistant, scenarios
```

Heavy analysis (routing, Gi*, ML) runs offline and writes small result files. The live app only reads them.

## 8. Technology

| Tool | Purpose | Essential? |
|---|---|---|
| GeoPandas, Shapely, PyProj, pyogrio | Spatial data handling | Essential |
| Streamlit | Dashboard | Essential |
| Folium or Plotly | Maps and charts | Essential (one of them) |
| PySAL / esda / libpysal | Gi*, Moran, LISA | Essential for Phase A |
| OSMnx / NetworkX | Network routing | Phase B |
| scikit-learn, SHAP | ML and explanations | Phase B |
| GeoPackage or CSV | Storage | Essential |
| PostGIS | Database | Optional, not planned |
| pytest, Git, GitHub | Testing and version control | Essential |

## 9. Candidate data sources (to evaluate, not yet confirmed)

For each: record source, date, CRS, licence and attribution before use. **[Verify]** every item.

- PMC or OpenCity ward boundaries
- OpenStreetMap facilities (ODbL; attribution "© OpenStreetMap contributors")
- OpenStreetMap road network
- WorldPop population (check year, resolution and terms)

## 10. Milestones

| # | Milestone | Approval gate |
|---|---|---|
| 1 | Reconstruction and requirements (this document) | You approve scope and open questions |
| 2 | Data foundation: acquire, validate, standardise | Data sources and ward count confirmed |
| 3 | Baseline analysis: counts, index, Gi*, planning score | Index method approved |
| 4 | Phase B analysis: routing, 2SFCA, equity, LISA, stress test | Results reviewed |
| 5 | ML and sensitivity analysis | Results reviewed |
| 6 | Rule-based assistant | Tested on supported and unsupported questions |
| 7 | Streamlit app (local), then deployment | App runs from precomputed files |
| 8 | Tests, README, screenshots, CV and interview material | Everything claimed has been run |

## 11. Risks

| Risk | Mitigation |
|---|---|
| Original index formula unrecoverable | Documented replacement, approved before use, labelled as reconstruction |
| OSM data differs from 2025 data | Record extraction date; compare counts; do not expect 880 |
| Routing fails for some wards | Log failures; report valid-route count; investigate causes |
| Streamlit Cloud memory limits | Precompute offline; keep app dependencies small |
| Laptop blocks compiled libraries | Develop in Codespaces |
| Personal data in the repo | `docs/historical/` stays git-ignored |

## 12. Approval checklist

- [ ] Scope in section 5 approved
- [ ] Clinics and primary care chosen as first destination
- [ ] Section 3 inconsistencies acknowledged
- [ ] Ready to start Milestone 2 (data acquisition)