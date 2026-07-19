"""Verify results/tables against the pinned MANIFEST.sha256 (final-kbs P10, step 1).

Exit 1 if any pinned CSV is missing or its hash differs; extra files (not yet pinned) are
listed as warnings only -- `make manifest` re-pins them.
"""
from __future__ import annotations

import hashlib
import sys
from pathlib import Path

ROOT = Path("results/tables")


def main() -> None:
    manifest = ROOT / "MANIFEST.sha256"
    if not manifest.exists():
        sys.exit("MANIFEST.sha256 missing; run `make manifest` first")
    pinned: dict[str, str] = {}
    for line in manifest.read_text(encoding="utf-8").splitlines():
        if line.strip():
            h, p = line.split(None, 1)
            pinned[p.strip()] = h
    bad, missing = [], []
    for p, h in pinned.items():
        f = Path(p)
        if not f.exists():
            missing.append(p)
        elif hashlib.sha256(f.read_bytes()).hexdigest() != h:
            bad.append(p)
    extra = [f.as_posix() for f in ROOT.rglob("*.csv") if f.as_posix() not in pinned]
    for p in extra:
        print(f"  [warn] not pinned: {p}")
    if bad or missing:
        for p in bad:
            print(f"  [FAIL] hash mismatch: {p}")
        for p in missing:
            print(f"  [FAIL] missing: {p}")
        sys.exit(1)
    print(f"verify-hashes: {len(pinned)} pinned CSVs match MANIFEST.sha256 "
          f"({len(extra)} unpinned extras)")


if __name__ == "__main__":
    main()
