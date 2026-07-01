from __future__ import annotations

from pathlib import Path
import pandas as pd


ROOTS = [
    Path("data/raw/ton_iot"),
    Path("data/raw/nf_ton_iot"),
    Path("data/raw/nf_bot_iot"),
    Path("data/raw"),
    Path("data/processed"),
]

KEYWORDS = [
    "ton",
    "ton_iot",
    "ton-iot",
    "network",
    "nf-ton",
    "nfton",
    "nf-bot",
    "nfbot",
    "bot-iot",
    "bot_iot",
]

POSSIBLE_LABEL_COLS = [
    "Label",
    "label",
    "Attack",
    "attack",
    "Attack_cat",
    "attack_cat",
    "Attack Type",
    "attack_type",
    "type",
    "Type",
    "class",
    "Class",
    "category",
    "Category",
]


def is_candidate(path: Path) -> bool:
    s = str(path).lower()
    return any(k in s for k in KEYWORDS)


def read_csv_flexible(path: Path, nrows: int | None = 1000) -> pd.DataFrame:
    return pd.read_csv(path, nrows=nrows, compression="infer", low_memory=False)


def inspect(path: Path) -> None:
    print("=" * 120)
    print(path)

    try:
        df = read_csv_flexible(path, nrows=1000)
    except Exception as exc:
        print("[READ ERROR]", exc)
        return

    print(f"[HEAD] rows={len(df)} cols={len(df.columns)}")
    print("[COLUMNS]")
    print(list(df.columns))

    norm = {str(c).strip().lower(): c for c in df.columns}
    found = []

    for c in POSSIBLE_LABEL_COLS:
        k = c.strip().lower()
        if k in norm and norm[k] not in found:
            found.append(norm[k])

    print("[POSSIBLE LABEL COLUMNS]", found)

    for col in found:
        try:
            full = pd.read_csv(path, usecols=[col], compression="infer", low_memory=False)
            vc = full[col].astype(str).str.strip().value_counts(dropna=False)
            print(f"[VALUE COUNTS] {col}")
            print(vc.head(100).to_string())
        except Exception as exc:
            print(f"[VALUE COUNT ERROR] {col}: {exc}")

    num_cols = df.select_dtypes(include="number").columns.tolist()
    obj_cols = df.select_dtypes(include="object").columns.tolist()

    print(f"[NUMERIC COLS] {len(num_cols)}")
    print(num_cols[:120])

    print(f"[OBJECT COLS] {len(obj_cols)}")
    print(obj_cols[:120])


def main() -> None:
    files = []

    for root in ROOTS:
        if not root.exists():
            continue
        files.extend(root.rglob("*.csv"))
        files.extend(root.rglob("*.csv.gz"))
        files.extend(root.rglob("*.txt"))

    candidates = [p for p in files if is_candidate(p)]

    print("[TOTAL CSV/CSV.GZ/TXT FOUND]", len(files))
    print("[TON/NF CANDIDATES]", len(candidates))

    if not candidates:
        print("[NO CANDIDATES FOUND]")
        print("Nearby files:")
        for p in files[:200]:
            print(" -", p)
        return

    for p in candidates:
        inspect(p)


if __name__ == "__main__":
    main()
