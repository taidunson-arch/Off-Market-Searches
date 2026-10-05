#!/usr/bin/env python3
"""Minimal test runner (pytest-compatible test modules, no pytest dependency).

Usage: python scripts/tests/run_tests.py [-k substring] [-v]
Discovers test_*.py beside this file, runs every `test_*` function, prints PASS/FAIL/SKIP per test and exits 1 on
any failure. A test may raise `SkipTest` (from unittest) to skip, e.g. when the real OHCS CSV is absent.
"""
from __future__ import annotations

import importlib.util
import os
import sys
sys.dont_write_bytecode = True
import os as _os
_os.environ.setdefault("PYTHONDONTWRITEBYTECODE", "1")
import traceback
from unittest import SkipTest

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))  # scripts/


def main(argv=None) -> int:
    argv = argv if argv is not None else sys.argv[1:]
    k = None
    if "-k" in argv:
        k = argv[argv.index("-k") + 1]
    verbose = "-v" in argv
    passed = failed = skipped = 0
    for fn in sorted(os.listdir(HERE)):
        if not (fn.startswith("test_") and fn.endswith(".py")):
            continue
        spec = importlib.util.spec_from_file_location(fn[:-3], os.path.join(HERE, fn))
        mod = importlib.util.module_from_spec(spec)
        try:
            spec.loader.exec_module(mod)  # type: ignore
        except Exception:
            print(f"FAIL  {fn} (import)"); traceback.print_exc(); failed += 1
            continue
        for name in sorted(dir(mod)):
            if not name.startswith("test_"):
                continue
            if k and k not in name and k not in fn:
                continue
            try:
                getattr(mod, name)()
                passed += 1
                print(f"PASS  {fn}::{name}")
            except SkipTest as exc:
                skipped += 1
                print(f"SKIP  {fn}::{name} ({exc})")
            except Exception:
                failed += 1
                print(f"FAIL  {fn}::{name}")
                traceback.print_exc()
    print(f"\n{passed} passed, {failed} failed, {skipped} skipped")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
