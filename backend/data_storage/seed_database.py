"""
Seed PrizePicks User Dashboard Database with Realistic Mock Data

Generates:
- 500 users (70% casual, 24% regular, 5% winning sharps, 1% elite sharps)
- 200 real NFL players
- 50 NFL games (Weeks 9-11 of 2025 season)
- ~5,000 entries with varying bet sizes
- Individual picks for each entry
- Transaction history for all money movements
"""

import sqlite3
import os
import random
from datetime import datetime, timedelta
from decimal import Decimal

# File paths - relative to project root
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(os.path.dirname(SCRIPT_DIR))
DATA_STORAGE_DIR = os.path.join(PROJECT_ROOT, 'backend', 'data_storage')
DATABASE_FILE = os.path.join(DATA_STORAGE_DIR, 'user_data.db')

# ============================================================================
# CONFIGURATION
# ============================================================================

# User distribution
TOTAL_USERS = 500
CASUAL_PERCENT = 0.70    # 350 users
REGULAR_PERCENT = 0.24   # 120 users
SHARP_PERCENT = 0.05     # 25 users
ELITE_PERCENT = 0.01     # 5 users

# Entry ranges by user type
CASUAL_ENTRIES = (1, 5)
REGULAR_ENTRIES = (5, 15)
SHARP_ENTRIES = (20, 50)
ELITE_ENTRIES = (50, 100)

# Bet size ranges by user type
CASUAL_BET_SIZE = (5, 20)
REGULAR_BET_SIZE = (10, 50)
SHARP_BET_SIZE = (25, 100)
ELITE_BET_SIZE = (50, 200)

# Win rates by user type
CASUAL_WIN_RATE = 0.37
REGULAR_WIN_RATE = 0.42
SHARP_WIN_RATE = 0.51
ELITE_WIN_RATE = 0.58

# Date range for entries (last 30 days)
END_DATE = datetime(2025, 11, 12)  # Current date
START_DATE = END_DATE - timedelta(days=30)

# ============================================================================
# REAL NFL DATA
# ============================================================================

# Real NFL players with positions and teams (200 players)
NFL_PLAYERS = [
    # Quarterbacks
    ("Patrick Mahomes", "KC", "QB", "NFL"),
    ("Josh Allen", "BUF", "QB", "NFL"),
    ("Joe Burrow", "CIN", "QB", "NFL"),
    ("Lamar Jackson", "BAL", "QB", "NFL"),
    ("Jalen Hurts", "PHI", "QB", "NFL"),
    ("Dak Prescott", "DAL", "QB", "NFL"),
    ("Justin Herbert", "LAC", "QB", "NFL"),
    ("Trevor Lawrence", "JAX", "QB", "NFL"),
    ("Tua Tagovailoa", "MIA", "QB", "NFL"),
    ("Jordan Love", "GB", "QB", "NFL"),
    ("Brock Purdy", "SF", "QB", "NFL"),
    ("CJ Stroud", "HOU", "QB", "NFL"),
    ("Jared Goff", "DET", "QB", "NFL"),
    ("Kirk Cousins", "ATL", "QB", "NFL"),
    ("Geno Smith", "SEA", "QB", "NFL"),
    ("Baker Mayfield", "TB", "QB", "NFL"),
    ("Matthew Stafford", "LAR", "QB", "NFL"),
    ("Sam Darnold", "MIN", "QB", "NFL"),
    ("Caleb Williams", "CHI", "QB", "NFL"),
    ("Jayden Daniels", "WAS", "QB", "NFL"),
    ("Bo Nix", "DEN", "QB", "NFL"),
    ("Anthony Richardson", "IND", "QB", "NFL"),
    ("Spencer Rattler", "NO", "QB", "NFL"),
    ("Jaxson Dart", "NYG", "QB", "NFL"),
    ("Aaron Rodgers", "PIT", "QB", "NFL"),
    
    # Running Backs
    ("Christian McCaffrey", "SF", "RB", "NFL"),
    ("Saquon Barkley", "PHI", "RB", "NFL"),
    ("Derrick Henry", "BAL", "RB", "NFL"),
    ("Bijan Robinson", "ATL", "RB", "NFL"),
    ("Breece Hall", "NYJ", "RB", "NFL"),
    ("Jahmyr Gibbs", "DET", "RB", "NFL"),
    ("Jonathan Taylor", "IND", "RB", "NFL"),
    ("Josh Jacobs", "GB", "RB", "NFL"),
    ("Kenneth Walker III", "SEA", "RB", "NFL"),
    ("De'Von Achane", "MIA", "RB", "NFL"),
    ("Kyren Williams", "LAR", "RB", "NFL"),
    ("James Cook", "BUF", "RB", "NFL"),
    ("Rachaad White", "TB", "RB", "NFL"),
    ("Rhamondre Stevenson", "NE", "RB", "NFL"),
    ("Joe Mixon", "HOU", "RB", "NFL"),
    ("David Montgomery", "DET", "RB", "NFL"),
    ("Alvin Kamara", "NO", "RB", "NFL"),
    ("Tony Pollard", "TEN", "RB", "NFL"),
    ("Travis Etienne", "JAX", "RB", "NFL"),
    ("Najee Harris", "PIT", "RB", "NFL"),
    ("D'Andre Swift", "CHI", "RB", "NFL"),
    ("Javonte Williams", "DAL", "RB", "NFL"),
    ("Aaron Jones", "MIN", "RB", "NFL"),
    ("Isiah Pacheco", "KC", "RB", "NFL"),
    ("Chuba Hubbard", "CAR", "RB", "NFL"),
    
    # Wide Receivers
    ("Justin Jefferson", "MIN", "WR", "NFL"),
    ("Tyreek Hill", "MIA", "WR", "NFL"),
    ("Ja'Marr Chase", "CIN", "WR", "NFL"),
    ("CeeDee Lamb", "DAL", "WR", "NFL"),
    ("Amon-Ra St. Brown", "DET", "WR", "NFL"),
    ("AJ Brown", "PHI", "WR", "NFL"),
    ("Davante Adams", "LAR", "WR", "NFL"),
    ("Garrett Wilson", "NYJ", "WR", "NFL"),
    ("Puka Nacua", "LAR", "WR", "NFL"),
    ("Cooper Kupp", "SEA", "WR", "NFL"),
    ("Nico Collins", "HOU", "WR", "NFL"),
    ("DeVonta Smith", "PHI", "WR", "NFL"),
    ("DK Metcalf", "PIT", "WR", "NFL"),
    ("Chris Olave", "NO", "WR", "NFL"),
    ("Stefon Diggs", "NE", "WR", "NFL"),
    ("Deebo Samuel", "WAS", "WR", "NFL"),
    ("Keon Coleman", "BUF", "WR", "NFL"),
    ("Brandon Aiyuk", "SF", "WR", "NFL"),
    ("DJ Moore", "CHI", "WR", "NFL"),
    ("Terry McLaurin", "WAS", "WR", "NFL"),
    ("Mike Evans", "TB", "WR", "NFL"),
    ("Jaylen Waddle", "MIA", "WR", "NFL"),
    ("Calvin Ridley", "TEN", "WR", "NFL"),
    ("Christian Kirk", "HOU", "WR", "NFL"),
    ("Keenan Allen", "LAC", "WR", "NFL"),
    ("Drake London", "ATL", "WR", "NFL"),
    ("Zay Flowers", "BAL", "WR", "NFL"),
    ("George Pickens", "DAL", "WR", "NFL"),
    ("Jordan Addison", "MIN", "WR", "NFL"),
    ("Rashee Rice", "KC", "WR", "NFL"),
    ("DeAndre Hopkins", "BAL", "WR", "NFL"),
    ("Michael Pittman Jr", "IND", "WR", "NFL"),
    ("Courtland Sutton", "DEN", "WR", "NFL"),
    ("Rashod Bateman", "BAL", "WR", "NFL"),
    ("Jaxon Smith-Njigba", "SEA", "WR", "NFL"),
    ("Rome Odunze", "CHI", "WR", "NFL"),
    ("Marvin Harrison Jr", "ARI", "WR", "NFL"),
    ("Ladd McConkey", "LAC", "WR", "NFL"),
    ("Xavier Worthy", "KC", "WR", "NFL"),
    ("Brian Thomas Jr", "JAX", "WR", "NFL"),
    
    # Tight Ends
    ("Travis Kelce", "KC", "TE", "NFL"),
    ("Sam LaPorta", "DET", "TE", "NFL"),
    ("George Kittle", "SF", "TE", "NFL"),
    ("Trey McBride", "ARI", "TE", "NFL"),
    ("Mark Andrews", "BAL", "TE", "NFL"),
    ("TJ Hockenson", "MIN", "TE", "NFL"),
    ("Evan Engram", "DEN", "TE", "NFL"),
    ("David Njoku", "CLE", "TE", "NFL"),
    ("Kyle Pitts", "ATL", "TE", "NFL"),
    ("Dallas Goedert", "PHI", "TE", "NFL"),
    ("Dalton Kincaid", "BUF", "TE", "NFL"),
    ("Brock Bowers", "LV", "TE", "NFL"),
    ("Jake Ferguson", "DAL", "TE", "NFL"),
    ("Cole Kmet", "CHI", "TE", "NFL"),
    ("Pat Freiermuth", "PIT", "TE", "NFL"),
    
    # Additional skill position players to reach 200
    ("Zach Charbonnet", "SEA", "RB", "NFL"),
    ("Tyjae Spears", "TEN", "RB", "NFL"),
    ("Jaylen Warren", "PIT", "RB", "NFL"),
    ("Khalil Herbert", "CIN", "RB", "NFL"),
    ("Jerome Ford", "CLE", "RB", "NFL"),
    ("Tyler Allgeier", "ATL", "RB", "NFL"),
    ("Roschon Johnson", "CHI", "RB", "NFL"),
    ("Justice Hill", "BAL", "RB", "NFL"),
    ("Ty Chandler", "MIN", "RB", "NFL"),
    ("Rico Dowdle", "CAR", "RB", "NFL"),
    ("Kimani Vidal", "LAC", "RB", "NFL"),
    ("Alexander Mattison", "LV", "RB", "NFL"),
    ("Dameon Pierce", "HOU", "RB", "NFL"),
    ("Zamir White", "LV", "RB", "NFL"),
    ("Kareem Hunt", "KC", "RB", "NFL"),
    ("Miles Sanders", "CAR", "RB", "NFL"),
    ("Tank Bigsby", "PHI", "RB", "NFL"),
    ("Audric Estime", "DEN", "RB", "NFL"),
    ("Braelon Allen", "NYJ", "RB", "NFL"),
    ("Blake Corum", "LAR", "RB", "NFL"),
    ("Tyler Lockett", "SEA", "WR", "NFL"),
    ("Quentin Johnston", "LAC", "WR", "NFL"),
    ("Josh Downs", "IND", "WR", "NFL"),
    ("Tank Dell", "HOU", "WR", "NFL"),
    ("Wan'Dale Robinson", "NYG", "WR", "NFL"),
    ("Dontayvion Wicks", "GB", "WR", "NFL"),
    ("Romeo Doubs", "GB", "WR", "NFL"),
    ("Curtis Samuel", "BUF", "WR", "NFL"),
    ("Jakobi Meyers", "LV", "WR", "NFL"),
    ("Demarcus Robinson", "LAR", "WR", "NFL"),
    ("Jauan Jennings", "SF", "WR", "NFL"),
    ("Jameson Williams", "DET", "WR", "NFL"),
    ("Rashid Shaheed", "NO", "WR", "NFL"),
    ("Jalen Tolbert", "DAL", "WR", "NFL"),
    ("Elijah Moore", "CLE", "WR", "NFL"),
    ("Josh Palmer", "LAC", "WR", "NFL"),
    ("Darnell Mooney", "ATL", "WR", "NFL"),
    ("Adam Thielen", "MIN", "WR", "NFL"),
    ("Noah Brown", "WAS", "WR", "NFL"),
    ("Ricky Pearsall", "SF", "WR", "NFL"),
    ("Khalil Shakir", "BUF", "WR", "NFL"),
    ("Adonai Mitchell", "NYJ", "WR", "NFL"),
    ("Malik Nabers", "NYG", "WR", "NFL"),
    ("Xavier Legette", "CAR", "WR", "NFL"),
    ("Dalton Schultz", "HOU", "TE", "NFL"),
    ("Jonnu Smith", "PIT", "TE", "NFL"),
    ("Hunter Henry", "NE", "TE", "NFL"),
    ("Chigoziem Okonkwo", "TEN", "TE", "NFL"),
    ("Tyler Conklin", "NYJ", "TE", "NFL"),
    ("Zach Ertz", "WAS", "TE", "NFL"),
    ("Isaiah Likely", "BAL", "TE", "NFL"),
    ("Luke Musgrave", "GB", "TE", "NFL"),
    ("Cade Otton", "TB", "TE", "NFL"),
    ("Tucker Kraft", "GB", "TE", "NFL"),
    ("Theo Johnson", "NYG", "TE", "NFL"),
    ("Noah Fant", "SEA", "TE", "NFL"),
    ("Ja'Tavion Sanders", "CAR", "TE", "NFL"),
    ("Mike Gesicki", "CIN", "TE", "NFL"),
    ("Will Dissly", "LAC", "TE", "NFL"),
]

# Real NFL matchups for Weeks 9-11 (2025 season)
# Format: (home_team, away_team, game_date, status, home_score, away_score)
NFL_GAMES = [
    # Week 9 (completed - Nov 3-4, 2025)
    ("KC", "TB", datetime(2025, 11, 4, 20, 15), "final", 30, 24),
    ("BUF", "MIA", datetime(2025, 11, 3, 13, 0), "final", 30, 27),
    ("MIN", "IND", datetime(2025, 11, 3, 20, 20), "final", 21, 13),
    ("DET", "GB", datetime(2025, 11, 3, 16, 25), "final", 24, 14),
    ("PHI", "JAX", datetime(2025, 11, 3, 16, 25), "final", 28, 23),
    ("LAR", "SEA", datetime(2025, 11, 3, 16, 5), "final", 26, 20),
    ("BAL", "DEN", datetime(2025, 11, 3, 13, 0), "final", 41, 10),
    ("CIN", "LV", datetime(2025, 11, 3, 13, 0), "final", 41, 24),
    ("ATL", "DAL", datetime(2025, 11, 3, 13, 0), "final", 27, 21),
    ("NO", "CAR", datetime(2025, 11, 3, 13, 0), "final", 23, 22),
    ("LAC", "CLE", datetime(2025, 11, 3, 13, 0), "final", 27, 10),
    ("NE", "TEN", datetime(2025, 11, 3, 13, 0), "final", 20, 17),
    ("CHI", "ARI", datetime(2025, 11, 3, 16, 5), "final", 29, 9),
    ("WAS", "NYG", datetime(2025, 11, 3, 13, 0), "final", 27, 22),
    
    # Week 10 (completed - Nov 10-11, 2025)
    ("BAL", "CIN", datetime(2025, 11, 7, 20, 15), "final", 35, 34),
    ("SF", "TB", datetime(2025, 11, 10, 13, 0), "final", 23, 20),
    ("PIT", "WAS", datetime(2025, 11, 10, 13, 0), "final", 28, 27),
    ("BUF", "IND", datetime(2025, 11, 10, 13, 0), "final", 30, 20),
    ("MIN", "JAX", datetime(2025, 11, 10, 13, 0), "final", 12, 7),
    ("DEN", "KC", datetime(2025, 11, 10, 13, 0), "final", 16, 14),
    ("ATL", "NO", datetime(2025, 11, 10, 13, 0), "final", 20, 17),
    ("TEN", "LAC", datetime(2025, 11, 10, 16, 5), "final", 27, 17),
    ("NYJ", "ARI", datetime(2025, 11, 10, 16, 25), "final", 31, 6),
    ("PHI", "DAL", datetime(2025, 11, 10, 16, 25), "final", 34, 6),
    ("DET", "HOU", datetime(2025, 11, 10, 20, 20), "final", 26, 23),
    ("MIA", "LAR", datetime(2025, 11, 11, 20, 15), "final", 23, 15),
    
    # Week 11 (upcoming - Nov 14-18, 2025)
    ("PHI", "WAS", datetime(2025, 11, 14, 20, 15), "scheduled", None, None),
    ("CLE", "NO", datetime(2025, 11, 17, 13, 0), "scheduled", None, None),
    ("JAX", "DET", datetime(2025, 11, 17, 13, 0), "scheduled", None, None),
    ("LV", "MIA", datetime(2025, 11, 17, 13, 0), "scheduled", None, None),
    ("LAR", "NE", datetime(2025, 11, 17, 13, 0), "scheduled", None, None),
    ("MIN", "TEN", datetime(2025, 11, 17, 13, 0), "scheduled", None, None),
    ("ATL", "DEN", datetime(2025, 11, 17, 16, 5), "scheduled", None, None),
    ("SEA", "SF", datetime(2025, 11, 17, 16, 5), "scheduled", None, None),
    ("KC", "BUF", datetime(2025, 11, 17, 16, 25), "scheduled", None, None),
    ("IND", "NYJ", datetime(2025, 11, 17, 20, 20), "scheduled", None, None),
    ("BAL", "PIT", datetime(2025, 11, 17, 13, 0), "scheduled", None, None),
    ("LAC", "CIN", datetime(2025, 11, 17, 20, 20), "scheduled", None, None),
    ("GB", "CHI", datetime(2025, 11, 17, 13, 0), "scheduled", None, None),
    ("DAL", "HOU", datetime(2025, 11, 18, 20, 15), "scheduled", None, None),
]

# US States where sports betting is legal (for user locations)
LEGAL_STATES = [
    "AZ", "CO", "CT", "IL", "IN", "IA", "KS", "KY", "LA", "ME",
    "MD", "MA", "MI", "NV", "NH", "NJ", "NY", "NC", "OH", "OR",
    "PA", "RI", "TN", "VA", "WV", "WY", "DC"
]

# First and last names for generating realistic users
FIRST_NAMES = [
    "James", "John", "Robert", "Michael", "William", "David", "Richard", "Joseph",
    "Thomas", "Christopher", "Daniel", "Matthew", "Anthony", "Mark", "Donald", "Steven",
    "Andrew", "Paul", "Joshua", "Kenneth", "Kevin", "Brian", "George", "Timothy",
    "Ronald", "Edward", "Jason", "Jeffrey", "Ryan", "Jacob", "Nicholas", "Eric",
    "Jonathan", "Stephen", "Larry", "Justin", "Scott", "Brandon", "Benjamin", "Samuel",
    "Mary", "Patricia", "Jennifer", "Linda", "Barbara", "Elizabeth", "Susan", "Jessica",
    "Sarah", "Karen", "Lisa", "Nancy", "Betty", "Margaret", "Sandra", "Ashley",
    "Kimberly", "Emily", "Donna", "Michelle", "Carol", "Amanda", "Dorothy", "Melissa",
    "Deborah", "Stephanie", "Rebecca", "Sharon", "Laura", "Cynthia", "Amy", "Kathleen",
    "Angela", "Shirley", "Anna", "Brenda", "Pamela", "Emma", "Nicole", "Helen"
]

LAST_NAMES = [
    "Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia", "Miller", "Davis",
    "Rodriguez", "Martinez", "Hernandez", "Lopez", "Gonzalez", "Wilson", "Anderson", "Thomas",
    "Taylor", "Moore", "Jackson", "Martin", "Lee", "Thompson", "White", "Harris",
    "Sanchez", "Clark", "Ramirez", "Lewis", "Robinson", "Walker", "Young", "Allen",
    "King", "Wright", "Scott", "Torres", "Nguyen", "Hill", "Flores", "Green",
    "Adams", "Nelson", "Baker", "Hall", "Rivera", "Campbell", "Mitchell", "Carter",
    "Roberts", "Gomez", "Phillips", "Evans", "Turner", "Diaz", "Parker", "Cruz"
]

# Stat types for different positions
STAT_TYPES = {
    "QB": ["Passing Yards", "Passing TDs", "Completions", "Pass Attempts", "Interceptions"],
    "RB": ["Rushing Yards", "Rushing TDs", "Receptions", "Receiving Yards", "Total Yards"],
    "WR": ["Receiving Yards", "Receptions", "Receiving TDs", "Targets", "Longest Reception"],
    "TE": ["Receiving Yards", "Receptions", "Receiving TDs", "Targets", "Longest Reception"],
}

# PrizePicks payout multipliers based on number of picks
PAYOUT_MULTIPLIERS = {
    2: 3.0,    # 2-pick: 3x payout
    3: 5.0,    # 3-pick: 5x payout
    4: 10.0,   # 4-pick: 10x payout
    5: 20.0,   # 5-pick: 20x payout
    6: 40.0,   # 6-pick: 40x payout
}

# Entry types with probability distribution
ENTRY_TYPES = [
    ("standard", 0.70),  # 70% standard entries
    ("flex", 0.20),      # 20% flex (one pick can miss)
    ("power", 0.08),     # 8% power plays
    ("goblin", 0.02),    # 2% goblin mode (high risk)
]

# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def random_date_between(start, end):
    """Generate random datetime between start and end dates"""
    # Handle edge case where start >= end
    if start >= end:
        return end
    
    delta = end - start
    random_days = random.randint(0, delta.days)
    random_seconds = random.randint(0, 86400)
    return start + timedelta(days=random_days, seconds=random_seconds)

def generate_username(first_name, last_name):
    """Generate realistic username variations"""
    variations = [
        f"{first_name.lower()}{last_name.lower()}",
        f"{first_name.lower()}.{last_name.lower()}",
        f"{first_name[0].lower()}{last_name.lower()}",
        f"{first_name.lower()}{last_name.lower()}{random.randint(1, 999)}",
        f"{first_name.lower()}_{last_name.lower()}",
        f"{last_name.lower()}{first_name[0].lower()}",
    ]
    return random.choice(variations)

def generate_email(username):
    """Generate email address"""
    domains = ["gmail.com", "yahoo.com", "hotmail.com", "outlook.com", "icloud.com", "aol.com"]
    return f"{username}@{random.choice(domains)}"

def generate_phone():
    """Generate fake phone number"""
    area_code = random.randint(200, 999)
    prefix = random.randint(200, 999)
    line = random.randint(1000, 9999)
    return f"{area_code}-{prefix}-{line}"

def get_user_tier_params(tier):
    """Get parameters for different user tiers"""
    if tier == "casual":
        return {
            "entries": CASUAL_ENTRIES,
            "bet_size": CASUAL_BET_SIZE,
            "win_rate": CASUAL_WIN_RATE,
            "initial_deposit": (50, 200),
        }
    elif tier == "regular":
        return {
            "entries": REGULAR_ENTRIES,
            "bet_size": REGULAR_BET_SIZE,
            "win_rate": REGULAR_WIN_RATE,
            "initial_deposit": (200, 500),
        }
    elif tier == "sharp":
        return {
            "entries": SHARP_ENTRIES,
            "bet_size": SHARP_BET_SIZE,
            "win_rate": SHARP_WIN_RATE,
            "initial_deposit": (500, 2000),
        }
    else:  # elite
        return {
            "entries": ELITE_ENTRIES,
            "bet_size": ELITE_BET_SIZE,
            "win_rate": ELITE_WIN_RATE,
            "initial_deposit": (2000, 5000),
        }

def weighted_choice(choices):
    """Select item based on probability weights"""
    items, probabilities = zip(*choices)
    return random.choices(items, weights=probabilities, k=1)[0]

def generate_line_for_stat(stat_type, position):
    """Generate realistic prop line for a stat"""
    line_ranges = {
        "Passing Yards": (220.5, 285.5),
        "Passing TDs": (1.5, 2.5),
        "Completions": (19.5, 28.5),
        "Pass Attempts": (30.5, 39.5),
        "Interceptions": (0.5, 1.5),
        "Rushing Yards": (55.5, 95.5),
        "Rushing TDs": (0.5, 1.5),
        "Receiving Yards": (45.5, 85.5),
        "Receptions": (4.5, 7.5),
        "Receiving TDs": (0.5, 1.5),
        "Targets": (5.5, 9.5),
        "Longest Reception": (18.5, 28.5),
        "Total Yards": (70.5, 110.5),
    }
    
    min_line, max_line = line_ranges.get(stat_type, (50.5, 100.5))
    # Generate line in 0.5 increments
    line = random.choice([x + 0.5 for x in range(int(min_line), int(max_line))])
    return line

def simulate_pick_result(win_rate, entry_status):
    """Simulate whether a pick hit or missed based on win rate"""
    if entry_status == "pending":
        return "pending"
    elif entry_status == "cancelled":
        return "void"
    else:
        # Small chance of push (0.5 on exact number)
        if random.random() < 0.05:
            return "push"
        return "hit" if random.random() < win_rate else "miss"

# ============================================================================
# DATA GENERATION FUNCTIONS
# ============================================================================

def seed_players(cursor):
    """Insert NFL players into database"""
    print("\n📊 Generating 200 NFL players...")
    
    for player_name, team, position, sport in NFL_PLAYERS:
        cursor.execute("""
            INSERT INTO players (player_name, team, position, sport, jersey_number, is_active)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (player_name, team, position, sport, random.randint(1, 99), 1))
    
    print(f"✅ Created {len(NFL_PLAYERS)} NFL players")

def seed_games(cursor):
    """Insert NFL games into database"""
    print("\n🏈 Generating 50 NFL games (Weeks 9-11)...")
    
    for home, away, game_date, status, home_score, away_score in NFL_GAMES:
        cursor.execute("""
            INSERT INTO games (sport, league, home_team, away_team, game_date, venue, status, home_score, away_score)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, ("NFL", "NFL", home, away, game_date, f"{home} Stadium", status, home_score, away_score))
    
    print(f"✅ Created {len(NFL_GAMES)} NFL games")

def seed_users_and_wallets(cursor):
    """Generate 500 users with proper tier distribution"""
    print("\n👥 Generating 500 users across 4 tiers...")
    
    # Determine user tiers
    user_tiers = (
        ["casual"] * int(TOTAL_USERS * CASUAL_PERCENT) +
        ["regular"] * int(TOTAL_USERS * REGULAR_PERCENT) +
        ["sharp"] * int(TOTAL_USERS * SHARP_PERCENT) +
        ["elite"] * int(TOTAL_USERS * ELITE_PERCENT)
    )
    
    # Adjust to exactly 500
    while len(user_tiers) < TOTAL_USERS:
        user_tiers.append("casual")
    user_tiers = user_tiers[:TOTAL_USERS]
    
    random.shuffle(user_tiers)
    
    tier_counts = {"casual": 0, "regular": 0, "sharp": 0, "elite": 0}
    
    used_usernames = set()
    used_emails = set()
    
    for i, tier in enumerate(user_tiers):
        tier_counts[tier] += 1
        
        # Generate unique username and email
        while True:
            first_name = random.choice(FIRST_NAMES)
            last_name = random.choice(LAST_NAMES)
            username = generate_username(first_name, last_name)
            email = generate_email(username)
            
            if username not in used_usernames and email not in used_emails:
                used_usernames.add(username)
                used_emails.add(email)
                break
        
        # User creation date (some recent, some older)
        # Ensure created_at is before END_DATE
        user_start = START_DATE - timedelta(days=365)
        user_end = END_DATE - timedelta(days=1)  # At least 1 day before END_DATE
        created_at = random_date_between(user_start, user_end)
        last_login = random_date_between(created_at, END_DATE)
        
        # Account status (elite sharps might be suspended!)
        if tier == "elite" and random.random() < 0.4:
            account_status = "suspended"
        else:
            account_status = "active"
        
        # Insert user
        cursor.execute("""
            INSERT INTO users (username, email, first_name, last_name, state, date_of_birth, 
                             created_at, last_login, account_status, kyc_verified, phone_number)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            username, email, first_name, last_name, random.choice(LEGAL_STATES),
            datetime(random.randint(1970, 2000), random.randint(1, 12), random.randint(1, 28)),
            created_at, last_login, account_status, 1, generate_phone()
        ))
        
        user_id = cursor.lastrowid
        
        # Create wallet for user (will be updated later with actual totals)
        cursor.execute("""
            INSERT INTO wallets (user_id, current_balance, total_deposits, total_withdrawals, 
                               total_winnings, total_wagered)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (user_id, 0, 0, 0, 0, 0))
    
    print(f"✅ Created 500 users:")
    print(f"   - Casual: {tier_counts['casual']} users")
    print(f"   - Regular: {tier_counts['regular']} users")
    print(f"   - Sharp: {tier_counts['sharp']} users")
    print(f"   - Elite: {tier_counts['elite']} users")
    
    return user_tiers

def seed_entries_and_picks(cursor, user_tiers):
    """Generate entries and picks for each user"""
    print("\n🎲 Generating entries and picks for all users...")
    
    # Get all players and games
    cursor.execute("SELECT player_id, player_name, position, team FROM players WHERE is_active = 1")
    players = cursor.fetchall()
    
    cursor.execute("SELECT game_id, home_team, away_team, game_date, status FROM games")
    games = cursor.fetchall()
    
    # Create lookup for games by teams
    # Convert game_date strings back to datetime objects
    games_by_team = {}
    for game_id, home, away, game_date_str, status in games:
        # Convert string to datetime if needed
        if isinstance(game_date_str, str):
            game_date = datetime.fromisoformat(game_date_str.replace('Z', '+00:00'))
        else:
            game_date = game_date_str
        games_by_team.setdefault(home, []).append((game_id, game_date, status))
        games_by_team.setdefault(away, []).append((game_id, game_date, status))
    
    total_entries = 0
    total_picks = 0
    
    # Get all users
    cursor.execute("SELECT user_id FROM users")
    users = cursor.fetchall()
    
    for idx, (user_id,) in enumerate(users):
        tier = user_tiers[idx]
        params = get_user_tier_params(tier)
        
        # Determine number of entries for this user
        num_entries = random.randint(*params["entries"])
        
        user_total_deposits = 0
        user_total_wagered = 0
        user_total_winnings = 0
        user_transactions = []
        
        # Initial deposit
        initial_deposit = random.uniform(*params["initial_deposit"])
        user_total_deposits = initial_deposit
        user_balance = initial_deposit
        
        # Record deposit transaction
        user_transactions.append({
            "user_id": user_id,
            "type": "deposit",
            "amount": initial_deposit,
            "balance_before": 0,
            "balance_after": user_balance,
            "date": random_date_between(START_DATE - timedelta(days=30), START_DATE),
            "payment_method": random.choice(["credit_card", "paypal", "venmo", "bank_transfer"]),
        })
        
        for _ in range(num_entries):
            # Entry amount
            bet_size = random.uniform(*params["bet_size"])
            bet_size = round(bet_size, 2)
            
            # Make sure user has enough balance (add deposit if needed)
            if user_balance < bet_size:
                additional_deposit = random.uniform(bet_size * 2, bet_size * 5)
                user_total_deposits += additional_deposit
                balance_before = user_balance
                user_balance += additional_deposit
                user_transactions.append({
                    "user_id": user_id,
                    "type": "deposit",
                    "amount": additional_deposit,
                    "balance_before": balance_before,
                    "balance_after": user_balance,
                    "date": random_date_between(START_DATE, END_DATE),
                    "payment_method": random.choice(["credit_card", "paypal", "venmo"]),
                })
            
            # Number of picks (2-6)
            num_picks = random.choices([2, 3, 4, 5, 6], weights=[0.35, 0.35, 0.15, 0.10, 0.05], k=1)[0]
            
            # Entry type
            entry_type = weighted_choice(ENTRY_TYPES)
            
            # Potential payout
            multiplier = PAYOUT_MULTIPLIERS[num_picks]
            potential_payout = round(bet_size * multiplier, 2)
            
            # Entry creation time
            entry_date = random_date_between(START_DATE, END_DATE)
            
            # Determine if entry is settled or pending based on latest pick's game
            # For simplicity, we'll determine this after creating picks
            
            # Insert entry (initially pending)
            cursor.execute("""
                INSERT INTO entries (user_id, entry_amount, potential_payout, num_picks, 
                                   entry_type, status, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (user_id, bet_size, potential_payout, num_picks, entry_type, "pending", entry_date))
            
            entry_id = cursor.lastrowid
            total_entries += 1
            
            # Deduct bet from balance
            balance_before = user_balance
            user_balance -= bet_size
            user_total_wagered += bet_size
            
            # Record bet transaction
            user_transactions.append({
                "user_id": user_id,
                "type": "bet_placed",
                "amount": bet_size,
                "balance_before": balance_before,
                "balance_after": user_balance,
                "related_entry_id": entry_id,
                "date": entry_date,
            })
            
            # Create picks for this entry
            selected_players = random.sample(players, num_picks)
            pick_results = []
            latest_game_date = entry_date
            all_games_final = True
            
            for player_id, player_name, position, team in selected_players:
                # Find a game for this player's team
                team_games = games_by_team.get(team, [])
                if not team_games:
                    # Use a random game as fallback - need to convert all games too
                    all_games_converted = []
                    for g in games:
                        gid, home, away, gdate_str, gstatus = g
                        if isinstance(gdate_str, str):
                            gdate = datetime.fromisoformat(gdate_str.replace('Z', '+00:00'))
                        else:
                            gdate = gdate_str
                        all_games_converted.append((gid, gdate, gstatus))
                    game_id, game_date, game_status = random.choice(all_games_converted)
                else:
                    # Pick a game that's after entry date
                    valid_games = [(gid, gdate, gstatus) for gid, gdate, gstatus in team_games if gdate >= entry_date]
                    if not valid_games:
                        valid_games = team_games
                    game_id, game_date, game_status = random.choice(valid_games)
                
                # Track latest game date
                if game_date > latest_game_date:
                    latest_game_date = game_date
                
                if game_status != "final":
                    all_games_final = False
                
                # Select stat type based on position
                stat_options = STAT_TYPES.get(position, ["Receiving Yards"])
                stat_type = random.choice(stat_options)
                
                # Generate line
                line = generate_line_for_stat(stat_type, position)
                
                # Over or under
                selection = random.choice(["over", "under"])
                
                # Insert pick (initially pending)
                cursor.execute("""
                    INSERT INTO picks (entry_id, player_id, game_id, stat_type, line, selection, 
                                     result, created_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, (entry_id, player_id, game_id, stat_type, line, selection, "pending", entry_date))
                
                total_picks += 1
                pick_results.append(("pending", player_name, stat_type, line, selection))
            
            # Determine entry status based on games
            if all_games_final:
                # Simulate results based on user's win rate
                win_rate = params["win_rate"]
                entry_won = random.random() < win_rate
                
                if entry_won:
                    entry_status = "won"
                    actual_payout = potential_payout
                    user_balance += actual_payout
                    user_total_winnings += actual_payout
                    
                    # Update picks to "hit"
                    cursor.execute("SELECT pick_id FROM picks WHERE entry_id = ?", (entry_id,))
                    for (pick_id,) in cursor.fetchall():
                        cursor.execute("UPDATE picks SET result = ? WHERE pick_id = ?", ("hit", pick_id))
                    
                    # Record payout transaction
                    balance_before = user_balance - actual_payout
                    user_transactions.append({
                        "user_id": user_id,
                        "type": "payout",
                        "amount": actual_payout,
                        "balance_before": balance_before,
                        "balance_after": user_balance,
                        "related_entry_id": entry_id,
                        "date": latest_game_date + timedelta(hours=3),
                    })
                else:
                    entry_status = "lost"
                    actual_payout = 0
                    
                    # Update some picks to "miss"
                    cursor.execute("SELECT pick_id FROM picks WHERE entry_id = ?", (entry_id,))
                    all_picks = cursor.fetchall()
                    # At least one pick must miss for entry to lose
                    num_misses = random.randint(1, len(all_picks))
                    missed_picks = random.sample(all_picks, num_misses)
                    
                    for (pick_id,) in all_picks:
                        if (pick_id,) in missed_picks:
                            cursor.execute("UPDATE picks SET result = ? WHERE pick_id = ?", ("miss", pick_id))
                        else:
                            cursor.execute("UPDATE picks SET result = ? WHERE pick_id = ?", ("hit", pick_id))
                
                # Update entry with final status
                settled_at = latest_game_date + timedelta(hours=3)
                cursor.execute("""
                    UPDATE entries 
                    SET status = ?, actual_payout = ?, settled_at = ?
                    WHERE entry_id = ?
                """, (entry_status, actual_payout, settled_at, entry_id))
            else:
                # Entry is still pending
                cursor.execute("UPDATE entries SET status = ? WHERE entry_id = ?", ("pending", entry_id))
        
        # Update user's wallet with final totals
        cursor.execute("""
            UPDATE wallets 
            SET current_balance = ?, total_deposits = ?, total_wagered = ?, total_winnings = ?
            WHERE user_id = ?
        """, (round(user_balance, 2), round(user_total_deposits, 2), 
              round(user_total_wagered, 2), round(user_total_winnings, 2), user_id))
        
        # Insert all transactions
        for trans in user_transactions:
            cursor.execute("""
                INSERT INTO transactions (user_id, transaction_type, amount, balance_before, 
                                        balance_after, related_entry_id, status, payment_method, 
                                        transaction_date)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                trans["user_id"], trans["type"], round(trans["amount"], 2),
                round(trans["balance_before"], 2), round(trans["balance_after"], 2),
                trans.get("related_entry_id"), "completed", trans.get("payment_method"),
                trans["date"]
            ))
    
    print(f"✅ Created {total_entries} entries with {total_picks} total picks")

# ============================================================================
# MAIN SEED FUNCTION
# ============================================================================

def seed_database():
    """Main function to seed all data"""
    print("=" * 60)
    print("🌱 SEEDING PRIZEPICKS USER DATABASE")
    print("=" * 60)
    
    if not os.path.exists(DATABASE_FILE):
        print(f"❌ ERROR: Database not found at {DATABASE_FILE}")
        print("Run init_database.py first to create the database structure")
        return False
    
    try:
        conn = sqlite3.connect(DATABASE_FILE)
        cursor = conn.cursor()
        
        # Check if database already has data
        cursor.execute("SELECT COUNT(*) FROM users")
        user_count = cursor.fetchone()[0]
        
        if user_count > 0:
            print(f"⚠️  WARNING: Database already contains {user_count} users")
            response = input("Do you want to DELETE all data and reseed? (yes/no): ").strip().lower()
            if response != 'yes':
                print("❌ Seeding cancelled")
                conn.close()
                return False
            
            # Clear all tables
            print("🗑️  Clearing existing data...")
            cursor.execute("DELETE FROM transactions")
            cursor.execute("DELETE FROM picks")
            cursor.execute("DELETE FROM entries")
            cursor.execute("DELETE FROM games")
            cursor.execute("DELETE FROM players")
            cursor.execute("DELETE FROM wallets")
            cursor.execute("DELETE FROM users")
            conn.commit()
            print("✅ All tables cleared")
        
        # Seed data in order (respecting foreign keys)
        seed_players(cursor)
        seed_games(cursor)
        user_tiers = seed_users_and_wallets(cursor)
        seed_entries_and_picks(cursor, user_tiers)
        
        # Commit all changes
        conn.commit()
        
        # Display summary
        print("\n" + "=" * 60)
        print("📊 SEEDING COMPLETE - DATABASE SUMMARY")
        print("=" * 60)
        
        cursor.execute("SELECT COUNT(*) FROM users")
        print(f"👥 Users: {cursor.fetchone()[0]}")
        
        cursor.execute("SELECT COUNT(*) FROM wallets")
        print(f"💰 Wallets: {cursor.fetchone()[0]}")
        
        cursor.execute("SELECT COUNT(*) FROM players")
        print(f"🏈 Players: {cursor.fetchone()[0]}")
        
        cursor.execute("SELECT COUNT(*) FROM games")
        print(f"🎮 Games: {cursor.fetchone()[0]}")
        
        cursor.execute("SELECT COUNT(*) FROM entries")
        print(f"🎲 Entries: {cursor.fetchone()[0]}")
        
        cursor.execute("SELECT COUNT(*) FROM picks")
        print(f"🎯 Picks: {cursor.fetchone()[0]}")
        
        cursor.execute("SELECT COUNT(*) FROM transactions")
        print(f"💳 Transactions: {cursor.fetchone()[0]}")
        
        # Show some stats
        cursor.execute("SELECT SUM(total_deposits) FROM wallets")
        total_deposits = cursor.fetchone()[0] or 0
        print(f"\n💵 Total Deposits: ${total_deposits:,.2f}")
        
        cursor.execute("SELECT SUM(total_wagered) FROM wallets")
        total_wagered = cursor.fetchone()[0] or 0
        print(f"🎰 Total Wagered: ${total_wagered:,.2f}")
        
        cursor.execute("SELECT SUM(total_winnings) FROM wallets")
        total_winnings = cursor.fetchone()[0] or 0
        print(f"🏆 Total Winnings: ${total_winnings:,.2f}")
        
        cursor.execute("SELECT SUM(current_balance) FROM wallets")
        total_balance = cursor.fetchone()[0] or 0
        print(f"💰 Total User Balance: ${total_balance:,.2f}")
        
        house_profit = total_wagered - total_winnings
        print(f"🏠 House Profit: ${house_profit:,.2f}")
        
        cursor.execute("SELECT COUNT(*) FROM entries WHERE status = 'won'")
        won = cursor.fetchone()[0]
        cursor.execute("SELECT COUNT(*) FROM entries WHERE status = 'lost'")
        lost = cursor.fetchone()[0]
        if won + lost > 0:
            actual_win_rate = won / (won + lost) * 100
            print(f"📈 Actual Win Rate: {actual_win_rate:.1f}%")
        
        print("\n" + "=" * 60)
        print("🎉 DATABASE READY FOR QUERIES!")
        print("=" * 60)
        print("\nNext step: Create Flask API endpoints to query this data")
        
        conn.close()
        return True
        
    except sqlite3.Error as e:
        print(f"\n❌ DATABASE ERROR: {e}")
        return False
    except Exception as e:
        print(f"\n❌ UNEXPECTED ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = seed_database()
    
    if success:
        print("\n✨ Run your Flask API server to start querying the data!")
    else:
        print("\n⚠️  Seeding failed. Please check the errors above.")