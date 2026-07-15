"""Stage CICIDS2017 Tuesday as a CHRONOLOGICAL binary stream (amendment 009, locked pre-run).

Tuesday-WorkingHours is a benign-dominated day whose only attacks are FTP-Patator and
SSH-Patator brute force (~3% of flows). The ML-CVE flows are in capture (chronological)
order. We keep that order, coerce features to numeric, median-fill from the TRAIN split
only (no future leak), and split the timeline 30/70:
  first 30% -> cicids_tue_chrono_train_binary.csv  (incumbent training pool)
  final 70% -> cicids_tue_chrono_stream_binary.csv (the chronological stream)

Because train and stream are the same day and distribution, the incumbent is expected to
stay HEALTHY across the stream -- the healthy-incumbent chronological test the reviewer
asked for, on a second real time-ordered dataset beyond UNSW (amendment 005). Whatever the
incumbent health turns out to be is reported as-is.
"""
from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd

RAW = Path("data/raw/cicids2017/MachineLearningCVE/Tuesday-WorkingHours.pcap_ISCX.csv")
OUT = Path("data/processed/cicids2017")
TRAIN_FRAC = 0.30


def main() -> None:
    df = pd.read_csv(RAW, low_memory=False)
    df.columns = [c.strip() for c in df.columns]
    label_col = [c for c in df.columns if c.lower() == "label"][0]
    print(f"[LOAD] {len(df)} rows, {df.shape[1]} cols; labels={df[label_col].value_counts().to_dict()}")

    y = np.where(df[label_col].astype(str).str.upper().str.strip() == "BENIGN", "BENIGN", "ATTACK")
    X = df.drop(columns=[label_col], errors="ignore")
    X = X.apply(pd.to_numeric, errors="coerce").replace([np.inf, -np.inf], np.nan)

    n_train = int(len(X) * TRAIN_FRAC)
    med = X.iloc[:n_train].median(numeric_only=True)
    X = X.fillna(med).fillna(0.0)
    X["Label"] = y

    train, stream = X.iloc[:n_train], X.iloc[n_train:]
    OUT.mkdir(parents=True, exist_ok=True)
    train.to_csv(OUT / "cicids_tue_chrono_train_binary.csv", index=False)
    stream.to_csv(OUT / "cicids_tue_chrono_stream_binary.csv", index=False)
    for name, part in [("train", train), ("stream", stream)]:
        frac = float((part["Label"] == "ATTACK").mean())
        print(f"[{name.upper()}] rows={len(part)} features={len(part.columns)-1} attack_frac={frac:.4f}")


if __name__ == "__main__":
    main()
