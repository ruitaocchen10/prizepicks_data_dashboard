"""
Deep dive into PrizePicks data structure
This will help us understand exactly how the data is organized
"""
import json
from collections import defaultdict

# Load PrizePicks data
with open('backend/data_storage/prizepicks_props.json', 'r') as f:
    data = json.load(f)

print("=" * 80)
print("PRIZEPICKS DATA DEEP DIVE")
print("=" * 80)

# ============================================================================
# PART 1: Understanding the 'included' section (where player info lives)
# ============================================================================
print("\n" + "=" * 80)
print("PART 1: 'INCLUDED' SECTION (Player & Game Info)")
print("=" * 80)

included_types = defaultdict(int)
for item in data['included']:
    included_types[item['type']] += 1

print(f"\nTypes found in 'included':")
for type_name, count in included_types.items():
    print(f"  {type_name}: {count} items")

# Look at a sample player
print("\n" + "-" * 80)
print("SAMPLE PLAYER from 'included':")
print("-" * 80)
sample_player = next((item for item in data['included'] if item['type'] == 'new_player'), None)
if sample_player:
    print(json.dumps(sample_player, indent=2))

# Look at a sample game
print("\n" + "-" * 80)
print("SAMPLE GAME from 'included':")
print("-" * 80)
sample_game = next((item for item in data['included'] if item['type'] == 'game'), None)
if sample_game:
    print(json.dumps(sample_game, indent=2))

# ============================================================================
# PART 2: Understanding the 'data' section (where projections/props live)
# ============================================================================
print("\n" + "=" * 80)
print("PART 2: 'DATA' SECTION (Projections/Props)")
print("=" * 80)

print(f"\nTotal projections: {len(data['data'])}")

# Analyze stat types
stat_types = defaultdict(int)
for projection in data['data']:
    stat_type = projection['attributes'].get('stat_type', 'Unknown')
    stat_types[stat_type] += 1

print(f"\nAll stat types found (sorted by count):")
for stat_type, count in sorted(stat_types.items(), key=lambda x: x[1], reverse=True):
    print(f"  {stat_type}: {count} props")

# Look at a sample projection
print("\n" + "-" * 80)
print("SAMPLE PROJECTION from 'data':")
print("-" * 80)
sample_projection = data['data'][0]
print(json.dumps(sample_projection, indent=2))

# ============================================================================
# PART 3: How to connect 'data' to 'included' (the relationships)
# ============================================================================
print("\n" + "=" * 80)
print("PART 3: CONNECTING DATA TO INCLUDED (Relationships)")
print("=" * 80)

# Build lookup dictionaries
players_lookup = {}
games_lookup = {}

for item in data['included']:
    if item['type'] == 'new_player':
        players_lookup[item['id']] = item['attributes']
    elif item['type'] == 'game':
        games_lookup[item['id']] = item['attributes']

print(f"\nBuilt lookup tables:")
print(f"  Players: {len(players_lookup)} entries")
print(f"  Games: {len(games_lookup)} entries")

# Show how to connect them
print("\n" + "-" * 80)
print("EXAMPLE: Connecting a projection to its player:")
print("-" * 80)
sample_proj = data['data'][0]
player_id = sample_proj['relationships']['new_player']['data']['id']
player_info = players_lookup.get(player_id, {})

print(f"Projection ID: {sample_proj['id']}")
print(f"  stat_type: {sample_proj['attributes']['stat_type']}")
print(f"  line_score: {sample_proj['attributes']['line_score']}")
print(f"  player_id (from relationships): {player_id}")
print(f"  player_name (from lookup): {player_info.get('name', 'Unknown')}")
print(f"  player_team (from lookup): {player_info.get('team', 'Unknown')}")

# ============================================================================
# PART 4: Finding specific QB passing props
# ============================================================================
print("\n" + "=" * 80)
print("PART 4: FINDING QB PASSING PROPS")
print("=" * 80)

# Let's find all passing-related props
passing_stats = {}
for projection in data['data']:
    stat_type = projection['attributes']['stat_type']
    
    # Look for anything with "Pass" in it
    if 'Pass' in stat_type:
        player_id = projection['relationships']['new_player']['data']['id']
        player_info = players_lookup.get(player_id, {})
        player_name = player_info.get('name', 'Unknown')
        
        if player_name not in passing_stats:
            passing_stats[player_name] = []
        
        passing_stats[player_name].append({
            'stat_type': stat_type,
            'line': projection['attributes']['line_score'],
            'team': player_info.get('team', 'Unknown')
        })

print(f"\nFound {len(passing_stats)} players with passing props:")
print("\nFirst 10 players with their passing props:")
for i, (player, props) in enumerate(list(passing_stats.items())[:10], 1):
    print(f"\n{i}. {player} ({props[0]['team']})")
    for prop in props:
        print(f"     - {prop['stat_type']}: {prop['line']}")

# ============================================================================
# PART 5: Understanding multiple lines per player
# ============================================================================
print("\n" + "=" * 80)
print("PART 5: WHY MULTIPLE LINES PER PLAYER?")
print("=" * 80)

# Pick a player with multiple props
sample_player_name = list(passing_stats.keys())[0]
sample_props = passing_stats[sample_player_name]

print(f"\nExample: {sample_player_name} has {len(sample_props)} passing props")
print("\nLet's look at the full details of each:")

for prop_info in sample_props:
    # Find the full projection
    for projection in data['data']:
        stat_type = projection['attributes']['stat_type']
        player_id = projection['relationships']['new_player']['data']['id']
        player_info = players_lookup.get(player_id, {})
        
        if (player_info.get('name') == sample_player_name and 
            stat_type == prop_info['stat_type'] and
            projection['attributes']['line_score'] == prop_info['line']):
            
            print(f"\n{stat_type}: {prop_info['line']}")
            print(f"  odds_type: {projection['attributes'].get('odds_type', 'N/A')}")
            print(f"  projection_type: {projection['attributes'].get('projection_type', 'N/A')}")
            print(f"  adjusted_odds: {projection['attributes'].get('adjusted_odds', 'N/A')}")
            break

print("\n" + "=" * 80)
print("KEY INSIGHTS:")
print("=" * 80)
print("""
1. 'included' section contains player and game metadata (names, teams, etc.)
2. 'data' section contains the actual projections/lines
3. They're connected via 'relationships' -> player ID
4. Each player can have MULTIPLE lines for the SAME stat type
5. These might be different odds tiers (demon, goblin, etc.)
6. We probably want the STANDARD line, not adjusted odds
""")

# ============================================================================
# PART 6: Recommendation for matching
# ============================================================================
print("\n" + "=" * 80)
print("RECOMMENDATION FOR MATCHING:")
print("=" * 80)
print("""
For matching with sportsbook data, we should:

1. Filter to stat_type == 'Pass Yards' (exact match, not Pass+Rush)
2. Look for adjusted_odds == False (standard lines, not promotional)
3. If multiple lines exist, pick the one closest to sportsbook average
4. OR take the middle/most common line

Let's check which 'Pass Yards' props meet these criteria:
""")

standard_passing = []
for projection in data['data']:
    if (projection['attributes']['stat_type'] == 'Pass Yards' and
        projection['attributes'].get('adjusted_odds') == False):
        
        player_id = projection['relationships']['new_player']['data']['id']
        player_info = players_lookup.get(player_id, {})
        
        standard_passing.append({
            'player': player_info.get('name', 'Unknown'),
            'team': player_info.get('team', 'Unknown'),
            'line': projection['attributes']['line_score'],
            'odds_type': projection['attributes'].get('odds_type', 'N/A')
        })

print(f"\nFound {len(standard_passing)} 'Pass Yards' props with adjusted_odds=False:")
for prop in standard_passing[:15]:
    print(f"  {prop['player']} ({prop['team']}): {prop['line']} yards [odds_type: {prop['odds_type']}]")

if len(standard_passing) > 15:
    print(f"  ... and {len(standard_passing) - 15} more")

print("\n" + "=" * 80)