#!/usr/bin/env python3
"""Reachability + header smoke test for the URLs in a jurisdiction pack's sources.md.

Default is a DRY RUN with no network calls: it parses every markdown table in sources.md (and federal/README.md
when present), lists each source_id / URL / access tier / current verified_live value and writes
sources_status.json with verified_live=false for everything. Pass `--live` to issue HEAD/GET requests
(stdlib urllib, honoring HTTPS_PROXY) and flip verified_live to true only when the request returns 2xx/3xx and,
when a local sample file is supplied via `--samples <dir>`, the sample's header contains the expected key
fields listed in the table's `key fields` column. The .md files are never edited automatically; copy the
status back by hand after reviewing.

Usage:
  python scripts/smoke_test_sources.py --pack references/sources/oregon-portland [--live] [--timeout 10] [--samples omdf/inbox]
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys
import time
from typing import Any, Dict, List

URL_RE = re.compile(r"https?://[^\s|)>\]]+")


def parse_tables(md: str) -> List[Dict[str, str]]:
    """Return a row dict per markdown-table row (header normalized to lowercase)."""
    rows: List[Dict[str, str]] = []
    lines = md.splitlines()
    i = 0
    while i < len(lines):
        line = lines[i]
        if line.strip().startswith("|") and i + 1 < len(lines) and re.match(r"^\s*\|?\s*:?-{2,}", lines[i + 1]):
            header = [h.strip().lower() for h in line.strip().strip("|").split("|")]
            i += 2
            while i < len(lines) and lines[i].strip().startswith("|"):
                cells = [c.strip() for c in lines[i].strip().strip("|").split("|")]
                if len(cells) == len(header):
                    rows.append(dict(zip(header, cells)))
                i += 1
        else:
            i += 1
    return rows


def collect_sources(pack: str) -> List[Dict[str, Any]]:
    out = []
    candidates = [os.path.join(pack, "sources.md"), os.path.join(pack, "..", "federal", "README.md")]
    for path in candidates:
        if not os.path.exists(path):
            continue
        with open(path, "r", encoding="utf-8") as fh:
            md = fh.read()
        for row in parse_tables(md):
            url_cell = row.get("url") or ""
            m = URL_RE.search(url_cell) or URL_RE.search(" ".join(row.values()))
            if not m:
                continue
            url = m.group(0).rstrip(".,;")
            out.append({"source_id": row.get("source_id") or row.get("source") or row.get("name") or url, "url": url,
                        "access": row.get("access", ""), "adapter": row.get("adapter", ""), "key_fields": row.get("key fields", ""),
                        "verified_live_declared": row.get("verified_live", ""), "file": os.path.relpath(path, pack)})
    return out


def probe(url: str, timeout: float) -> Dict[str, Any]:
    import urllib.error
    import urllib.request
    res: Dict[str, Any] = {"url": url, "status": None, "ok": False, "error": None, "elapsed_s": None}
    t0 = time.time()
    for method in ("HEAD", "GET"):
        try:
            req = urllib.request.Request(url, method=method, headers={"User-Agent": "off-market-deal-finder-v2 smoke test"})
            with urllib.request.urlopen(req, timeout=timeout) as resp:
                res.update({"status": resp.status, "ok": 200 <= resp.status < 400, "content_type": resp.headers.get("Content-Type", "")})
                break
        except urllib.error.HTTPError as exc:
            res.update({"status": exc.code, "ok": False, "error": f"HTTP {exc.code}"})
            if method == "HEAD" and exc.code in (405, 403, 501):
                continue
            break
        except Exception as exc:  # proxy refusals, timeouts, DNS
            res.update({"error": f"{type(exc).__name__}: {exc}"})
            break
    res["elapsed_s"] = round(time.time() - t0, 2)
    return res


def check_sample(sample_dir: str, source_id: str, key_fields: str) -> Dict[str, Any]:
    """Look for a file whose name contains the source_id tokens and verify key fields appear in its header."""
    if not sample_dir or not os.path.isdir(sample_dir) or not key_fields:
        return {"sample_checked": False}
    toks = [t for t in re.split(r"[^a-z0-9]+", source_id.lower()) if len(t) > 2]
    for fn in os.listdir(sample_dir):
        if all(t in fn.lower() for t in toks[:2]):
            path = os.path.join(sample_dir, fn)
            try:
                import pandas as pd
                df = pd.read_excel(path, nrows=5) if fn.lower().endswith(("xlsx", "xls")) else pd.read_csv(path, nrows=5, dtype=str, encoding="utf-8-sig")
                header = [str(c).strip().lower() for c in df.columns]
                wanted = [k.strip().lower() for k in re.split(r"[;,]", key_fields) if k.strip()]
                missing = [k for k in wanted if not any(k in h for h in header)]
                return {"sample_checked": True, "sample_file": fn, "missing_fields": missing, "header_ok": not missing}
            except Exception as exc:
                return {"sample_checked": True, "sample_file": fn, "error": str(exc), "header_ok": False}
    return {"sample_checked": False}


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--pack", required=True)
    ap.add_argument("--live", action="store_true", help="actually issue HTTP requests (default: dry run, no network)")
    ap.add_argument("--timeout", type=float, default=10)
    ap.add_argument("--samples", default=None, help="directory with downloaded sample files for header checks")
    ap.add_argument("--out", default=None, help="default <pack>/sources_status.json")
    a = ap.parse_args(argv)
    sources = collect_sources(a.pack)
    if not sources:
        print(f"no markdown tables with URLs found under {a.pack} (expected sources.md); nothing to test")
    results = []
    for s in sources:
        r = dict(s)
        if a.live:
            r.update(probe(s["url"], a.timeout))
            r.update(check_sample(a.samples, s["source_id"], s["key_fields"]))
            r["verified_live"] = bool(r.get("ok")) and (r.get("header_ok", True) if r.get("sample_checked") else True)
        else:
            r.update({"status": None, "ok": None, "verified_live": False, "note": "dry run; pass --live to probe"})
        results.append(r)
    out = a.out or os.path.join(a.pack, "sources_status.json")
    with open(out, "w", encoding="utf-8") as fh:
        json.dump({"mode": "live" if a.live else "dry_run", "pack": a.pack, "results": results}, fh, indent=2)
    print(f"{'source_id':<40}{'access':<20}{'status':<8}{'verified_live':<14}url")
    for r in results:
        print(f"{str(r['source_id'])[:39]:<40}{str(r['access'])[:19]:<20}{str(r.get('status') or '-'):<8}{str(r['verified_live']):<14}{r['url'][:70]}")
    print(f"wrote {out} ({len(results)} sources; {'live' if a.live else 'dry run - no network calls made'})")


if __name__ == "__main__":
    main()
