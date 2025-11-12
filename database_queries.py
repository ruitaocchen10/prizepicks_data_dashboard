"""
Database Query Functions for PrizePicks Analytics Dashboard

This module contains all SQL query logic for the pre-built analytics views.
Keeps api_server.py clean and focused on routing.
"""

import sqlite3
import os
from datetime import datetime
from typing import Optional, List, Dict, Any

# Database configuration
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
# Script is now in project root, so SCRIPT_DIR is already PROJECT_ROOT
PROJECT_ROOT = SCRIPT_DIR
DATABASE_FILE = os.path.join(PROJECT_ROOT, 'backend', 'data_storage', 'user_data.db')

# ============================================================================
# DATABASE CONNECTION HELPER
# ============================================================================

def get_db_connection():
    """
    Create and return a database connection with Row factory
    This allows accessing columns by name like a dictionary
    """
    conn = sqlite3.connect(DATABASE_FILE)
    conn.row_factory = sqlite3.Row
    return conn

def execute_query(query: str, params: tuple = ()) -> List[Dict]:
    """
    Execute a query and return results as list of dictionaries
    
    Args:
        query: SQL query string
        params: Query parameters (for preventing SQL injection)
    
    Returns:
        List of dictionaries representing rows
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(query, params)
    results = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return results

# ============================================================================
# PRE-BUILT ANALYTICS QUERIES
# ============================================================================

def get_top_winners(
    sort_by: str = 'revenue',
    state: Optional[str] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    limit: int = 10
) -> Dict[str, Any]:
    """
    Get top 10 winning users based on either revenue (net profit) or count (number of wins)
    
    Args:
        sort_by: 'revenue' (net profit) or 'count' (number of winning entries)
        state: Filter by US state (e.g., 'NY', 'CA') or None for all states
        start_date: Start date filter (ISO format: 'YYYY-MM-DD') or None
        end_date: End date filter (ISO format: 'YYYY-MM-DD') or None
        limit: Number of results to return (default 10)
    
    Returns:
        Dictionary with query metadata and results
    """
    
    # Build the base query
    if sort_by == 'revenue':
        # Sort by net profit (total winnings - total wagered)
        query = """
            SELECT 
                u.user_id,
                u.username,
                u.state,
                u.account_status,
                COUNT(DISTINCT e.entry_id) as total_entries,
                COUNT(DISTINCT CASE WHEN e.status = 'won' THEN e.entry_id END) as winning_entries,
                COUNT(DISTINCT CASE WHEN e.status = 'lost' THEN e.entry_id END) as losing_entries,
                SUM(CASE WHEN e.status = 'won' THEN e.actual_payout ELSE 0 END) as total_winnings,
                SUM(e.entry_amount) as total_wagered,
                (SUM(CASE WHEN e.status = 'won' THEN e.actual_payout ELSE 0 END) - SUM(e.entry_amount)) as net_profit,
                CASE 
                    WHEN SUM(e.entry_amount) > 0 
                    THEN ROUND((SUM(CASE WHEN e.status = 'won' THEN e.actual_payout ELSE 0 END) - SUM(e.entry_amount)) / SUM(e.entry_amount) * 100, 2)
                    ELSE 0 
                END as roi_percentage,
                ROUND(CAST(COUNT(CASE WHEN e.status = 'won' THEN 1 END) AS FLOAT) / 
                      NULLIF(COUNT(CASE WHEN e.status IN ('won', 'lost') THEN 1 END), 0) * 100, 1) as win_rate_percentage
            FROM users u
            JOIN entries e ON u.user_id = e.user_id
            WHERE e.status IN ('won', 'lost')
        """
        order_by = "ORDER BY net_profit DESC"
    else:  # sort_by == 'count'
        # Sort by number of winning entries
        query = """
            SELECT 
                u.user_id,
                u.username,
                u.state,
                u.account_status,
                COUNT(DISTINCT e.entry_id) as total_entries,
                COUNT(DISTINCT CASE WHEN e.status = 'won' THEN e.entry_id END) as winning_entries,
                COUNT(DISTINCT CASE WHEN e.status = 'lost' THEN e.entry_id END) as losing_entries,
                SUM(CASE WHEN e.status = 'won' THEN e.actual_payout ELSE 0 END) as total_winnings,
                SUM(e.entry_amount) as total_wagered,
                (SUM(CASE WHEN e.status = 'won' THEN e.actual_payout ELSE 0 END) - SUM(e.entry_amount)) as net_profit,
                ROUND(CAST(COUNT(CASE WHEN e.status = 'won' THEN 1 END) AS FLOAT) / 
                      NULLIF(COUNT(CASE WHEN e.status IN ('won', 'lost') THEN 1 END), 0) * 100, 1) as win_rate_percentage
            FROM users u
            JOIN entries e ON u.user_id = e.user_id
            WHERE e.status IN ('won', 'lost')
        """
        order_by = "ORDER BY winning_entries DESC"
    
    # Add filters
    params = []
    
    if state:
        query += " AND u.state = ?"
        params.append(state)
    
    if start_date:
        query += " AND DATE(e.created_at) >= ?"
        params.append(start_date)
    
    if end_date:
        query += " AND DATE(e.created_at) <= ?"
        params.append(end_date)
    
    # Group by user and add ordering and limit
    query += f"""
        GROUP BY u.user_id
        HAVING total_entries > 0
        {order_by}
        LIMIT ?
    """
    params.append(limit)
    
    # Execute query
    results = execute_query(query, tuple(params))
    
    return {
        'query_type': 'top_winners',
        'filters': {
            'sort_by': sort_by,
            'state': state,
            'start_date': start_date,
            'end_date': end_date,
            'limit': limit
        },
        'count': len(results),
        'results': results
    }

def get_top_hit_lines(
    sort_by: str = 'revenue',
    state: Optional[str] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    limit: int = 10
) -> Dict[str, Any]:
    """
    Get top 10 hit lines (specific player props that users won on)
    
    Args:
        sort_by: 'revenue' (total payout from this line) or 'count' (number of times hit)
        state: Filter by US state or None for all states
        start_date: Start date filter (ISO format: 'YYYY-MM-DD') or None
        end_date: End date filter (ISO format: 'YYYY-MM-DD') or None
        limit: Number of results to return (default 10)
    
    Returns:
        Dictionary with query metadata and results
    """
    
    # Build the query
    query = """
        SELECT 
            p.player_name,
            p.position,
            p.team,
            pk.stat_type,
            pk.line,
            pk.selection,
            COUNT(pk.pick_id) as times_picked,
            COUNT(CASE WHEN pk.result = 'hit' THEN 1 END) as times_hit,
            COUNT(CASE WHEN pk.result = 'miss' THEN 1 END) as times_missed,
            SUM(CASE WHEN pk.result = 'hit' AND e.status = 'won' THEN e.actual_payout ELSE 0 END) as total_revenue_generated,
            ROUND(CAST(COUNT(CASE WHEN pk.result = 'hit' THEN 1 END) AS FLOAT) / 
                  NULLIF(COUNT(CASE WHEN pk.result IN ('hit', 'miss') THEN 1 END), 0) * 100, 1) as hit_rate_percentage
        FROM picks pk
        JOIN players p ON pk.player_id = p.player_id
        JOIN entries e ON pk.entry_id = e.entry_id
        JOIN users u ON e.user_id = u.user_id
        WHERE pk.result IN ('hit', 'miss')
    """
    
    # Add filters
    params = []
    
    if state:
        query += " AND u.state = ?"
        params.append(state)
    
    if start_date:
        query += " AND DATE(pk.created_at) >= ?"
        params.append(start_date)
    
    if end_date:
        query += " AND DATE(pk.created_at) <= ?"
        params.append(end_date)
    
    # Group by specific line (player + stat + line + selection)
    query += """
        GROUP BY p.player_id, pk.stat_type, pk.line, pk.selection
        HAVING times_hit > 0
    """
    
    # Add ordering based on sort_by
    if sort_by == 'revenue':
        query += " ORDER BY total_revenue_generated DESC"
    else:  # sort_by == 'count'
        query += " ORDER BY times_hit DESC"
    
    query += " LIMIT ?"
    params.append(limit)
    
    # Execute query
    results = execute_query(query, tuple(params))
    
    # Format the line description for frontend
    for result in results:
        result['line_description'] = f"{result['player_name']} {result['selection'].upper()} {result['line']} {result['stat_type']}"
    
    return {
        'query_type': 'top_hit_lines',
        'filters': {
            'sort_by': sort_by,
            'state': state,
            'start_date': start_date,
            'end_date': end_date,
            'limit': limit
        },
        'count': len(results),
        'results': results
    }

def search_user(search_query: str) -> Dict[str, Any]:
    """
    Search for a user by username or email and return their complete profile
    
    Args:
        search_query: Username or email to search for (partial match supported)
    
    Returns:
        Dictionary with user profile data including:
        - Basic info (username, email, state, status)
        - Wallet info (balance, deposits, wagered, winnings)
        - Entry statistics (total, wins, losses, win rate)
        - Most picked players
        - Recent entries
    """
    
    # Search for user (case-insensitive partial match)
    user_query = """
        SELECT 
            u.user_id,
            u.username,
            u.email,
            u.first_name,
            u.last_name,
            u.state,
            u.account_status,
            u.kyc_verified,
            u.created_at,
            u.last_login,
            w.current_balance,
            w.total_deposits,
            w.total_wagered,
            w.total_winnings
        FROM users u
        LEFT JOIN wallets w ON u.user_id = w.user_id
        WHERE u.username LIKE ? OR u.email LIKE ?
        LIMIT 1
    """
    
    search_pattern = f"%{search_query}%"
    results = execute_query(user_query, (search_pattern, search_pattern))
    
    if not results:
        return {
            'query_type': 'user_search',
            'search_query': search_query,
            'found': False,
            'message': 'No user found matching that username or email'
        }
    
    user = results[0]
    user_id = user['user_id']
    
    # Calculate net profit and ROI
    net_profit = user['total_winnings'] - user['total_wagered']
    roi = (net_profit / user['total_wagered'] * 100) if user['total_wagered'] > 0 else 0
    
    user['net_profit'] = round(net_profit, 2)
    user['roi_percentage'] = round(roi, 2)
    
    # Get entry statistics
    entry_stats_query = """
        SELECT 
            COUNT(*) as total_entries,
            COUNT(CASE WHEN status = 'won' THEN 1 END) as winning_entries,
            COUNT(CASE WHEN status = 'lost' THEN 1 END) as losing_entries,
            COUNT(CASE WHEN status = 'pending' THEN 1 END) as pending_entries,
            ROUND(AVG(entry_amount), 2) as avg_bet_size,
            MAX(actual_payout) as biggest_win,
            MIN(CASE WHEN status = 'won' THEN actual_payout END) as smallest_win,
            ROUND(CAST(COUNT(CASE WHEN status = 'won' THEN 1 END) AS FLOAT) / 
                  NULLIF(COUNT(CASE WHEN status IN ('won', 'lost') THEN 1 END), 0) * 100, 1) as win_rate_percentage
        FROM entries
        WHERE user_id = ?
    """
    
    entry_stats = execute_query(entry_stats_query, (user_id,))[0]
    
    # Get most picked players (top 5)
    most_picked_query = """
        SELECT 
            p.player_name,
            p.position,
            p.team,
            COUNT(pk.pick_id) as times_picked,
            COUNT(CASE WHEN pk.result = 'hit' THEN 1 END) as times_hit,
            ROUND(CAST(COUNT(CASE WHEN pk.result = 'hit' THEN 1 END) AS FLOAT) / 
                  NULLIF(COUNT(CASE WHEN pk.result IN ('hit', 'miss') THEN 1 END), 0) * 100, 1) as hit_rate_percentage
        FROM picks pk
        JOIN players p ON pk.player_id = p.player_id
        JOIN entries e ON pk.entry_id = e.entry_id
        WHERE e.user_id = ?
        GROUP BY p.player_id
        ORDER BY times_picked DESC
        LIMIT 5
    """
    
    most_picked_players = execute_query(most_picked_query, (user_id,))
    
    # Get recent entries (last 10)
    recent_entries_query = """
        SELECT 
            e.entry_id,
            e.entry_amount,
            e.potential_payout,
            e.actual_payout,
            e.num_picks,
            e.entry_type,
            e.status,
            e.created_at,
            e.settled_at,
            (e.actual_payout - e.entry_amount) as profit_loss
        FROM entries e
        WHERE e.user_id = ?
        ORDER BY e.created_at DESC
        LIMIT 10
    """
    
    recent_entries = execute_query(recent_entries_query, (user_id,))
    
    # Get picks for each recent entry
    for entry in recent_entries:
        picks_query = """
            SELECT 
                p.player_name,
                p.position,
                pk.stat_type,
                pk.line,
                pk.selection,
                pk.result
            FROM picks pk
            JOIN players p ON pk.player_id = p.player_id
            WHERE pk.entry_id = ?
        """
        entry['picks'] = execute_query(picks_query, (entry['entry_id'],))
    
    return {
        'query_type': 'user_search',
        'search_query': search_query,
        'found': True,
        'user': user,
        'entry_stats': entry_stats,
        'most_picked_players': most_picked_players,
        'recent_entries': recent_entries
    }

# ============================================================================
# HELPER FUNCTIONS FOR API
# ============================================================================

def get_available_states() -> List[str]:
    """
    Get list of all states that have users
    Useful for populating state dropdown in frontend
    """
    query = """
        SELECT DISTINCT state 
        FROM users 
        WHERE state IS NOT NULL 
        ORDER BY state
    """
    results = execute_query(query)
    return [row['state'] for row in results]

def get_date_range() -> Dict[str, str]:
    """
    Get the min and max dates from entries table
    Useful for setting date picker bounds in frontend
    """
    query = """
        SELECT 
            MIN(DATE(created_at)) as min_date,
            MAX(DATE(created_at)) as max_date
        FROM entries
    """
    result = execute_query(query)[0]
    return {
        'min_date': result['min_date'],
        'max_date': result['max_date']
    }

# ============================================================================
# TESTING
# ============================================================================

if __name__ == "__main__":
    """Test the query functions"""
    
    print("=" * 60)
    print("TESTING DATABASE QUERIES")
    print("=" * 60)
    
    # Test 1: Top winners by revenue
    print("\n1. Top 10 Winners by Revenue (All States):")
    result = get_top_winners(sort_by='revenue', limit=5)
    print(f"Found {result['count']} results")
    for idx, winner in enumerate(result['results'][:3], 1):
        print(f"  {idx}. {winner['username']} - Net Profit: ${winner['net_profit']:.2f}")
    
    # Test 2: Top hit lines by count in NY
    print("\n2. Top 5 Hit Lines by Count in NY:")
    result = get_top_hit_lines(sort_by='count', state='NY', limit=5)
    print(f"Found {result['count']} results")
    for idx, line in enumerate(result['results'][:3], 1):
        print(f"  {idx}. {line['line_description']} - Hit {line['times_hit']} times")
    
    # Test 3: User search
    print("\n3. Search for user 'john':")
    result = search_user('john')
    if result['found']:
        user = result['user']
        print(f"  Found: {user['username']} ({user['email']})")
        print(f"  Balance: ${user['current_balance']:.2f}")
        print(f"  Net Profit: ${user['net_profit']:.2f}")
        print(f"  Win Rate: {result['entry_stats']['win_rate_percentage']}%")
    else:
        print(f"  {result['message']}")
    
    # Test 4: Helper functions
    print("\n4. Available States:")
    states = get_available_states()
    print(f"  {', '.join(states[:10])}...")
    
    print("\n5. Date Range:")
    date_range = get_date_range()
    print(f"  {date_range['min_date']} to {date_range['max_date']}")
    
    print("\n" + "=" * 60)
    print("ALL TESTS COMPLETE")
    print("=" * 60)