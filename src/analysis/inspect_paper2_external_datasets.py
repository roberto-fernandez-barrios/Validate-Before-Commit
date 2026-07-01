from __future__ import annotations

from pathlib import Path
import pandas as pd


ROOTS = [
    Path("data/raw"),
    Path("data/processed"),
]


KEYWORDS = [
    "unsw",
    "nb15",
    "nsl",
    "kdd",
]


POSSIBLE_LABEL_COLS = [
    "label",
    "Label",
    " LABEL",
    " Label",
    "attack_cat",
    "Attack_cat",
    "class",
    "Class",
    "target",
    "Target",
]


def is_candidate(path: Path) -> bool:
    lower = str(path).lower()
    return any(k in lower for k in KEYWORDS)


def safe_read_head(path: Path, nrows: int = 1000) -> pd.DataFrame | None:
    try:
        return pd.read_csv(path, nrows=nrows, low_memory=False)
    except Exception as exc:
        print(f"[READ ERROR] {path}: {exc}")
        return None


def inspect_csv(path: Path) -> None:
    print("=" * 120)
    print(path)

    df = safe_read_head(path)
    if df is None:
        return

    print(f"[HEAD] rows={len(df)} cols={len(df.columns)}")
    print("[COLUMNS]")
    print(list(df.columns))

    normalized = {c.strip().lower(): c for c in df.columns}

    found_labels = []
    for c in POSSIBLE_LABEL_COLS:
        key = c.strip().lower()
        if key in normalized:
            found_labels.append(normalized[key])

    print("[POSSIBLE LABEL COLUMNS]", found_labels)

    for col in found_labels:
        try:
            full_col = pd.read_csv(path, usecols=[col], low_memory=False)
            vc = full_col[col].astype(str).str.strip().value_counts(dropna=False)
            print(f"[VALUE COUNTS] {col}")
            print(vc.head(30).to_string())
        except Exception as exc:
            print(f"[VALUE COUNT ERROR] {col}: {exc}")

    numeric_cols = df.select_dtypes(include=["number"]).columns.tolist()
    object_cols = df.select_dtypes(include=["object"]).columns.tolist()

    print(f"[NUMERIC COLS] {len(numeric_cols)}")
    print(numeric_cols[:60])

    print(f"[OBJECT COLS] {len(object_cols)}")
    print(object_cols[:60])


def main() -> None:
    csvs = []

    for root in ROOTS:
        if not root.exists():
            continue
        csvs.extend(root.rglob("*.csv"))

    candidates = [p for p in csvs if is_candidate(p)]

    print(f"[TOTAL CSVS FOUND] {len(csvs)}")
    print(f"[UNSW/NB15-LIKE CANDIDATES] {len(candidates)}")

    if not candidates:
        print()
        print("[NO UNSW/NB15 CANDIDATES FOUND]")
        print("Nearby CSVs under data roots:")
        for p in csvs[:100]:
            print(" -", p)
        return

    for path in candidates:
        inspect_csv(path)


if __name__ == "__main__":
    main()
