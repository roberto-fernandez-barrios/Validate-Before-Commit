"""Stage a CICIDS2017 day as an INTRA-DAY chronological binary stream (final-q1 D4).

Generalizes prepare_paper2_cicids_tuesday_chronological.py (amendment 009, Tuesday-only) to
any day: keeps capture (chronological) order, coerces features to numeric, median-fills from
the TRAIN split only (no future leak), and splits the timeline TRAIN_FRAC/rest:
  first TRAIN_FRAC -> cicids_<day>_chrono_train_binary.csv  (incumbent training pool)
  remainder        -> cicids_<day>_chrono_stream_binary.csv (the chronological stream)

Registered scope (notes/q1_max_protocol.md, D4): Wednesday and Thursday intra-day splits,
train_frac=0.30 (matching the existing Tuesday split for comparability). Thursday's capture
ships as two files (Morning-WebAttacks, Afternoon-Infilteration); concatenated in file order
before splitting, since that IS the day's chronological order.
"""
from __future__ import annotations

import argparse
from pathlib import Path

import numpy as np
import pandas as pd

RAW = Path("data/raw/cicids2017/MachineLearningCVE")
OUT = Path("data/processed/cicids2017")

DAY_FILES = {
    "wednesday": ["Wednesday-workingHours.pcap_ISCX.csv"],
    "thursday": ["Thursday-WorkingHours-Morning-WebAttacks.pcap_ISCX.csv",
                "Thursday-WorkingHours-Afternoon-Infilteration.pcap_ISCX.csv"],
}


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--day", choices=sorted(DAY_FILES), required=True)
    ap.add_argument("--train-frac", type=float, default=0.30)
    args = ap.parse_args()

    parts = []
    for fn in DAY_FILES[args.day]:
        df = pd.read_csv(RAW / fn, low_memory=False)
        df.columns = [c.strip() for c in df.columns]
        print(f"[LOAD] {fn}: {len(df)} rows")
        parts.append(df)
    df = pd.concat(parts, ignore_index=True)
    label_col = [c for c in df.columns if c.lower() == "label"][0]
    print(f"[{args.day.upper()}] {len(df)} rows total; labels={df[label_col].value_counts().to_dict()}")

    y = np.where(df[label_col].astype(str).str.upper().str.strip() == "BENIGN", "BENIGN", "ATTACK")
    X = df.drop(columns=[label_col], errors="ignore")
    X = X.apply(pd.to_numeric, errors="coerce").replace([np.inf, -np.inf], np.nan)

    n_train = int(len(X) * args.train_frac)
    med = X.iloc[:n_train].median(numeric_only=True)
    X = X.fillna(med).fillna(0.0)
    X["Label"] = y

    train, stream = X.iloc[:n_train], X.iloc[n_train:]
    OUT.mkdir(parents=True, exist_ok=True)
    tf = str(int(round(args.train_frac * 100)))
    train.to_csv(OUT / f"cicids_{args.day}_chrono_train{tf}_binary.csv", index=False)
    stream.to_csv(OUT / f"cicids_{args.day}_chrono_stream{tf}_binary.csv", index=False)
    for name, part in [("train", train), ("stream", stream)]:
        frac = float((part["Label"] == "ATTACK").mean())
        print(f"[{name.upper()}] rows={len(part)} features={len(part.columns)-1} attack_frac={frac:.4f}")


if __name__ == "__main__":
    main()
