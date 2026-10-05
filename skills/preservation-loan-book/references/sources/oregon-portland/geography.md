# Geography: Portland, Oregon market pack

Every primary dataset in this market is county-scoped (recorder, assessor, courts) or state-scoped (OHCS, SOS), so the target geography is defined by county FIPS first and refined by jurisdiction polygon second. Filtering a statewide file by the string "Portland" is what produced the ambiguity in the first run: it caught unincorporated postal Portland and missed Gresham, Beaverton, Hillsboro and every Clark County WA property.

## Modes

| mode | definition | county FIPS | OHCS rows (2026-10-02 file, before status filter) | notes |
|---|---|---|---|---|
| `city_limits` | inside the City of Portland boundary | 41051 (most), 41067, 41005 (slivers) | 517 by `City == Portland` string (518 after the `Portalnd` typo map in `dataset-schemas.yaml`); polygon join pending | the string count includes unincorporated postal Portland and excludes Gresham (14), Beaverton (14), Tigard (11), Hillsboro (10), Milwaukie (9), Happy Valley (8); until point-in-polygon is implemented every row carries `geo_grade = city_name_weak` and the brief says so |
| `county` | Multnomah County | 41051 | 546 (County title-cased: `MULTNOMAH` 322 + `Multnomah` 224) | includes Portland, Gresham, Troutdale, Fairview, Wood Village, unincorporated |
| `metro_core` (default) | tri-county Oregon metro | 41051, 41067, 41005 | 810 (Multnomah 546, Washington 163, Clackamas 101) | matches Metro RLIS coverage; all Oregon adapters apply |
| `cbsa` | Portland-Vancouver-Hillsboro OR-WA MSA | 41005, 41009, 41051, 41067, 41071, 53011, 53059 | 810 + Columbia and Yamhill OHCS rows; Clark and Skamania WA appear only via HUD, USDA, NHPD and the Clark County Auditor (OHCS and RLIS stop at the state line) | Clark County follows RCW 61.24 / 84.64 and is outside Oregon's rent cap and Portland's relocation/FAIR rules |
| `custom` | user-supplied FIPS list, ZIP list or polygon | as given | computed | echo the definition in the geography object |

Default when the user says "Portland" without qualification: `metro_core`, and ask whether they meant city limits or the bi-state metro if the asset class is affordable (OHCS covers Oregon only) or if they name Vancouver.

## Jurisdictions

| county | jurisdictions in scope |
|---|---|
| Multnomah (41051) | Portland, Gresham, Troutdale, Fairview, Wood Village, Maywood Park, unincorporated Multnomah |
| Washington (41067) | Beaverton, Hillsboro, Tigard, Tualatin, Sherwood, Forest Grove, Cornelius, King City, Durham, unincorporated Washington (Aloha, Bethany, Cedar Mill) |
| Clackamas (41005) | Lake Oswego, Milwaukie, Oregon City, Happy Valley, West Linn, Wilsonville, Gladstone, Damascus area, unincorporated Clackamas |
| Clark WA (53011) | Vancouver, Camas, Washougal, Battle Ground, Ridgefield, unincorporated Clark |
| Columbia (41009), Yamhill (41071), Skamania WA (53059) | CBSA only; mostly USDA 515 and small-town HUD stock |

## Resolution order (per row)

1. `county_field`: a county name or FIPS in the source (OHCS `County` after `.strip().title()`; HUD `county`; assessor). Highest grade.
2. `zip_crosswalk`: HUD USPS ZIP-County crosswalk, pick the county with the highest `RES_RATIO`; flag straddling ZIPs (97086 Happy Valley/Multnomah-Clackamas, 97230 Portland/Gresham edge, 97080, 97236, 97266, 97062, 97140, 97070). Never use ZIP prefixes (970-972 covers the whole state west side; 986 covers SW Washington beyond Clark).
3. `point_in_polygon`: OHCS `Geocode` WKT `POINT (lon lat)` or HUD ArcGIS geometry against county and city polygons (Metro RLIS jurisdiction boundaries; PortlandMaps city limits; Census TIGER for Clark). Required for `city_limits`; not implemented in v2 scripts.
4. `city_name_weak`: city string match. Last resort, never the default, always reported in `rows_by_grade`.

## Boundary sources

| layer | publisher | URL | access | verified_live |
|---|---|---|---|---|
| Jurisdiction / city limits polygons, taxlots | Metro RLIS Discovery (RLIS Live) | https://rlisdiscovery.oregonmetro.gov/ ; https://oregonmetro.gov/rlis-live | free-public (open database license) | false |
| Portland city boundary, zoning, taxlots | PortlandMaps ArcGIS REST | https://www.portlandmaps.com/arcgis/rest/services/ | free-public | false |
| Multnomah taxlots with owner/mailing | SAIL FeatureServer | https://services5.arcgis.com/x7DNZL1YqNQVNykA/ArcGIS/rest/services/Multnomah_County_Taxlot_Parcels/FeatureServer/0 | free-public | false |
| Clark County taxlots / land records | Clark County GIS | https://gis.clark.wa.gov/arcgisfedpw/rest/services/ClarkView_Public/Taxlots/MapServer/0 ; https://gis.clark.wa.gov/arcgisfed2/rest/services/MapCatalog/LandRecords/MapServer/0/query | free-public | false |
| ZIP-County crosswalk | HUD USPS Crosswalk Files | https://www.huduser.gov/portal/datasets/usps_crosswalk.html | free-registration (API token) | false |
| County / place polygons | Census TIGER/Line | https://www.census.gov/geographies/mapping-files/time-series/geo/tiger-line-file.html | free-public | false |

## Sources that stop at a boundary

| source | covers | does not cover |
|---|---|---|
| OHCS OAHI | Oregon statewide | Clark / Skamania WA |
| Metro RLIS (taxlots, affordable inventory) | Multnomah, Washington, Clackamas | Clark WA, Columbia, Yamhill |
| MultcoRecords, MultcoPropTax, SAIL | Multnomah only | all other counties |
| Washington County A&T / Recording | Washington County OR only | |
| Clackamas AscendWeb / Clerk | Clackamas only | |
| Clark County Auditor / Assessor / Digital Archives | Clark WA only | |
| OJD Smart Search | all Oregon circuit courts | Washington state courts (use WA Odyssey portal) |
| Oregon SOS | Oregon registrations incl. foreign | WA-only entities (WA SOS CCFS) |
| HUD, USDA, NHPD, Ginnie, DUS, MSIA, EDGAR | national | — |
| Portland BDS, PHB, Conduits liens, relocation/FAIR rules | City of Portland only | Gresham (own rental inspection program), suburbs, Vancouver |

## Geography object (echoed in every output)

```jsonc
{
  "mode": "metro_core",
  "label": "Portland metro core (Multnomah, Washington, Clackamas)",
  "county_fips": ["41051", "41067", "41005"],
  "jurisdictions": ["Portland", "Gresham", "Troutdale", "Fairview", "Wood Village", "Beaverton", "Hillsboro", "Tigard", "Tualatin", "Sherwood", "Forest Grove", "Cornelius", "Lake Oswego", "Milwaukie", "Oregon City", "Happy Valley", "West Linn", "Wilsonville"],
  "resolution_order": ["county_field", "zip_crosswalk", "point_in_polygon", "city_name_weak"],
  "rows_by_grade": {"county_field": 810, "zip_crosswalk": 0, "point_in_polygon": 0, "city_name_weak": 0},
  "sources_stopping_at_state_line": ["ohcs_oahi", "metro_rlis_affordable", "metro_rlis_taxlots"]
}
```
