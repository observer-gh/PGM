#!/usr/bin/env python3
"""
Build pre-kickoff features from the three cleaned tables.
This first slice adds: rest_days_home / rest_days_away / rest_days_diff.
"""

import os
import argparse
import pandas as pd

# ------------------------------------------------------------
# helpers
# ------------------------------------------------------------


def load_cleaned(root: str):
    games = pd.read_csv(os.path.join(root, "games_clean.csv"),
                        parse_dates=["date"],
                        dtype={"home_club_id": "int64", "away_club_id": "int64"})
    players = pd.read_csv(os.path.join(root, "players_clean.csv"),
                          dtype={"player_id": "int64", "current_club_id": "int64"})
    vals = pd.read_csv(os.path.join(root, "player_valuations_clean.csv"),
                       parse_dates=["date"],
                       dtype={"player_id": "int64", "current_club_id": "int64"})
    return games, players, vals

# ------------------------------------------------------------
# feature block ➊  –  rest-days
# ------------------------------------------------------------


def add_rest_days(g: pd.DataFrame) -> pd.DataFrame:
    for side in ("home", "away"):
        cid = f"{side}_club_id"
        g = g.sort_values([cid, "date"])
        prev = g.groupby(cid)["date"].shift()

        raw_gap = (g["date"] - prev).dt.days               # un-capped
        g[f"long_break_flag_{side}"] = (raw_gap > 60).astype(int)

        rd = raw_gap.fillna(7).clip(upper=60)              # capped 0-60
        g[f"rest_days_{side}"] = rd

    g["rest_days_diff"] = g["rest_days_home"] - g["rest_days_away"]
    g["long_break_flag_diff"] = g["long_break_flag_home"] - \
        g["long_break_flag_away"]
    return g


# season_ppg_*, goal_diff_pg_*, win_rate_last5_*
def add_season_form(g: pd.DataFrame) -> pd.DataFrame:
    # build long club–match table
    home = g[["game_id", "date", "home_club_id",
              "home_club_goals", "away_club_goals"]].copy()
    home.columns = ["game_id", "date", "club_id", "gf", "ga"]

    away = g[["game_id", "date", "away_club_id",
              "away_club_goals", "home_club_goals"]].copy()
    away.columns = ["game_id", "date", "club_id", "gf", "ga"]

    long = pd.concat([home, away], ignore_index=True)
    long["pts"] = (long.gf > long.ga) * 3 + (long.gf == long.ga)
    long.sort_values(["club_id", "date"], inplace=True)

    # cumulative *before* current match
    long["gp"] = long.groupby("club_id").cumcount()
    long["cum_pts"] = long.groupby("club_id")["pts"].cumsum() - long["pts"]
    long["cum_gf"] = long.groupby("club_id")["gf"].cumsum() - long["gf"]
    long["cum_ga"] = long.groupby("club_id")["ga"].cumsum() - long["ga"]

    long["season_ppg"] = long["cum_pts"] / long["gp"].replace(0, pd.NA)
    long["goal_diff_pg"] = (long["cum_gf"] - long["cum_ga"]
                            ) / long["gp"].replace(0, pd.NA)

    long["is_win"] = (long["pts"] == 3).astype(int)
    long["win_rate_last5"] = (
        long.groupby("club_id")["is_win"]
            .transform(lambda s: s.shift().rolling(5, min_periods=1).mean())
    )

    return long[["game_id", "club_id",
                 "season_ppg", "goal_diff_pg", "win_rate_last5"]]


def add_manager_tenure(games: pd.DataFrame) -> pd.DataFrame:
    for side in ("home", "away"):
        cid = f"{side}_club_id"
        mgr = f"{side}_club_manager_name"
        first_seen = (games.groupby([cid, mgr])["date"]
                      .transform("min"))
        games[f"manager_tenure_{side}"] = (games["date"] - first_seen).dt.days
    games["manager_tenure_diff"] = (games["manager_tenure_home"]
                                    - games["manager_tenure_away"])

    # simple fill + flag
    games["manager_tenure_home_missing"] = games["manager_tenure_home"].isna().astype(int)
    games["manager_tenure_away_missing"] = games["manager_tenure_away"].isna().astype(int)
    games[["manager_tenure_home", "manager_tenure_away",
           "manager_tenure_diff"]] = games[["manager_tenure_home",
                                            "manager_tenure_away",
                                            "manager_tenure_diff"]].fillna(0)

    return games


def add_age_and_value(games: pd.DataFrame,
                      players: pd.DataFrame,
                      vals: pd.DataFrame) -> pd.DataFrame:
    """
    • avg_age_* : mean age of all registered players at the club on match-day
    • squad_value_* : sum of market values (latest valuation) for that club
    """
    # latest value already in player_valuations_clean.csv
    club_val = (vals.groupby("current_club_id")["market_value_in_eur"]
                    .sum()
                    .rename("squad_value"))

    # compute player age on each match date, then club mean
    players["date_of_birth"] = pd.to_datetime(players["date_of_birth"],
                                              errors="coerce")

    # merge age once per match-side
    for side in ("home", "away"):
        cid = f"{side}_club_id"

        # --- squad value ---
        games = games.merge(club_val, left_on=cid, right_index=True, how="left") \
                     .rename(columns={"squad_value": f"squad_value_{side}"})

        # --- average age ---
        ages = (games[[cid, "date"]]
                .drop_duplicates()
                .merge(players[["current_club_id", "date_of_birth"]],
                       left_on=cid, right_on="current_club_id", how="left"))
        ages["age"] = (ages["date"] - ages["date_of_birth"]).dt.days / 365.25
        club_age = ages.groupby([cid, "date"])["age"].mean().rename("avg_age")

        games = pd.merge_asof(
            games.sort_values("date"),
            club_age.reset_index().sort_values("date"),
            on="date",
            by=cid,
            direction="backward"
        ).rename(columns={"avg_age": f"avg_age_{side}"})

    # diffs
    games["squad_value_diff"] = (games["squad_value_home"]
                                 - games["squad_value_away"])
    games["avg_age_diff"] = (games["avg_age_home"]
                             - games["avg_age_away"])
    # 20 % missing data, add fix
    # ---- NaN handling + flags --------------------------------------
    for side in ("home", "away"):
        for col in ("avg_age", "squad_value"):
            full = f"{col}_{side}"
            flag = f"{full}_missing"
            games[flag] = games[full].isna().astype(int)
            games[full].fillna(games[full].median(), inplace=True)

    # recompute diffs after fill
    games["avg_age_diff"] = games["avg_age_home"] - games["avg_age_away"]
    games["squad_value_diff"] = games["squad_value_home"] - \
        games["squad_value_away"]
    return games

    return games


def add_foreign_ratio(g: pd.DataFrame, players: pd.DataFrame) -> pd.DataFrame:
    # ensure no NaNs in citizenship so every player counts
    players["country_of_citizenship"] = players["country_of_citizenship"].fillna(
        "unknown")

    # dominant (domestic) nationality per club
    dom_nat = (players.groupby("current_club_id")["country_of_citizenship"]
               .agg(lambda s: s.mode().iat[0]))
    players = players.join(dom_nat, on="current_club_id", rsuffix="_dom")
    players["is_foreign"] = (players["country_of_citizenship"]
                             != players["country_of_citizenship_dom"]).astype(int)

    fr = players.groupby("current_club_id")["is_foreign"].mean()   # 0-1 ratio

    for side in ("home", "away"):
        col = f"foreign_ratio_{side}"
        g = g.merge(fr.rename(col),
                    left_on=f"{side}_club_id",
                    right_index=True,
                    how="left")
        # flag + fill
        g[f"{col}_missing"] = g[col].isna().astype(int)
        g[col].fillna(0, inplace=True)

    g["foreign_ratio_diff"] = g["foreign_ratio_home"] - g["foreign_ratio_away"]
    return g

# mutual btw home-away pair


def add_head_to_head(g: pd.DataFrame) -> pd.DataFrame:
    g = g.sort_values("date").reset_index(drop=True)
    h2h_win, h2h_gd = [], []

    for idx, r in g.iterrows():
        mask = (
            ((g.home_club_id == r.home_club_id) & (g.away_club_id == r.away_club_id)) |
            ((g.home_club_id == r.away_club_id) &
             (g.away_club_id == r.home_club_id))
        ) & (g.date < r.date)
        prev = g.loc[mask].tail(5)

        if prev.empty:
            h2h_win.append(0.5)        # neutral prior
            h2h_gd.append(0)
            continue

        wins = (
            ((prev.home_club_id == r.home_club_id) & (prev.home_club_goals > prev.away_club_goals)) |
            ((prev.away_club_id == r.home_club_id) &
             (prev.away_club_goals > prev.home_club_goals))
        ).mean()
        gd = (
            prev.apply(lambda x: x.home_club_goals - x.away_club_goals
                       if x.home_club_id == r.home_club_id
                       else x.away_club_goals - x.home_club_goals, axis=1)
        ).sum()

        h2h_win.append(round(wins, 3))
        h2h_gd.append(gd)

    g["h2h_win_rate_home"] = h2h_win
    g["h2h_goal_diff"] = h2h_gd
    return g

# ------------------------------------------------------------


def build_features(clean_dir: str) -> pd.DataFrame:
    games, players, vals = load_cleaned(clean_dir)

    # block ➊ rest-days
    games = add_rest_days(games)

    # block ➋ season form
    form = add_season_form(games)
    for side in ("home", "away"):
        games = games.merge(
            form,
            left_on=["game_id", f"{side}_club_id"],
            right_on=["game_id", "club_id"],
            how="left"
        ).drop(columns="club_id")\
         .rename(columns={
             "season_ppg":    f"season_ppg_{side}",
             "goal_diff_pg":  f"goal_diff_pg_{side}",
             "win_rate_last5": f"win_rate_last5_{side}"
         })

    games["season_ppg_diff"] = games["season_ppg_home"] - \
        games["season_ppg_away"]
    games["goal_diff_pg_diff"] = games["goal_diff_pg_home"] - \
        games["goal_diff_pg_away"]
    games["win_rate_last5_diff"] = games["win_rate_last5_home"] - \
        games["win_rate_last5_away"]

    # block ➌  manager tenure  (add after season-form section)
    games = add_manager_tenure(games)

    # block ➍  age & squad value
    games = add_age_and_value(games, players, vals)

    # block ➎  foreign-player ratio
    games = add_foreign_ratio(games, players)

    # block ➏  head-to-head
    games = add_head_to_head(games)

    # block ➐  simple flags / direct
    games["home_team_flag"] = 1
    games["attendance_ratio"] = games["attendance"] / games["attendance"].max()
    games["attendance_missing"] = games["attendance_ratio"].isna().astype(int)
    games["attendance_ratio"].fillna(
        games["attendance_ratio"].median(), inplace=True)

    games["matchday_idx"] = games.groupby(
        ["season", "competition_id"]).cumcount()+1

    games["league_tier"] = games["competition_type"].map(
        {"Domestic League": 1, "Domestic Cup": 2}).fillna(3).astype("int8")

    # -------- NaN handling + nice rounding ---------------------------
    form_cols = [c for c in games.columns
                 if c.startswith(("season_ppg_", "goal_diff_pg_", "win_rate_last5_"))]

    games[form_cols] = games[form_cols].fillna(
        0)        # fill missing history with 0
    float_cols = [c for c in games.columns
                  if games[c].dtype == "float64"]
    games[float_cols] = games[float_cols].round(3)       # clip long decimals

    # return early for testing
    return games[[
        "game_id",
        # rest-day block
        "rest_days_home", "long_break_flag_home",
        "rest_days_away", "long_break_flag_away",
        "rest_days_diff", "long_break_flag_diff",
        # season-form block
        "season_ppg_home", "season_ppg_away", "season_ppg_diff",
        "goal_diff_pg_home", "goal_diff_pg_away", "goal_diff_pg_diff",
        "win_rate_last5_home", "win_rate_last5_away", "win_rate_last5_diff",
        # manager-tenure block
        "manager_tenure_home", "manager_tenure_away", "manager_tenure_diff",
        # age & value
        "avg_age_home", "avg_age_away", "avg_age_diff",
        "avg_age_home_missing", "avg_age_away_missing",
        "squad_value_home", "squad_value_away", "squad_value_diff",
        "squad_value_home_missing", "squad_value_away_missing",
        # foreign ratio
        "foreign_ratio_home", "foreign_ratio_away", "foreign_ratio_diff",
        # head-to-head
        "h2h_win_rate_home", "h2h_goal_diff",
        # simple flags
        "home_team_flag", "attendance_ratio", "attendance_missing", "matchday_idx", "league_tier"
    ]]


# ------------------------------------------------------------
if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--clean_dir", default="../cleaned_data")
    ap.add_argument("--out_csv",   default="match_features.csv")
    args = ap.parse_args()

    features = build_features(args.clean_dir)
    features.to_csv(args.out_csv, index=False)
    print("✅ wrote", args.out_csv, "| columns:", list(features.columns))
