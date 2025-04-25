import pandas as pd

players = pd.read_csv('./cleaned_data/players_clean.csv')
games = pd.read_csv('./cleaned_data/games_clean.csv')
valuations = pd.read_csv('./cleaned_data/player_valuations_clean.csv')
appearances = pd.read_csv('./raw_data/appearances.csv')
# Merge player data into appearances
appearances = appearances.merge(players[['player_id', 'date_of_birth', 'country_of_citizenship']],
                                on='player_id', how='left')

# Calculate age at match date
appearances['date'] = pd.to_datetime(appearances['date'])
appearances['date_of_birth'] = pd.to_datetime(
    appearances['date_of_birth'], errors='coerce')
appearances['player_age'] = (
    appearances['date'] - appearances['date_of_birth']).dt.days / 365.25

# Merge latest valuations clearly
valuations['date'] = pd.to_datetime(valuations['date'])
latest_valuations = valuations.sort_values(
    'date').groupby('player_id').last().reset_index()

appearances = appearances.merge(latest_valuations[['player_id', 'market_value_in_eur']],
                                on='player_id', how='left')

# Aggregate clearly by game_id & club_id
team_features = appearances.groupby(['game_id', 'player_club_id']).agg({
    'market_value_in_eur': 'mean',
    'country_of_citizenship': lambda x: x.nunique(),
    'player_age': 'mean',
    'minutes_played': 'sum',
    'goals': 'sum',
    'assists': 'sum',
    'yellow_cards': 'sum',
    'red_cards': 'sum'
}).reset_index()

team_features.rename(columns={
    'market_value_in_eur': 'avg_market_value',
    'country_of_citizenship': 'nationalities',
    'player_age': 'avg_age',
    'minutes_played': 'total_minutes',
    'goals': 'total_goals',
    'assists': 'total_assists',
    'yellow_cards': 'total_yellow_cards',
    'red_cards': 'total_red_cards'
}, inplace=True)

# Prepare home & away clearly in the games dataframe
games = games[['game_id', 'date', 'home_club_id',
               'away_club_id', 'home_club_goals', 'away_club_goals']]

# Merge home features
games = games.merge(team_features, left_on=['game_id', 'home_club_id'], right_on=[
                    'game_id', 'player_club_id'], how='left')
games.rename(columns={
    'avg_market_value': 'home_avg_market_value',
    'nationalities': 'home_nationalities',
    'avg_age': 'home_avg_age',
    'total_minutes': 'home_total_minutes',
    'total_goals': 'home_total_goals',
    'total_assists': 'home_total_assists',
    'total_yellow_cards': 'home_total_yellow_cards',
    'total_red_cards': 'home_total_red_cards'
}, inplace=True)
games.drop('player_club_id', axis=1, inplace=True)

# Merge away features
games = games.merge(team_features, left_on=['game_id', 'away_club_id'], right_on=[
                    'game_id', 'player_club_id'], how='left')
games.rename(columns={
    'avg_market_value': 'away_avg_market_value',
    'nationalities': 'away_nationalities',
    'avg_age': 'away_avg_age',
    'total_minutes': 'away_total_minutes',
    'total_goals': 'away_total_goals',
    'total_assists': 'away_total_assists',
    'total_yellow_cards': 'away_total_yellow_cards',
    'total_red_cards': 'away_total_red_cards'
}, inplace=True)
games.drop('player_club_id', axis=1, inplace=True)

# Compute final match result


def match_result(row):
    if row['home_club_goals'] > row['away_club_goals']:
        return 'Home Win'
    elif row['home_club_goals'] < row['away_club_goals']:
        return 'Away Win'
    else:
        return 'Draw'


games['result'] = games.apply(match_result, axis=1)

# Save flattened data clearly
final_dataset = games.dropna().reset_index(drop=True)
final_dataset.to_csv('./cleaned_data/final_dataset.csv', index=False)
print("✅ Final flattened dataset created successfully!")
