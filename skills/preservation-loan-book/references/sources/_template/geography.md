# Geography: <Metro>, <State> market pack

Define the target area by county FIPS first and jurisdiction polygon second. Never define a mode by ZIP prefix or city string alone; a city-string match is `geo_grade = city_name_weak` and is never the default.

## Modes

| mode | definition | county FIPS | rows in state HFA inventory (before status filter) | notes |
|---|---|---|---|---|
| `city_limits` | inside the City of <Metro> boundary | <FIPS of counties the city touches> | <n by city string; polygon join pending> | string match includes unincorporated postal addresses and excludes suburbs; `city_name_weak` until point-in-polygon is run |
| `county` | <Core County> | <FIPS> | <n> | |
| `metro_core` (default) | <core counties> | <FIPS list> | <n> | match the regional GIS authority's coverage |
| `cbsa` | <CBSA name> | <all CBSA FIPS incl. other-state counties> | <n> | name the sources that stop at the state line |
| `custom` | user-supplied FIPS / ZIP list / polygon | as given | computed | echo the definition |

Default when the user names the metro without qualification: `metro_core`; ask when the asset class is affordable (state HFA data stops at the state line) or when a cross-state suburb is named.

## Jurisdictions

| county | jurisdictions in scope |
|---|---|
| <County A (FIPS)> | <cities>, unincorporated <County A> |
| <County B (FIPS)> | |
| <Other-state county (FIPS)> | note the different preservation-notice law and tenant rules |

## Resolution order (per row)

1. `county_field` (source has county name or FIPS)
2. `zip_crosswalk` (HUD USPS ZIP-County crosswalk, highest RES_RATIO; flag straddling ZIPs: <list>)
3. `point_in_polygon` (source geometry vs county / city polygons)
4. `city_name_weak` (last resort; reported in `rows_by_grade`)

## Boundary sources

| layer | publisher | URL | access | verified_live |
|---|---|---|---|---|
| jurisdiction / city limits polygons | <regional GIS> | <URL> | | false |
| taxlots with owner / mailing | <county assessor GIS> | <URL> | | false |
| ZIP-County crosswalk | HUD PD&R | https://www.huduser.gov/portal/datasets/usps_crosswalk.html | free-registration | false |
| county / place polygons | Census TIGER/Line | https://www.census.gov/geographies/mapping-files/time-series/geo/tiger-line-file.html | free-public | false |

## Sources that stop at a boundary

| source | covers | does not cover |
|---|---|---|
| state HFA inventory | <state> | other-state counties |
| regional GIS | <counties> | |
| county recorder (LURA / ROFR images only) | one county each | |
| state courts portal | <state> courts | other-state courts |
| state SOS | <state> registrations incl. foreign | other-state-only entities |
| HUD, USDA, NHPD, Ginnie, DUS, MSIA, EDGAR | national | — |
| city code / lien / rent rules | <city> only | suburbs |

## Geography object (echoed in every output)

```jsonc
{
  "mode": "metro_core",
  "label": "<label>",
  "county_fips": ["<FIPS>"],
  "jurisdictions": ["<city>"],
  "resolution_order": ["county_field", "zip_crosswalk", "point_in_polygon", "city_name_weak"],
  "rows_by_grade": {"county_field": 0, "zip_crosswalk": 0, "point_in_polygon": 0, "city_name_weak": 0},
  "sources_stopping_at_state_line": ["<source_id>"]
}
```
