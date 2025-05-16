import pandas as pd

df = pd.read_csv("match_features.csv")   # or the in-memory DataFrame

# count + percent of NaNs for every column
na = df.isna().sum().to_frame("missing")
na["pct"] = (na["missing"] / len(df) * 100).round(2)

# show only columns that still have NaNs, sorted high → low
print(na[na["missing"] > 0].sort_values("pct", ascending=False))
