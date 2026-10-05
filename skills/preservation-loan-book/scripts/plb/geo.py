"""Geography resolution for preservation-loan-book.

Geography is defined by county FIPS sets, never by ZIP prefix and never by a bare city string
unless the caller explicitly asks for `city_limits`, which is graded `city_name_weak` until a
point-in-polygon join is implemented. Resolution order: county field -> ZIP crosswalk ->
point-in-polygon -> city name.

Portland pack definitions (references/sources/oregon-portland/geography.md):
  county     41051
  metro_core 41051, 41067, 41005
  cbsa       41005, 41009, 41051, 41067, 41071, 53011, 53059
"""
from __future__ import annotations

import hashlib
import re
from typing import Dict, Iterable, List, Optional, Tuple

STATE_BY_FIPS_PREFIX = {"41": "OR", "53": "WA"}

COUNTY_FIPS_OR_WA: Dict[str, str] = {
    "Multnomah": "41051", "Washington": "41067", "Clackamas": "41005", "Columbia": "41009", "Yamhill": "41071",
    "Clark": "53011", "Skamania": "53059", "Marion": "41047", "Lane": "41039", "Deschutes": "41017",
    "Jackson": "41029", "Linn": "41043", "Benton": "41003", "Polk": "41053", "Douglas": "41019", "Josephine": "41033",
    "Klamath": "41035", "Umatilla": "41059", "Coos": "41011", "Lincoln": "41041", "Tillamook": "41057",
    "Clatsop": "41007", "Hood River": "41027", "Wasco": "41065", "Union": "41061", "Baker": "41001",
    "Malheur": "41045", "Crook": "41013", "Jefferson": "41031", "Curry": "41015", "Morrow": "41049",
    "Harney": "41025", "Lake": "41037", "Grant": "41023", "Wallowa": "41063", "Sherman": "41055",
    "Gilliam": "41021", "Wheeler": "41069",
}
COUNTY_NAME_BY_FIPS = {v: k for k, v in COUNTY_FIPS_OR_WA.items()}

PORTLAND_MODES: Dict[str, Dict[str, object]] = {
    "city_limits": {"fips": ["41051", "41067", "41005"], "city": "Portland", "grade": "city_name_weak"},
    "county": {"fips": ["41051"], "grade": "county_field"},
    "metro_core": {"fips": ["41051", "41067", "41005"], "grade": "county_field"},
    "cbsa": {"fips": ["41005", "41009", "41051", "41067", "41071", "53011", "53059"], "grade": "county_field"},
}

METRO_JURISDICTIONS = [
    "Portland", "Gresham", "Troutdale", "Fairview", "Wood Village", "Beaverton", "Hillsboro", "Tigard", "Tualatin",
    "Sherwood", "Forest Grove", "Cornelius", "Lake Oswego", "Milwaukie", "Oregon City", "Happy Valley", "West Linn",
    "Wilsonville", "Vancouver", "Camas",
]

_ABBREV = {
    "STREET": "ST", "AVENUE": "AVE", "BOULEVARD": "BLVD", "ROAD": "RD", "DRIVE": "DR", "COURT": "CT", "PLACE": "PL",
    "LANE": "LN", "TERRACE": "TER", "PARKWAY": "PKWY", "HIGHWAY": "HWY", "CIRCLE": "CIR", "NORTH": "N", "SOUTH": "S",
    "EAST": "E", "WEST": "W", "NORTHEAST": "NE", "NORTHWEST": "NW", "SOUTHEAST": "SE", "SOUTHWEST": "SW",
    "APARTMENT": "APT", "SUITE": "STE", "UNIT": "UNIT", "AND": "&",
}


def normalize_address(addr: Optional[str]) -> str:
    """USPS-style light normalization: uppercase, strip punctuation, standard suffix abbreviations."""
    if not addr:
        return ""
    s = re.sub(r"[.,#]", " ", str(addr).upper())
    s = re.sub(r"\s+", " ", s).strip()
    toks = [_ABBREV.get(t, t) for t in s.split(" ")]
    return " ".join(toks)


def zip5(z: Optional[str]) -> str:
    if z is None:
        return ""
    m = re.match(r"\s*(\d{5})", str(z))
    return m.group(1) if m else ""


def property_id(state: Optional[str], county_fips: Optional[str], parcel_id: Optional[str],
                address: Optional[str], zip_code: Optional[str]) -> str:
    """`{state}-{county_fips}-{parcel_id}` when a parcel is known, else `addr:` + 12 hex of sha1."""
    if parcel_id and county_fips and state:
        return f"{state}-{county_fips}-{str(parcel_id).strip()}"
    key = normalize_address(address) + "|" + zip5(zip_code)
    return "addr:" + hashlib.sha1(key.encode("utf-8")).hexdigest()[:12]


def county_fips_from_name(name: Optional[str], county_map: Optional[Dict[str, str]] = None) -> Optional[str]:
    if not name:
        return None
    n = str(name).strip().title()
    if county_map and n in county_map:
        return str(county_map[n])
    return COUNTY_FIPS_OR_WA.get(n)


def modes_for_fips(fips: Optional[str], city: Optional[str], modes: Dict[str, Dict[str, object]] = PORTLAND_MODES) -> List[str]:
    """All geography modes a property satisfies, pipe-joined later (e.g. county|metro_core|cbsa)."""
    out = []
    for mode, spec in modes.items():
        if fips and fips in spec["fips"]:
            if "city" in spec:
                if city and str(city).strip().title() == spec["city"]:
                    out.append(mode)
            else:
                out.append(mode)
    return out


def in_mode(fips: Optional[str], city: Optional[str], mode: str, counties_override: Optional[Iterable[str]] = None,
            modes: Dict[str, Dict[str, object]] = PORTLAND_MODES) -> Tuple[bool, str]:
    """Membership test for one mode; returns (in_geography, geo_grade)."""
    if counties_override:
        allowed = set(str(c) for c in counties_override)
        return (fips in allowed, "county_field")
    spec = modes.get(mode)
    if spec is None:
        raise ValueError(f"unknown geography_mode {mode}; expected one of {sorted(modes)}")
    if "city" in spec:
        ok = bool(city) and str(city).strip().title() == spec["city"]
        return ok, "city_name_weak"
    return (fips in spec["fips"]), "county_field"


def parse_wkt_point(wkt: Optional[str]) -> Tuple[Optional[float], Optional[float]]:
    """`POINT (lon lat)` -> (lat, lon)."""
    if not wkt:
        return None, None
    m = re.match(r"\s*POINT\s*\(\s*(-?\d+(?:\.\d+)?)\s+(-?\d+(?:\.\d+)?)\s*\)", str(wkt))
    if not m:
        return None, None
    return float(m.group(2)), float(m.group(1))


def load_zip_crosswalk(path: str):
    """Load a HUD USPS ZIP-County crosswalk CSV (columns ZIP, COUNTY, RES_RATIO; case-insensitive).

    Returns dict zip5 -> (county_fips, res_ratio, straddles) where the county with the highest
    RES_RATIO wins and `straddles` is True when any other county has RES_RATIO >= 0.10.
    """
    import pandas as pd
    df = pd.read_csv(path, dtype=str)
    cols = {c.lower(): c for c in df.columns}
    zc, cc = cols.get("zip"), cols.get("county")
    rr = cols.get("res_ratio")
    if not (zc and cc):
        raise ValueError("crosswalk needs ZIP and COUNTY columns")
    out: Dict[str, Tuple[str, float, bool]] = {}
    for z, grp in df.groupby(zc):
        z5 = zip5(z)
        ratios = []
        for _, r in grp.iterrows():
            try:
                ratio = float(r[rr]) if rr else 1.0
            except (TypeError, ValueError):
                ratio = 0.0
            ratios.append((ratio, str(r[cc]).zfill(5)))
        ratios.sort(reverse=True)
        best = ratios[0]
        straddles = any(x[0] >= 0.10 for x in ratios[1:])
        out[z5] = (best[1], best[0], straddles)
    return out
