"""
Match props between Sportsbook and PrizePicks
Filters PrizePicks data to only include players from the sportsbook games
"""
import json

def load_data():
    """Load both datasets"""
    print("\n" + "="*60)
    print("LOADING DATA")
    print("="*60)
    
    with open('backend/data_storage/qb_passing_props.json', 'r') as f:
        sportsbook_data = json.load(f)
    print("✅ Loaded sportsbook data")
    
    with open('backend/data_storage/prizepicks_props.json', 'r') as f:
        prizepicks_data = json.load(f)
    print("✅ Loaded PrizePicks data")
    
    return sportsbook_data, prizepicks_data

def extract_sportsbook_players(games):
    """
    Extract player names and their lines from sportsbook data
    Returns: dict with player names as keys
    """
    print("\n" + "="*60)
    print("EXTRACTING SPORTSBOOK PLAYERS")
    print("="*60)
    
    players = {}
    
    for game in games:
        game_info = f"{game['away_team']} @ {game['home_team']}"
        
        for bookmaker in game.get('bookmakers', []):
            for market in bookmaker.get('markets', []):
                if market['key'] == 'player_pass_yds':
                    for outcome in market['outcomes']:
                        player_name = outcome['description']
                        
                        # Initialize player if not seen before
                        if player_name not in players:
                            players[player_name] = {
                                'game': game_info,
                                'commence_time': game['commence_time'],
                                'sportsbook_lines': {}
                            }
                        
                        # Store lines by bookmaker (Over line only)
                        if outcome['name'] == 'Over':
                            players[player_name]['sportsbook_lines'][bookmaker['title']] = {
                                'line': outcome['point'],
                                'odds': outcome['price']
                            }
    
    print(f"Found {len(players)} unique players:")
    for player in players.keys():
        print(f"  - {player}")
    
    return players

def extract_prizepicks_props(prizepicks_data):
    """
    Extract PrizePicks props organized by player
    Returns: dict with player names as keys
    """
    print("\n" + "="*60)
    print("EXTRACTING PRIZEPICKS PROPS")
    print("="*60)
    
    # Build player name lookup from 'included' section
    player_names = {}
    for item in prizepicks_data.get('included', []):
        if item['type'] == 'new_player':
            player_names[item['id']] = item['attributes']['name']
    
    # Extract props by player
    props_by_player = {}
    for projection in prizepicks_data.get('data', []):
        player_id = projection['relationships']['new_player']['data']['id']
        player_name = player_names.get(player_id)
        
        if not player_name:
            continue
        
        stat_type = projection['attributes']['stat_type']
        line = projection['attributes']['line_score']
        
        # Initialize player if not seen
        if player_name not in props_by_player:
            props_by_player[player_name] = []
        
        props_by_player[player_name].append({
            'stat_type': stat_type,
            'line': line
        })
    
    print(f"Found props for {len(props_by_player)} players")
    
    return props_by_player

def match_props(sportsbook_players, prizepicks_props):
    """
    Match props between the two sources
    Only includes players that appear in sportsbook data
    """
    print("\n" + "="*60)
    print("MATCHING PROPS")
    print("="*60)
    
    matches = []
    
    for player_name, sb_data in sportsbook_players.items():
        # Check if this player has PrizePicks props
        if player_name not in prizepicks_props:
            print(f"⚠️  {player_name}: No PrizePicks data found")
            continue
        
        # Look for "Pass Yards" stat specifically (not "Pass+Rush Yds")
        pp_props = prizepicks_props[player_name]
        passing_prop = None
        
        for prop in pp_props:
            # Match ONLY pure passing yards
            if prop['stat_type'] == 'Pass Yards':
                passing_prop = prop
                break
        
        if not passing_prop:
            print(f"⚠️  {player_name}: Has PrizePicks props but no 'Pass Yards' stat")
            continue
        
        # We have a match!
        match = {
            'player': player_name,
            'game': sb_data['game'],
            'commence_time': sb_data['commence_time'],
            'prizepicks_line': passing_prop['line'],
            'sportsbook_lines': sb_data['sportsbook_lines']
        }
        
        matches.append(match)
        print(f"✅ {player_name}: Matched!")
    
    return matches

def display_matches(matches):
    """Display matched props in a readable format"""
    print("\n" + "="*60)
    print(f"MATCHED PROPS SUMMARY ({len(matches)} total)")
    print("="*60)
    
    for match in matches:
        print(f"\n🏈 {match['player']}")
        print(f"   Game: {match['game']}")
        print(f"   PrizePicks Line: {match['prizepicks_line']} yards")
        print(f"   Sportsbook Lines:")
        for book, data in match['sportsbook_lines'].items():
            print(f"      {book}: {data['line']} yards (odds: {data['odds']})")

def save_matches(matches):
    """Save matched props to file"""
    with open('backend/data_storage/matched_props.json', 'w') as f:
        json.dump(matches, f, indent=2)
    print(f"\n📁 Saved {len(matches)} matches to backend/data_storage/matched_props.json")

def main():
    """Main matching workflow"""
    print("\n" + "🔄" * 30)
    print("PRIZEPICKS EV FINDER - PROP MATCHING")
    print("🔄" * 30)
    
    # Load data
    sportsbook_data, prizepicks_data = load_data()
    
    # Extract players from sportsbook (these are the only ones we care about!)
    sportsbook_players = extract_sportsbook_players(sportsbook_data)
    
    # Extract all PrizePicks props
    prizepicks_props = extract_prizepicks_props(prizepicks_data)
    
    # Match them up (filtered to sportsbook players only)
    matches = match_props(sportsbook_players, prizepicks_props)
    
    # Display results
    display_matches(matches)
    
    # Save to file
    save_matches(matches)
    
    print("\n" + "="*60)
    print("✅ MATCHING COMPLETE!")
    print("="*60)
    print("\nNext step: Calculate EV for these matched props")

if __name__ == "__main__":
    main()