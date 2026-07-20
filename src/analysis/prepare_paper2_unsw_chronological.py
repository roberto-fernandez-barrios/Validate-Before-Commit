"""Stage UNSW-NB15 as a CHRONOLOGICAL binary stream (amendment 005, design locked pre-run).

Concatenates the raw capture files UNSW-NB15_{1..4}.csv (2,540,044 flows; headers from
NUSW-NB15_features.csv), sorts stably by Stime, drops identifiers/nominals/timestamps
(srcip, sport, dstip, dsport, proto, state, service, attack_cat, Stime, Ltime), coerces the
rest to numeric and median-fills using TRAIN-SPLIT medians only (no future statistics leak
into the past-trained pipeline). Label = BENIGN/ATTACK from the binary label column.
Split: first 30% of the sorted timeline -> unsw_chrono_train_binary.csv;
final 70% -> unsw_chrono_stream_binary.csv.
"""
from __future__ import annotations

import argparse
from pathlib import Path

import numpy as np
import pandas as pd

RAW = Path("data/raw/unsw_nb15")
OUT = Path("data/processed/unsw_nb15")
DROP = ["srcip", "sport", "dstip", "dsport", "proto", "state", "service",
        "attack_cat", "Stime", "Ltime"]
TRAIN_FRAC = 0.30


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--train-frac", type=float, default=TRAIN_FRAC,
                    help="final-q1 D4: sensitivity beyond the original 30%% split (0.20, 0.40).")
    args = ap.parse_args()
    train_frac = args.train_frac

    feats = pd.read_csv(RAW / "NUSW-NB15_features.csv", encoding="latin-1")
    names = [str(n).strip() for n in feats["Name"]]
    print(f"[FEATURES] {len(names)} columns")

    parts = []
    for i in (1, 2, 3, 4):
        f = RAW / f"UNSW-NB15_{i}.csv"
        df = pd.read_csv(f, header=None, names=names, low_memory=False)
        print(f"[LOAD] {f.name}: {len(df)} rows")
        parts.append(df)
    df = pd.concat(parts, ignore_index=True)

    df["Stime"] = pd.to_numeric(df["Stime"], errors="coerce")
    df = df.sort_values("Stime", kind="stable").reset_index(drop=True)
    print(f"[SORT] {len(df)} rows, Stime span {df.Stime.min()} .. {df.Stime.max()}")

    label_col = names[-1]  # binary 0/1 label
    y = np.where(pd.to_numeric(df[label_col], errors="coerce").fillna(0).astype(int) == 0,
                 "BENIGN", "ATTACK")

    X = df.drop(columns=DROP + [label_col], errors="ignore")
    X = X.apply(pd.to_numeric, errors="coerce").replace([np.inf, -np.inf], np.nan)

    n_train = int(len(X) * train_frac)
    med = X.iloc[:n_train].median(numeric_only=True)
    X = X.fillna(med).fillna(0.0)
    X["Label"] = y

    train, stream = X.iloc[:n_train], X.iloc[n_train:]
    OUT.mkdir(parents=True, exist_ok=True)
    tf = str(int(round(train_frac * 100)))
    suffix = "" if train_frac == TRAIN_FRAC else tf   # keep the original filenames at 30%
    train.to_csv(OUT / f"unsw_chrono_train{suffix}_binary.csv", index=False)
    stream.to_csv(OUT / f"unsw_chrono_stream{suffix}_binary.csv", index=False)
    for name, part in [("train", train), ("stream", stream)]:
        frac = float((part["Label"] == "ATTACK").mean())
        print(f"[{name.upper()}] rows={len(part)} features={len(part.columns)-1} attack_frac={frac:.4f}")


if __name__ == "__main__":
    main()
