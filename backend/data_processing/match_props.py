"""
FIXED Match props between Sportsbook and PrizePicks
Only matches STANDARD lines (not demon/goblin)
UPDATED FOR PASSING TDs
"""
import json

def load_data():
    """Load both datasets"""
    print("\n" + "="*60)
    print("LOADING DATA")
    print("="*60)
    
    with open('backend/data_storage/qb_passing_tds.json', 'r') as f:
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
                if market['key'] == 'player_pass_tds':
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

def extract_prizepicks_standard_lines(prizepicks_data):
    """
    Extract ONLY STANDARD 'Pass TDs' lines from PrizePicks
    Filters out demon and goblin lines
    Returns: dict with player names as keys
    """
    print("\n" + "="*60)
    print("EXTRACTING PRIZEPICKS STANDARD LINES")
    print("="*60)
    
    # Build player name lookup from 'included' section
    player_names = {}
    for item in prizepicks_data.get('included', []):
        if item['type'] == 'new_player':
            player_names[item['id']] = {
                'name': item['attributes']['name'],
                'team': item['attributes'].get('team', 'N/A')
            }
    
    # Extract ONLY standard Pass TDs lines
    standard_lines = {}
    
    for projection in prizepicks_data.get('data', []):
        stat_type = projection['attributes']['stat_type']
        odds_type = projection['attributes'].get('odds_type', 'unknown')
        adjusted_odds = projection['attributes'].get('adjusted_odds')
        
        # CRITICAL FILTERS:
        # 1. Must be "Pass TDs" (not Pass+Rush TDs)
        # 2. Must be "standard" odds type
        # 3. adjusted_odds should be None or False (not True)
        if (stat_type == 'Pass TDs' and 
            odds_type == 'standard' and
            adjusted_odds != True):
            
            player_id = projection['relationships']['new_player']['data']['id']
            player_info = player_names.get(player_id, {})
            player_name = player_info.get('name', 'Unknown')
            
            # Only keep one line per player (the standard line)
            if player_name not in standard_lines:
                standard_lines[player_name] = {
                    'team': player_info.get('team', 'N/A'),
                    'line': projection['attributes']['line_score'],
                    'stat_type': stat_type,
                    'odds_type': odds_type
                }
    
    print(f"Found {len(standard_lines)} players with STANDARD Pass TDs lines:")
    for player, data in standard_lines.items():
        print(f"  - {player} ({data['team']}): {data['line']} TDs")
    
    return standard_lines

def match_props(sportsbook_players, prizepicks_standard_lines):
    """
    Match props between the two sources
    Only includes players that appear in BOTH datasets
    """
    print("\n" + "="*60)
    print("MATCHING PROPS")
    print("="*60)
    
    matches = []
    players_not_found = []
    
    for player_name, sb_data in sportsbook_players.items():
        # Check if this player has a PrizePicks STANDARD line
        if player_name in prizepicks_standard_lines:
            pp_data = prizepicks_standard_lines[player_name]
            
            # Calculate average sportsbook line for comparison
            sb_lines = [data['line'] for data in sb_data['sportsbook_lines'].values()]
            avg_sb_line = sum(sb_lines) / len(sb_lines) if sb_lines else 0
            
            # We have a match!
            match = {
                'player': player_name,
                'game': sb_data['game'],
                'commence_time': sb_data['commence_time'],
                'prizepicks': {
                    'line': pp_data['line'],
                    'team': pp_data['team']
                },
                'sportsbook': {
                    'lines': sb_data['sportsbook_lines'],
                    'average_line': round(avg_sb_line, 1)
                },
                'line_difference': round(pp_data['line'] - avg_sb_line, 1)
            }
            
            matches.append(match)
            print(f"✅ {player_name}: Matched!")
            print(f"   PrizePicks: {pp_data['line']} | Sportsbook avg: {avg_sb_line}")
        else:
            players_not_found.append(player_name)
            print(f"⚠️  {player_name}: No standard PrizePicks line found")
    
    if players_not_found:
        print(f"\n⚠️  {len(players_not_found)} players from sportsbook not found in PrizePicks:")
        for player in players_not_found:
            print(f"   - {player}")
        print("\nPossible reasons:")
        print("   1. PrizePicks doesn't have a standard line for this player")
        print("   2. They only have demon/goblin lines")
        print("   3. Name mismatch between sources")
    
    return matches

def display_matches(matches):
    """Display matched props in a readable format"""
    print("\n" + "="*60)
    print(f"MATCHED PROPS SUMMARY ({len(matches)} total)")
    print("="*60)
    
    if not matches:
        print("\n❌ No matches found!")
        print("\nThis could mean:")
        print("  1. Different games between sportsbook and PrizePicks")
        print("  2. PrizePicks only has demon/goblin lines for these players")
        print("  3. Name formatting differences")
        return
    
    for match in matches:
        print(f"\n🏈 {match['player']}")
        print(f"   Game: {match['game']}")
        print(f"   PrizePicks: {match['prizepicks']['line']} TDs")
        print(f"   Sportsbook average: {match['sportsbook']['average_line']} TDs")
        print(f"   Difference: {match['line_difference']} TDs")
        print(f"   Sportsbook lines:")
        for book, data in match['sportsbook']['lines'].items():
            print(f"      {book}: {data['line']} TDs (odds: {data['odds']})")

def save_matches(matches):
    """Save matched props to file"""
    with open('backend/data_storage/matched_tds.json', 'w') as f:
        json.dump(matches, f, indent=2)
    print(f"\n📁 Saved {len(matches)} matches to backend/data_storage/matched_tds.json")

def main():
    """Main matching workflow"""
    print("\n" + "🔄" * 30)
    print("PRIZEPICKS EV FINDER - PROP MATCHING (PASSING TDs)")
    print("🔄" * 30)
    
    # Load data
    sportsbook_data, prizepicks_data = load_data()
    
    # Extract players from sportsbook (these are the only ones we care about!)
    sportsbook_players = extract_sportsbook_players(sportsbook_data)
    
    # Extract ONLY standard lines from PrizePicks
    prizepicks_standard_lines = extract_prizepicks_standard_lines(prizepicks_data)
    
    # Match them up
    matches = match_props(sportsbook_players, prizepicks_standard_lines)
    
    # Display results
    display_matches(matches)
    
    # Save to file
    if matches:
        save_matches(matches)
    
    print("\n" + "="*60)
    print("✅ MATCHING COMPLETE!")
    print("="*60)
    
    if matches:
        print("\nNext step: Calculate EV for these matched props")
    else:
        print("\n💡 Try running the data collection again - different games might have better matches")

if __name__ == "__main__":
    main()