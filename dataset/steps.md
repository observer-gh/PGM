### players.csv

<class 'pandas.core.frame.DataFrame'>
RangeIndex: 32601 entries, 0 to 32600
Data columns (total 23 columns):

##### Column Non-Null Count Dtype

---

0 player_id 32601 non-null int64  
 1 first_name 30539 non-null object
2 last_name 32601 non-null object
3 name 32601 non-null object
4 last_season 32601 non-null int64  
 5 current_club_id 32601 non-null int64  
 6 player_code 32601 non-null object
7 country_of_birth 29802 non-null object
8 city_of_birth 30146 non-null object
9 country_of_citizenship 32218 non-null object
10 date_of_birth 32554 non-null object
11 sub_position 32421 non-null object
12 position 32601 non-null object
13 foot 30065 non-null object
14 height_in_cm 30345 non-null float64
15 contract_expiration_date 20510 non-null object
16 agent_name 16582 non-null object
17 image_url 32601 non-null object
18 url 32601 non-null object
19 current_club_domestic_competition_id 32601 non-null object
20 current_club_name 32601 non-null object
21 market_value_in_eur 31078 non-null float64
22 highest_market_value_in_eur 31078 non-null float64
dtypes: float64(3), int64(3), object(17)
memory usage: 5.7+ MB
None

##### null rows:

player_id 0
first_name 2062
last_name 0
name 0
last_season 0
current_club_id 0
player_code 0
country_of_birth 2799
city_of_birth 2455
country_of_citizenship 383
date_of_birth 47
sub_position 180
position 0
foot 2536
height_in_cm 2256
contract_expiration_date 12091
agent_name 16019
image_url 0
url 0
current_club_domestic_competition_id 0
current_club_name 0
market_value_in_eur 1523
highest_market_value_in_eur 1523
dtype: int64

### games.csv

<class 'pandas.core.frame.DataFrame'>
RangeIndex: 74026 entries, 0 to 74025
Data columns (total 23 columns):

##### Column Non-Null Count Dtype

---

0 game_id 74026 non-null int64  
 1 competition_id 74026 non-null object
2 season 74026 non-null int64  
 3 round 74026 non-null object
4 date 74026 non-null object
5 home_club_id 74017 non-null float64
6 away_club_id 74017 non-null float64
7 home_club_goals 74014 non-null float64
8 away_club_goals 74014 non-null float64
9 home_club_position 51559 non-null float64
10 away_club_position 51559 non-null float64
11 home_club_manager_name 73198 non-null object
12 away_club_manager_name 73198 non-null object
13 stadium 73776 non-null object
14 attendance 64078 non-null float64
15 referee 73374 non-null object
16 url 74026 non-null object
17 home_club_formation 67051 non-null object
18 away_club_formation 67220 non-null object
19 home_club_name 61176 non-null object
20 away_club_name 62571 non-null object
21 aggregate 74014 non-null object
22 competition_type 74026 non-null object
dtypes: float64(7), int64(2), object(14)
memory usage: 13.0+ MB
None

##### null rows:

game_id 0
competition_id 0
season 0
round 0
date 0
home_club_id 9
away_club_id 9
home_club_goals 12
away_club_goals 12
home_club_position 22467
away_club_position 22467
home_club_manager_name 828
away_club_manager_name 828
stadium 250
attendance 9948
referee 652
url 0
home_club_formation 6975
away_club_formation 6806
home_club_name 12850
away_club_name 11455
aggregate 12
competition_type 0
dtype: int64
<class 'pandas.core.frame.DataFrame'>
RangeIndex: 496606 entries, 0 to 496605
Data columns (total 5 columns):

# Column Non-Null Count Dtype

---

0 player_id 496606 non-null int64
1 date 496606 non-null object
2 market_value_in_eur 496606 non-null int64
3 current_club_id 496606 non-null int64
4 player_club_domestic_competition_id 496606 non-null object
dtypes: int64(3), object(2)
memory usage: 18.9+ MB
None
null rows:
player_id 0
date 0
market_value_in_eur 0
current_club_id 0
player_club_domestic_competition_id 0
dtype: int64
