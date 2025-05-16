import os
import pandas as pd

players = pd.read_csv("./raw_data/players.csv")
games = pd.read_csv("./raw_data/games.csv")
valuations = pd.read_csv("./raw_data/player_valuations.csv")

# Clean players dataframe
players_clean = players.drop(columns=[
    'agent_name', 'image_url', 'url', 'player_code', 'contract_expiration_date'
]).copy()  # <- important: make explicit copy here to avoid chained assignment

# Fill numerical missing values explicitly
players_clean['height_in_cm'] = players_clean['height_in_cm'].fillna(
    players_clean['height_in_cm'].median()
)
players_clean['market_value_in_eur'] = players_clean['market_value_in_eur'].fillna(
    players_clean['market_value_in_eur'].median()
)

# Fill categorical missing values explicitly
for col in ['foot', 'country_of_birth', 'first_name']:
    players_clean[col] = players_clean[col].fillna("Unknown")

# Clean games dataframe explicitly
games_clean = games.dropna(
    subset=['home_club_goals', 'away_club_goals', 'home_club_id', 'away_club_id']).copy()

games_clean = games_clean.drop(
    columns=['attendance', 'referee', 'stadium', 'url'])

# Player id consistency check
valuation_player_ids = set(valuations['player_id'].unique())
player_ids = set(players_clean['player_id'].unique())
missing_in_valuations = player_ids - valuation_player_ids
print("Players missing in valuations:", len(missing_in_valuations))

# which players are missing
missing_players_df = players_clean[players_clean['player_id'].isin(
    missing_in_valuations)]
print(missing_players_df.head())

# Create a directory named "cleaned_data" first or ensure it exists

output_folder = './cleaned_data'
os.makedirs(output_folder, exist_ok=True)

# Save cleaned players dataframe
players_clean.to_csv(os.path.join(
    output_folder, 'players_clean.csv'), index=False)

# Save cleaned games dataframe
games_clean.to_csv(os.path.join(output_folder, 'games_clean.csv'), index=False)

# Save valuations (since it's already clean)
valuations.to_csv(os.path.join(
    output_folder, 'player_valuations_clean.csv'), index=False)

print("✅ Cleaned dataframes saved successfully.")
