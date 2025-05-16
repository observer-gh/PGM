games.csv

- long breaks -> clip at 60
- no break data -> 7
- no season info club -> no season_ppg -> fill with 0
- missing before adding in default values

  avg_age_diff 15637 21.13
  squad_value_diff 15637 21.13
  avg_age_home 12900 17.43
  squad_value_home 12900 17.43
  avg_age_away 11513 15.56
  squad_value_away 11513 15.56
  manager_tenure_home 816 1.10
  manager_tenure_away 816 1.10
  manager_tenure_diff 816 1.10

- missing nationality -> use "unknown"

  foreign_ratio_diff 15637 21.13
  foreign_ratio_home 12900 17.43
  foreign_ratio_away 11513 15.56

- h2h missing -> wr 0.5, goal 0 prior added
- attendance missing ->
  attendance_ratio 9936 13.42
