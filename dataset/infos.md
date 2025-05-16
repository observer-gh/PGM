players.csv

- 32601 entries
- 1523 lacks market value, which is critical

games.csv

- 496606 entires
- 9 miss home/away team info. critical
- 12 miss goals info. critical
- 22467 miss club position info. needed?

player_valuations.csv

- 1523 players missing, compared to players.csv

30 pre-match (“macro”) features for match-outcome modelling

# Feature Scope Quick definition

⸻

1. Raw tables & critical fixes

CSV Rows Main issues Actions
games.csv 74 026 → 74 014 9 missing club IDs, 12 missing scores drop those rows, parse date, cast IDs to int64
players.csv 32 601 1 523 missing market_value_in_eur, some missing DOB / nationality merge latest valuation, fill remaining values (see table below)
player_valuations.csv 496 606 (→ 31 078 unique players) many duplicates per player sort by date, keep latest row

⸻

2. Feature set (32 pre-kick-off inputs)

# Feature column(s) Missing before fix Imputation / flag Note

1. home_team_flag

2. rest_days_home / rest_days_away / rest_days_diff
   • Handling: if a club has no prior match date → fill 7 days (one-week prior); any gap > 60 days is capped at 60.
   • \*The very first match per club had a raw NaT; the 7-day default fixes this.
3. long_break_flag_home / long_break_flag_away / long_break_flag_diff
   • Derived: 1 when raw rest-gap > 60 days; 0 otherwise.
4. season_ppg_home / away / diff (cumulative points-per-game)
   • Missing before %: ≈ 2.4 % (no prior games)
   • Handling: NaN → 0.
5. goal_diff_pg_home / away / diff (goal-difference per game)
   • Same missing pattern and fix as above (NaN → 0).
6. win_rate_last5_home / away / diff
   • Same missing pattern and fix (NaN → 0).
7. league_tier

8. manager_tenure_home / away / diff
   • Missing before %: 1.1 % (no manager name)
   • Handling: NaN → 0 (“unknown/new”) plus flags manager_tenure_home_missing, manager_tenure_away_missing.
9. avg_age_home / away / diff
   • Missing % before fill: 17 % (no DOB)
   • Handling: median age fill per column plus avg_age_home_missing, avg_age_away_missing.
10. squad_value_home / away / diff
    • Missing % before fill: 17 % (no valuation)
    • Handling: global median fill plus squad_value_home_missing, squad_value_away_missing.
11. foreign_ratio_home / away / diff
    • Missing % before fix: 17 %
    • Handling: players with missing citizenship set to "unknown" so every club has a dominant nationality; remaining NaN ratios filled 0, with flags foreign_ratio_home_missing, foreign_ratio_away_missing.
    • Interpretation: ratio = share of non-domestic players.
12. attendance_ratio
    • Missing %: 13.4 %
    • Handling: median fill plus attendance_missing flag.
    • Computation: attendance / max(attendance) in dataset.
13. matchday_idx
    • Missing %: 0 %
    • Handling: sequential counter (cumcount+1) within each season × competition.
14. h2h_win_rate_home
    • Missing %: 0 % (by design)
    • Handling: if the two clubs never met before, set neutral prior 0.5.
15. h2h_goal_diff
    • Missing %: 0 %
    • Handling: same “no-history” prior set to 0.

After these steps all numeric features have 0 % NaNs.
Every median or default substitution is trackable via a corresponding \_missing or flag column.

⸻

3. Key design choices
   • Neutral priors keep early-season matches (rest = 7 d, win-rate = 0.5, GD = 0).
   • Median fill + binary flag approach for age, value, attendance, nationality—simple, transparent, model can learn if “info missing” matters.
   • Long off-season gaps isolated via long*break_flag*\*.
   • All features are computable before kick-off (no in-play events).

⸻

4. File outputs

match_features.csv # final table: 74 014 rows × 33 cols (target + 32 features)

⸻

Questions or tweaks? Ping @you-know-who in Slack.
