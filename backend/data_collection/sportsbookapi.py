import requests
import json
import os
from dotenv import load_dotenv

load_dotenv()
API_KEY = os.getenv('ODDS_API_KEY') # get api key from .env

SPORT = 'americanfootball_nfl'
REGIONS = 'us'
MARKETS = 'player_pass_yds'  # Just QB passing yards!
MAX_GAMES = 5  # Limit to 5 games

# Step 1: Get all NFL games
games_response = requests.get(
    f'https://api.the-odds-api.com/v4/sports/{SPORT}/odds',
    params={
        'apiKey': API_KEY,
        'regions': REGIONS,
        'markets': 'h2h',
        'oddsFormat': 'american',
    }
)

if games_response.status_code != 200: # 200 is successful
    print(f"Error getting games: {games_response.status_code}")
    print(games_response.text)
    exit()

games = games_response.json()
print(f"Found {len(games)} NFL games")
print(f"Pulling QB passing yards for first {MAX_GAMES} games\n")

# Step 2: Get QB passing yards props for first 5 games only
all_props = []
for i, game in enumerate(games[:MAX_GAMES], 1):  # Only first 5 games
    print(f"[{i}/{MAX_GAMES}] Getting passing yards for: {game['away_team']} @ {game['home_team']}")
    
    props_response = requests.get(
        f'https://api.the-odds-api.com/v4/sports/{SPORT}/events/{game['id']}/odds',
        params={
            'apiKey': API_KEY,
            'regions': REGIONS,
            'markets': MARKETS,
            'oddsFormat': 'american',
        }
    )
    
    if props_response.status_code == 200:
        all_props.append(props_response.json())
    else:
        print(f"  ❌ Error: {props_response.status_code}")

os.makedirs('backend/data_storage', exist_ok=True)  # Create folder if it doesn't exist
# Save to file for later use
with open('backend/data_storage/qb_passing_props.json', 'w') as f:
    json.dump(all_props, f, indent=2)

print(f"\n✅ Successfully pulled QB passing yards for {len(all_props)} games")
print(f"📁 Saved to backend/data_storage/qb_passing_props.json")
print(f"💳 Credits remaining: {props_response.headers.get('x-requests-remaining')}")
print(f"💳 Credits used this month: {props_response.headers.get('x-requests-used')}")
print(f"💰 Credits used this call: 5 (1 per game)")