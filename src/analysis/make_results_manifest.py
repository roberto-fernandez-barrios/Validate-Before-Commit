"""Write results/tables/MANIFEST.sha256: SHA-256 of every CSV under results/tables.

Reviewers regenerating the pipeline (see Makefile / REPRODUCE.md) can diff their outputs
against the committed confirmatory CSVs and this manifest.
"""
from __future__ import annotations

import hashlib
from pathlib import Path

ROOT = Path("results/tables")


def main() -> None:
    lines = []
    for f in sorted(ROOT.rglob("*.csv")):
        h = hashlib.sha256(f.read_bytes()).hexdigest()
        lines.append(f"{h}  {f.as_posix()}")
    out = ROOT / "MANIFEST.sha256"
    out.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"wrote {out} ({len(lines)} files)")


if __name__ == "__main__":
    main()
