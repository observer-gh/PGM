#!/usr/bin/env python3
"""
merge.py  –  enrich match_features.csv with legacy “avg market value”
            and derive star-player concentration indices.

usage
-----
python merge.py \
    --features_csv  match_features.csv \
    --old_csv       old_dataset.csv \
    --out_csv       match_features_plus.csv
"""

import argparse
import pandas as pd

# ------------------------------------------------------------------


def main(feat_path: str, old_path: str, out_path: str) -> None:
    features = pd.read_csv(feat_path)
    extra_cols = [
        "game_id",
        "home_avg_market_value", "away_avg_market_value",
        "home_total_yellow_cards", "home_total_red_cards",
        "away_total_yellow_cards", "away_total_red_cards",
    ]

    old = pd.read_csv(old_path, usecols=extra_cols)

  # ---------- merge ------------------------------------------------
    df = features.merge(old, on="game_id", how="left")

   # ---------- missing flags & median fill --------------------------
    for side in ("home", "away"):
        col = f"{side}_avg_market_value"
        flag = f"{col}_missing"
        df[flag] = df[col].isna().astype(int)
        df[col] = df[col].fillna(df[col].median())

    # ---------- star-player index -----------------------------------
    for side in ("home", "away"):
        df[f"star_index_{side}"] = (
            df[f"{side}_avg_market_value"] /
            (df[f"squad_value_{side}"] / 11)  # starting 11 memebers
        ).round(3)
        for color in ("yellow", "red"):
            col = f"{side}_total_{color}_cards"
            flag = f"{col}_missing"
            df[flag] = df[col].isna().astype(int)
            df[col] = df[col].fillna(0)

    df["star_index_diff"] = df["star_index_home"] - df["star_index_away"]

    # ---------- put new cols at the end -----------------------------
    new_cols = [
        # avg market value + flags
        "home_avg_market_value", "away_avg_market_value",
        "home_avg_market_value_missing", "away_avg_market_value_missing",
        "star_index_home", "star_index_away", "star_index_diff",
        # raw card totals + flags
        "home_total_yellow_cards", "home_total_red_cards",
        "away_total_yellow_cards", "away_total_red_cards",
        "home_total_yellow_cards_missing", "home_total_red_cards_missing",
        "away_total_yellow_cards_missing", "away_total_red_cards_missing",
    ]
    ordered = [c for c in df.columns if c not in new_cols] + new_cols
    df = df[ordered]

    # ---------- write ------------------------------------------------
    df.to_csv(out_path, index=False)
    print(
        f"✅  wrote {out_path}  |  rows: {len(df):,}  cols: {len(df.columns)}")


# ------------------------------------------------------------------
if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--features_csv",
                    help="output from build_features.py (match_features.csv)", default="match_features.csv")
    ap.add_argument("--old_csv",
                    help="legacy dataset containing avg market values", default="../cleaned_data/final_dataset.csv")
    ap.add_argument("--out_csv", default="match_features_merged.csv")
    args = ap.parse_args()

    main(args.features_csv, args.old_csv, args.out_csv)
