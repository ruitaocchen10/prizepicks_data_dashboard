-- PrizePicks User Dashboard Database Schema
-- SQLite Database Structure

-- ============================================================================
-- USERS TABLE
-- Stores basic user account information
-- ============================================================================
CREATE TABLE IF NOT EXISTS users (
    user_id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT NOT NULL UNIQUE,
    email TEXT NOT NULL UNIQUE,
    first_name TEXT,
    last_name TEXT,
    state TEXT NOT NULL,  -- Important for legal/regulatory compliance
    date_of_birth DATE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_login TIMESTAMP,
    account_status TEXT DEFAULT 'active' CHECK(account_status IN ('active', 'suspended', 'closed', 'pending_verification')),
    kyc_verified BOOLEAN DEFAULT 0,  -- Know Your Customer verification
    phone_number TEXT,
    referral_code TEXT UNIQUE
);

-- ============================================================================
-- WALLETS TABLE
-- Tracks user account balances and lifetime totals
-- ============================================================================
CREATE TABLE IF NOT EXISTS wallets (
    wallet_id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL UNIQUE,
    current_balance DECIMAL(10, 2) DEFAULT 0.00 CHECK(current_balance >= 0),
    total_deposits DECIMAL(10, 2) DEFAULT 0.00,
    total_withdrawals DECIMAL(10, 2) DEFAULT 0.00,
    total_winnings DECIMAL(10, 2) DEFAULT 0.00,
    total_wagered DECIMAL(10, 2) DEFAULT 0.00,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
);

-- ============================================================================
-- PLAYERS TABLE
-- Stores information about athletes
-- ============================================================================
CREATE TABLE IF NOT EXISTS players (
    player_id INTEGER PRIMARY KEY AUTOINCREMENT,
    player_name TEXT NOT NULL,
    team TEXT,
    position TEXT,
    sport TEXT NOT NULL CHECK(sport IN ('NFL', 'NBA', 'MLB', 'NHL', 'Soccer', 'NCAAF', 'NCAAB')),
    jersey_number INTEGER,
    is_active BOOLEAN DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ============================================================================
-- GAMES TABLE
-- Stores information about scheduled sports games
-- ============================================================================
CREATE TABLE IF NOT EXISTS games (
    game_id INTEGER PRIMARY KEY AUTOINCREMENT,
    sport TEXT NOT NULL CHECK(sport IN ('NFL', 'NBA', 'MLB', 'NHL', 'Soccer', 'NCAAF', 'NCAAB')),
    league TEXT NOT NULL,
    home_team TEXT NOT NULL,
    away_team TEXT NOT NULL,
    game_date TIMESTAMP NOT NULL,
    venue TEXT,
    status TEXT DEFAULT 'scheduled' CHECK(status IN ('scheduled', 'live', 'final', 'postponed', 'cancelled')),
    home_score INTEGER,
    away_score INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ============================================================================
-- ENTRIES TABLE
-- Stores user betting entries (lineups/slips)
-- ============================================================================
CREATE TABLE IF NOT EXISTS entries (
    entry_id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    entry_amount DECIMAL(10, 2) NOT NULL CHECK(entry_amount > 0),
    potential_payout DECIMAL(10, 2) NOT NULL,
    actual_payout DECIMAL(10, 2) DEFAULT 0.00,
    num_picks INTEGER NOT NULL CHECK(num_picks BETWEEN 2 AND 6),  -- PrizePicks allows 2-6 picks
    entry_type TEXT NOT NULL CHECK(entry_type IN ('standard', 'flex', 'power', 'goblin')),  -- Different PrizePicks modes
    status TEXT DEFAULT 'pending' CHECK(status IN ('pending', 'won', 'lost', 'cancelled', 'pushed')),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    settled_at TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
);

-- ============================================================================
-- PICKS TABLE
-- Stores individual player prop picks within entries
-- ============================================================================
CREATE TABLE IF NOT EXISTS picks (
    pick_id INTEGER PRIMARY KEY AUTOINCREMENT,
    entry_id INTEGER NOT NULL,
    player_id INTEGER NOT NULL,
    game_id INTEGER,
    stat_type TEXT NOT NULL,  -- e.g., 'Points', 'Rebounds', 'Passing Yards', 'Strikeouts'
    line DECIMAL(10, 2) NOT NULL,  -- The over/under number
    selection TEXT NOT NULL CHECK(selection IN ('over', 'under')),
    actual_value DECIMAL(10, 2),  -- Actual stat result
    result TEXT DEFAULT 'pending' CHECK(result IN ('pending', 'hit', 'miss', 'push', 'void')),
    odds_at_selection INTEGER,  -- Store what the sportsbook odds were (optional)
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    settled_at TIMESTAMP,
    FOREIGN KEY (entry_id) REFERENCES entries(entry_id) ON DELETE CASCADE,
    FOREIGN KEY (player_id) REFERENCES players(player_id),
    FOREIGN KEY (game_id) REFERENCES games(game_id)
);

-- ============================================================================
-- TRANSACTIONS TABLE
-- Tracks all money movements for audit trail
-- ============================================================================
CREATE TABLE IF NOT EXISTS transactions (
    transaction_id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    transaction_type TEXT NOT NULL CHECK(transaction_type IN ('deposit', 'withdrawal', 'bet_placed', 'payout', 'refund', 'bonus')),
    amount DECIMAL(10, 2) NOT NULL,
    balance_before DECIMAL(10, 2) NOT NULL,
    balance_after DECIMAL(10, 2) NOT NULL,
    related_entry_id INTEGER,  -- Links to entry if transaction is bet/payout
    status TEXT DEFAULT 'completed' CHECK(status IN ('pending', 'completed', 'failed', 'cancelled')),
    payment_method TEXT,  -- e.g., 'credit_card', 'paypal', 'venmo'
    transaction_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    notes TEXT,
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE,
    FOREIGN KEY (related_entry_id) REFERENCES entries(entry_id) ON DELETE SET NULL
);

-- ============================================================================
-- INDEXES FOR PERFORMANCE
-- Speed up common queries
-- ============================================================================

-- User lookups
CREATE INDEX IF NOT EXISTS idx_users_username ON users(username);
CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);
CREATE INDEX IF NOT EXISTS idx_users_state ON users(state);
CREATE INDEX IF NOT EXISTS idx_users_status ON users(account_status);

-- Wallet lookups
CREATE INDEX IF NOT EXISTS idx_wallets_user_id ON wallets(user_id);

-- Player lookups
CREATE INDEX IF NOT EXISTS idx_players_name ON players(player_name);
CREATE INDEX IF NOT EXISTS idx_players_sport ON players(sport);

-- Game lookups
CREATE INDEX IF NOT EXISTS idx_games_date ON games(game_date);
CREATE INDEX IF NOT EXISTS idx_games_status ON games(status);

-- Entry lookups
CREATE INDEX IF NOT EXISTS idx_entries_user_id ON entries(user_id);
CREATE INDEX IF NOT EXISTS idx_entries_status ON entries(status);
CREATE INDEX IF NOT EXISTS idx_entries_created_at ON entries(created_at);

-- Pick lookups
CREATE INDEX IF NOT EXISTS idx_picks_entry_id ON picks(entry_id);
CREATE INDEX IF NOT EXISTS idx_picks_player_id ON picks(player_id);
CREATE INDEX IF NOT EXISTS idx_picks_result ON picks(result);

-- Transaction lookups
CREATE INDEX IF NOT EXISTS idx_transactions_user_id ON transactions(user_id);
CREATE INDEX IF NOT EXISTS idx_transactions_type ON transactions(transaction_type);
CREATE INDEX IF NOT EXISTS idx_transactions_date ON transactions(transaction_date);

-- ============================================================================
-- VIEWS FOR COMMON QUERIES
-- Pre-defined queries for dashboard analytics
-- ============================================================================

-- User summary view with wallet info
CREATE VIEW IF NOT EXISTS user_summary AS
SELECT 
    u.user_id,
    u.username,
    u.email,
    u.state,
    u.created_at,
    u.account_status,
    w.current_balance,
    w.total_deposits,
    w.total_withdrawals,
    w.total_winnings,
    w.total_wagered,
    COUNT(DISTINCT e.entry_id) as total_entries,
    COUNT(DISTINCT CASE WHEN e.status = 'won' THEN e.entry_id END) as winning_entries,
    COUNT(DISTINCT CASE WHEN e.status = 'lost' THEN e.entry_id END) as losing_entries
FROM users u
LEFT JOIN wallets w ON u.user_id = w.user_id
LEFT JOIN entries e ON u.user_id = e.user_id
GROUP BY u.user_id;

-- Popular players view
CREATE VIEW IF NOT EXISTS popular_players AS
SELECT 
    p.player_id,
    p.player_name,
    p.team,
    p.sport,
    COUNT(pk.pick_id) as times_picked,
    COUNT(CASE WHEN pk.result = 'hit' THEN 1 END) as times_hit,
    ROUND(CAST(COUNT(CASE WHEN pk.result = 'hit' THEN 1 END) AS FLOAT) / 
          NULLIF(COUNT(CASE WHEN pk.result IN ('hit', 'miss') THEN 1 END), 0) * 100, 2) as hit_rate_percentage
FROM players p
LEFT JOIN picks pk ON p.player_id = pk.player_id
GROUP BY p.player_id
HAVING times_picked > 0
ORDER BY times_picked DESC;

-- Daily revenue view
CREATE VIEW IF NOT EXISTS daily_revenue AS
SELECT 
    DATE(transaction_date) as date,
    SUM(CASE WHEN transaction_type = 'deposit' THEN amount ELSE 0 END) as total_deposits,
    SUM(CASE WHEN transaction_type = 'withdrawal' THEN amount ELSE 0 END) as total_withdrawals,
    SUM(CASE WHEN transaction_type = 'bet_placed' THEN amount ELSE 0 END) as total_wagered,
    SUM(CASE WHEN transaction_type = 'payout' THEN amount ELSE 0 END) as total_payouts,
    SUM(CASE WHEN transaction_type = 'bet_placed' THEN amount ELSE 0 END) - 
    SUM(CASE WHEN transaction_type = 'payout' THEN amount ELSE 0 END) as net_revenue
FROM transactions
GROUP BY DATE(transaction_date)
ORDER BY date DESC;