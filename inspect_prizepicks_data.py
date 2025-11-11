import json

# Load the PrizePicks data
with open('backend/data_storage/prizepicks_props.json', 'r') as f:
    data = json.load(f)

print("=" * 60)
print("PRIZEPICKS DATA STRUCTURE")
print("=" * 60)

# Check top-level keys
print(f"\nTop-level keys: {list(data.keys())}")
print(f"Number of projections: {len(data.get('data', []))}")
print(f"Number of included items: {len(data.get('included', []))}")

# Look at first projection
if data.get('data'):
    print("\n" + "=" * 60)
    print("SAMPLE PROJECTION (first one):")
    print("=" * 60)
    print(json.dumps(data['data'][0], indent=2))

# Look at players in 'included'
if data.get('included'):
    print("\n" + "=" * 60)
    print("SAMPLE PLAYERS (first 5):")
    print("=" * 60)
    
    players = [item for item in data['included'] if item.get('type') == 'new_player']
    
    for i, player in enumerate(players[:5], 1):
        player_name = player.get('attributes', {}).get('name')
        player_team = player.get('attributes', {}).get('team')
        print(f"{i}. {player_name} ({player_team})")

# Find QB passing yard props specifically
print("\n" + "=" * 60)
print("QB PASSING YARD PROPS:")
print("=" * 60)

# Build player lookup
player_names = {}
for item in data.get('included', []):
    if item['type'] == 'new_player':
        player_names[item['id']] = {
            'name': item['attributes']['name'],
            'team': item['attributes'].get('team', 'N/A')
        }

# Find passing props
passing_props = []
for projection in data.get('data', []):
    stat_type = projection.get('attributes', {}).get('stat_type', '')
    
    if 'Pass' in stat_type or 'pass' in stat_type.lower():
        player_id = projection['relationships']['new_player']['data']['id']
        player_info = player_names.get(player_id, {'name': 'Unknown', 'team': 'N/A'})
        
        passing_props.append({
            'player': player_info['name'],
            'team': player_info['team'],
            'stat_type': stat_type,
            'line': projection['attributes']['line_score']
        })

print(f"\nFound {len(passing_props)} passing props:")
for prop in passing_props[:10]:  # Show first 10
    print(f"  {prop['player']} ({prop['team']}) - {prop['stat_type']}: {prop['line']}")

if len(passing_props) > 10:
    print(f"  ... and {len(passing_props) - 10} more")