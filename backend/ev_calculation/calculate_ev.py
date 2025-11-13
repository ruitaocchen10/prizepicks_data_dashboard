"""
Calculate Expected Value for matched props
Converts odds to implied probabilities and determines +EV opportunities
UPDATED FOR PASSING YARDS with line adjustment
"""
import json

# Breakeven percentages for each PrizePicks slip type (from your table)
BREAKEVEN_RATES = {
    '2_power': 57.74,
    '3_power': 58.48,
    '3_flex': 59.80,
    '4_power': 56.23,
    '4_flex': 56.89,
    '5_flex': 54.34,
    '6_flex': 54.34
}

# Probability slope for passing yards (2% per yard)
YARDS_PROBABILITY_SLOPE = 0.02  # 2% change in probability per yard difference

def odds_to_probability(odds):
    """
    Convert American odds to implied probability
    
    Args:
        odds (int): American odds (e.g., -110, +150)
    
    Returns:
        float: Implied probability as percentage (e.g., 52.38)
    """
    if odds < 0:
        # Negative odds: |odds| / (|odds| + 100)
        probability = abs(odds) / (abs(odds) + 100)
    else:
        # Positive odds: 100 / (odds + 100)
        probability = 100 / (odds + 100)
    
    return probability * 100  # Return as percentage

def get_reference_sportsbook_line(sportsbook_lines):
    """
    Extract reference sportsbook line with priority fallback
    Checks sportsbooks in order of reliability/popularity
    Returns the first one found
    
    Priority order:
    1. FanDuel (most popular)
    2. DraftKings (most popular)
    3. BetMGM (reliable)
    4. Caesars (reliable)
    5. BetRivers (backup)
    6. Any other available sportsbook
    
    Args:
        sportsbook_lines (dict): Dictionary of bookmaker lines
    
    Returns:
        tuple: (bookmaker_name, line_data) or (None, None) if not found
    """
    # Priority order - check these first
    priority_sportsbooks = [
        'FanDuel',
        'DraftKings', 
        'BetMGM',
        'Caesars',
        'BetRivers',
        'BetOnline.ag',
        'Bovada'
    ]
    
    # Check priority sportsbooks in order
    for sportsbook in priority_sportsbooks:
        if sportsbook in sportsbook_lines:
            return (sportsbook, sportsbook_lines[sportsbook])
    
    # If none of the priority sportsbooks found, use ANY available sportsbook
    if sportsbook_lines:
        first_available = next(iter(sportsbook_lines.items()))
        return first_available
    
    # No sportsbooks found at all
    return (None, None)

def adjust_probability_for_line_difference(sportsbook_probability, line_difference):
    """
    Adjust sportsbook probability to account for PrizePicks line difference
    Uses linear interpolation with 2% per yard slope
    
    Args:
        sportsbook_probability (float): Implied probability from sportsbook odds (for OVER)
        line_difference (float): Sportsbook line - PrizePicks line (can be positive or negative)
    
    Returns:
        tuple: (adjusted_over_probability, adjusted_under_probability, adjustment_amount)
    
    Example:
        Sportsbook: Over 237.5 at -110 (52.4% OVER probability)
        PrizePicks: 235.5
        Line difference: 237.5 - 235.5 = 2.0 yards
        
        PrizePicks line is 2 yards LOWER → easier to go OVER
        Adjustment: 2.0 * 0.02 = +4% 
        Adjusted OVER probability: 52.4% + 4% = 56.4%
    """
    # Calculate adjustment based on line difference
    # Positive line_difference means sportsbook line is higher (PrizePicks line is lower/easier to go over)
    # Negative line_difference means sportsbook line is lower (PrizePicks line is higher/easier to go under)
    adjustment = line_difference * YARDS_PROBABILITY_SLOPE * 100  # Convert to percentage
    
    # Adjust the OVER probability
    adjusted_over_probability = sportsbook_probability + adjustment
    
    # Cap probabilities between 5% and 95% (reasonable bounds)
    adjusted_over_probability = max(5.0, min(95.0, adjusted_over_probability))
    
    # Calculate corresponding UNDER probability
    adjusted_under_probability = 100 - adjusted_over_probability
    
    return adjusted_over_probability, adjusted_under_probability, adjustment

def calculate_prop_ev(match):
    """
    Calculate EV for a single prop
    
    Args:
        match (dict): Matched prop data
    
    Returns:
        dict: Enhanced prop data with EV calculations
    """
    # Get reference sportsbook line (checks all available in priority order)
    bookmaker_name, reference_data = get_reference_sportsbook_line(match['sportsbook']['lines'])
    
    if not reference_data:
        # No sportsbook data at all - can't calculate EV
        return {
            **match,
            'ev_analysis': {
                'status': 'no_reference_data',
                'message': 'No sportsbook lines available'
            }
        }
    
    reference_line = reference_data['line']
    reference_odds = reference_data['odds']
    prizepicks_line = match['prizepicks']['line']
    
    # Calculate implied probability from reference sportsbook odds (this is for OVER)
    sportsbook_over_probability = odds_to_probability(reference_odds)
    
    # Calculate line difference (Sportsbook - PrizePicks)
    # Positive = PrizePicks line is lower (better for OVER)
    # Negative = PrizePicks line is higher (better for UNDER)
    line_difference = reference_line - prizepicks_line
    
    # Adjust probabilities based on line difference
    adjusted_over_prob, adjusted_under_prob, probability_adjustment = adjust_probability_for_line_difference(
        sportsbook_over_probability, 
        line_difference
    )
    
    # Determine which side has better EV
    if adjusted_over_prob > adjusted_under_prob:
        better_side = 'over'
        implied_probability = adjusted_over_prob
    else:
        better_side = 'under'
        implied_probability = adjusted_under_prob
    
    # Determine risk level based on 2-pick breakeven (57.74%)
    breakeven_2pick = BREAKEVEN_RATES['2_power']
    
    if implied_probability >= 60:
        risk_level = 'low'
        risk_color = 'green'
        risk_label = 'Strong +EV'
    elif implied_probability >= breakeven_2pick:
        risk_level = 'medium'
        risk_color = 'lightgreen'
        risk_label = 'Slight Edge'
    elif implied_probability >= 55:
        risk_level = 'moderate'
        risk_color = 'yellow'
        risk_label = 'Marginal'
    elif implied_probability >= 50:
        risk_level = 'high'
        risk_color = 'orange'
        risk_label = 'Risky'
    else:
        risk_level = 'very_high'
        risk_color = 'red'
        risk_label = 'Very Risky'
    
    # Build EV analysis object
    ev_analysis = {
        'status': 'calculated',
        'bookmaker_used': bookmaker_name,
        'better_side': better_side,
        'implied_probability': round(implied_probability, 2),
        'adjusted_over_probability': round(adjusted_over_prob, 2),
        'adjusted_under_probability': round(adjusted_under_prob, 2),
        'reference_line': reference_line,
        'reference_odds': reference_odds,
        'sportsbook_over_probability': round(sportsbook_over_probability, 2),
        'line_difference': round(line_difference, 2),
        'probability_adjustment': round(probability_adjustment, 2),
        'yards_slope_used': YARDS_PROBABILITY_SLOPE,
        'risk_level': risk_level,
        'risk_color': risk_color,
        'risk_label': risk_label,
        'breakeven_2pick': breakeven_2pick,
        'edge_over_breakeven': round(implied_probability - breakeven_2pick, 2)
    }
    
    return {
        **match,
        'ev_analysis': ev_analysis
    }

def load_matched_props():
    """Load matched props from file"""
    print("\n" + "="*60)
    print("LOADING MATCHED PROPS")
    print("="*60)
    
    try:
        with open('backend/data_storage/matched_yards.json', 'r') as f:  # Changed filename
            matched_props = json.load(f)
        print(f"✅ Loaded {len(matched_props)} matched props")
        return matched_props
    except FileNotFoundError:
        print("❌ Error: matched_yards.json not found!")
        print("   Run match_props.py first to generate matched props")
        return None

def calculate_all_ev(matched_props):
    """Calculate EV for all matched props"""
    print("\n" + "="*60)
    print("CALCULATING EV FOR ALL PROPS")
    print("="*60)
    
    ev_props = []
    
    for match in matched_props:
        prop_with_ev = calculate_prop_ev(match)
        ev_props.append(prop_with_ev)
        
        # Print summary
        if prop_with_ev['ev_analysis']['status'] == 'calculated':
            ev = prop_with_ev['ev_analysis']
            print(f"\n✅ {match['player']}")
            print(f"   Best side: {ev['better_side'].upper()} {match['prizepicks']['line']} yards")  # Changed from TDs
            print(f"   Sportsbook line: {ev['reference_line']} yards at {ev['reference_odds']}")
            print(f"   Line difference: {ev['line_difference']} yards")
            print(f"   Probability adjustment: {ev['probability_adjustment']:+.2f}%")
            print(f"   Final probability: {ev['implied_probability']}%")
            print(f"   Risk: {ev['risk_label']} ({ev['risk_color']})")
            print(f"   Edge: {ev['edge_over_breakeven']:+.2f}% vs 2-pick breakeven")
        else:
            print(f"\n⚠️  {match['player']}: {prop_with_ev['ev_analysis']['message']}")
    
    return ev_props

def display_summary(ev_props):
    """Display summary of EV opportunities"""
    print("\n" + "="*60)
    print("EV OPPORTUNITIES SUMMARY")
    print("="*60)
    
    # Filter to only props with calculated EV
    calculated_props = [p for p in ev_props if p['ev_analysis']['status'] == 'calculated']
    
    if not calculated_props:
        print("\n❌ No props with calculated EV")
        return
    
    # Sort by implied probability (best first)
    sorted_props = sorted(calculated_props, key=lambda x: x['ev_analysis']['implied_probability'], reverse=True)
    
    print(f"\n🎯 Top +EV Opportunities:")
    print("-" * 60)
    
    for i, prop in enumerate(sorted_props[:10], 1):  # Top 10 (changed from 5)
        ev = prop['ev_analysis']
        print(f"{i}. {prop['player']} - {ev['better_side'].upper()} {prop['prizepicks']['line']} yards")
        print(f"   {ev['implied_probability']}% probability ({ev['risk_label']})")
        print(f"   Line diff: {ev['line_difference']:+.1f} yards | Prob adjustment: {ev['probability_adjustment']:+.2f}%")
        print(f"   Edge: {ev['edge_over_breakeven']:+.2f}% vs breakeven")
        print()
    
    # Show breakeven comparison
    print("\n📊 PrizePicks Breakeven Rates:")
    print("-" * 60)
    for slip_type, rate in BREAKEVEN_RATES.items():
        slip_name = slip_type.replace('_', ' ').title()
        print(f"   {slip_name}: {rate}%")
    
    # Count by risk level
    risk_counts = {}
    for prop in calculated_props:
        risk = prop['ev_analysis']['risk_label']
        risk_counts[risk] = risk_counts.get(risk, 0) + 1
    
    print("\n🎨 Risk Distribution:")
    print("-" * 60)
    for risk, count in sorted(risk_counts.items(), key=lambda x: x[1], reverse=True):
        print(f"   {risk}: {count} props")

def save_ev_analysis(ev_props):
    """Save EV analysis to file"""
    output_file = 'backend/data_storage/ev_analysis.json'
    
    with open(output_file, 'w') as f:
        json.dump(ev_props, f, indent=2)
    
    print(f"\n📁 Saved EV analysis to {output_file}")

def main():
    """Main EV calculation workflow"""
    print("\n" + "🎯" * 30)
    print("PRIZEPICKS EV CALCULATOR (PASSING YARDS)")
    print("🎯" * 30)
    
    # Load matched props
    matched_props = load_matched_props()
    if not matched_props:
        return
    
    # Calculate EV for all props
    ev_props = calculate_all_ev(matched_props)
    
    # Display summary
    display_summary(ev_props)
    
    # Save results
    save_ev_analysis(ev_props)
    
    print("\n" + "="*60)
    print("✅ EV CALCULATION COMPLETE!")
    print("="*60)
    print("\nNext step: Build React frontend to display ev_analysis.json")

if __name__ == "__main__":
    main()