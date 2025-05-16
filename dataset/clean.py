#!/usr/bin/env python3
"""
Clean games.csv for match-outcome modelling.

• Drops rows where home/away club IDs or goals are null
• Casts club IDs → int64, goals → int16
• Parses the date column to pandas-datetime
• Saves cleaned file to cleaned_data/games_clean.csv
"""

import os
import argparse
import pandas as pd


def clean_games(input_path: str) -> pd.DataFrame:
    df = pd.read_csv(input_path)

    # ------------------------------------------------------------------
    # 1. drop rows missing critical info (21 total in your counts)
    # ------------------------------------------------------------------
    critical = ["home_club_id", "away_club_id",
                "home_club_goals", "away_club_goals"]
    before = len(df)
    df = df.dropna(subset=critical)
    print(f"Dropped {before - len(df):,} rows with missing club IDs or goals")

    # ------------------------------------------------------------------
    # 2. type fixes
    # ------------------------------------------------------------------
    for col in ["home_club_id", "away_club_id"]:
        df[col] = df[col].astype("int64")

    df["home_club_goals"] = df["home_club_goals"].astype("int16")
    df["away_club_goals"] = df["away_club_goals"].astype("int16")

    # ------------------------------------------------------------------
    # 3. parse dates (drop if unparsable)
    # ------------------------------------------------------------------
    df["date"] = pd.to_datetime(df["date"], errors="coerce")
    bad_dates = df["date"].isna().sum()
    if bad_dates:
        df = df.dropna(subset=["date"])
        print(f"Dropped {bad_dates} rows with unparsable dates")

    # ------------------------------------------------------------------
    # 4. optional slim-down (URL is rarely needed)
    # ------------------------------------------------------------------
    df = df.drop(columns=["url"], errors="ignore")
    return df


# for player_valuations.csv
def clean_valuations(input_path: str) -> pd.DataFrame:
    val = pd.read_csv(
        input_path,
        dtype={"player_id": "int64", "current_club_id": "int64"}
    )
    val["date"] = pd.to_datetime(val["date"])
    # keep the most recent valuation per player
    val = (val.sort_values("date")
           .drop_duplicates("player_id", keep="last"))
    return val


# ------------------------------------------------------------------
# NEW helper  ✦  place below clean_valuations()
# ------------------------------------------------------------------
def clean_players(input_path: str, latest_val: pd.DataFrame) -> pd.DataFrame:
    pl = pd.read_csv(input_path,
                     dtype={"player_id": "int64", "current_club_id": "int64"})

    # 1. drop columns we never use
    pl = pl.drop(columns=[
        "agent_name", "image_url", "url",
        "city_of_birth", "contract_expiration_date"
    ], errors="ignore")

    # 2. fill / standardise categoricals
    for col in ("foot", "country_of_birth", "first_name"):
        pl[col] = pl[col].fillna("unknown").str.lower().str.strip()

    # 3. merge latest valuation → fill missing market value
    pl = pl.merge(
        latest_val[["player_id", "market_value_in_eur"]]
        .rename(columns={"market_value_in_eur": "latest_mv"}),
        on="player_id", how="left"
    )
    pl["market_value_in_eur"] = (pl["market_value_in_eur"]
                                 .fillna(pl["latest_mv"])
                                 .fillna(pl["market_value_in_eur"].median()))
    pl = pl.drop(columns="latest_mv")

    # 4. height impute by position median, fallback to global median
    pl["height_in_cm"] = (
        pl.groupby("position")["height_in_cm"]
          .transform(lambda s: s.fillna(s.median()))
          .fillna(pl["height_in_cm"].median())
          .astype("float32")
    )

    # --- keep only the essential columns, in the order you specified ---
    keep_cols = [
        "player_id",
        "market_value_in_eur",
        "highest_market_value_in_eur",
        "last_season",
        "current_club_id",
        "date_of_birth",
        "country_of_citizenship",
        "current_club_domestic_competition_id",
    ]
    pl = pl[keep_cols]        # final trimmed DataFrame
    return pl

    return pl


# ------------------------------------------------------------------
# UPDATED main()  ✦  add players step
# ------------------------------------------------------------------
def main(raw_dir: str, out_dir: str):
    os.makedirs(out_dir, exist_ok=True)

    games_clean = clean_games(os.path.join(raw_dir, "games.csv"))
    games_clean.to_csv(os.path.join(out_dir, "games_clean.csv"), index=False)

    valuations_clean = clean_valuations(
        os.path.join(raw_dir, "player_valuations.csv"))
    valuations_clean.to_csv(os.path.join(
        out_dir, "player_valuations_clean.csv"), index=False)

    # ▼ NEW
    players_clean = clean_players(os.path.join(
        raw_dir, "players.csv"), valuations_clean)
    players_clean.to_csv(os.path.join(
        out_dir, "players_clean.csv"), index=False)

    print("✅ wrote",
          f"{len(games_clean):,} games |",
          f"{len(players_clean):,} players |",
          f"{len(valuations_clean):,} latest valuations")


# ------------------------------------------------------------------
# keep this at bottom (same as before, just points to new main)
# ------------------------------------------------------------------
if __name__ == "__main__":
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--raw_dir", default="../raw_data")
    ap.add_argument("--out_dir", default="../cleaned_data")
    args = ap.parse_args()

    main(args.raw_dir, args.out_dir)
