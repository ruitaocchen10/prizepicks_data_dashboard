"""
Flask API Server for PrizePicks EV Dashboard
Serves ev_analysis.json and handles data refresh requests
"""
from flask import Flask, jsonify, request
from flask_cors import CORS
import json
import subprocess
import os
from database_queries import (  # ADD THIS IMPORT
    get_top_winners, 
    get_top_hit_lines, 
    search_user,
    get_available_states,
    get_date_range
)

app = Flask(__name__)
CORS(app)

# Path to data file
DATA_FILE = 'backend/data_storage/ev_analysis.json'

@app.route('/api/ev-data', methods=['GET'])
def get_ev_data():
    """
    GET endpoint to retrieve current EV analysis data
    Returns the contents of ev_analysis.json
    """
    try:
        with open(DATA_FILE, 'r') as f:
            data = json.load(f)
        return jsonify(data), 200
    except FileNotFoundError:
        return jsonify({
            'error': 'Data file not found',
            'message': 'Run the backend scripts first to generate ev_analysis.json'
        }), 404
    except Exception as e:
        return jsonify({
            'error': 'Failed to load data',
            'message': str(e)
        }), 500

@app.route('/api/refresh', methods=['POST'])
def refresh_data():
    """
    POST endpoint to refresh all data
    Runs all backend scripts in sequence:
    1. sportsbookapi.py - Get sportsbook passing yards lines
    2. prizepicksapi.py - Get PrizePicks props
    3. match_props.py - Match the props (±2.5 yard tolerance)
    4. calculate_ev.py - Calculate EV with probability adjustments
    """
    try:
        print("\n" + "="*60)
        print("🔄 REFRESH REQUEST RECEIVED FROM FRONTEND")
        print("="*60)
        print(f"⏰ Timestamp: {__import__('datetime').datetime.now()}")
        
        # Step 1: Get sportsbook data
        print("\n" + "🏈" * 30)
        print("[1/4] 📊 RUNNING SPORTSBOOKAPI.PY (Passing Yards)...")
        print("🏈" * 30)
        result1 = subprocess.run(
            ['python', 'backend/data_collection/sportsbookapi.py'],
            capture_output=True,
            text=True,
            timeout=60  # 60 second timeout
        )
        if result1.returncode != 0:
            print("❌ SPORTSBOOK API FAILED!")
            print(f"Error: {result1.stderr}")
            return jsonify({
                'error': 'Sportsbook API failed',
                'details': result1.stderr
            }), 500
        print("✅ SPORTSBOOK DATA COLLECTED SUCCESSFULLY")
        print(f"Output preview: {result1.stdout[:200]}...")
        
        # Step 2: Get PrizePicks data
        print("\n" + "🎯" * 30)
        print("[2/4] 🎲 RUNNING PRIZEPICKSAPI.PY...")
        print("🎯" * 30)
        result2 = subprocess.run(
            ['python', 'backend/data_collection/prizepicksapi.py'],
            capture_output=True,
            text=True,
            timeout=30
        )
        if result2.returncode != 0:
            print("❌ PRIZEPICKS API FAILED!")
            print(f"Error: {result2.stderr}")
            return jsonify({
                'error': 'PrizePicks API failed',
                'details': result2.stderr
            }), 500
        print("✅ PRIZEPICKS DATA COLLECTED SUCCESSFULLY")
        print(f"Output preview: {result2.stdout[:200]}...")
        
        # Step 3: Match props
        print("\n" + "🔗" * 30)
        print("[3/4] 🔀 RUNNING MATCH_PROPS.PY (±2.5 yard tolerance)...")
        print("🔗" * 30)
        result3 = subprocess.run(
            ['python', 'backend/data_processing/match_props.py'],
            capture_output=True,
            text=True,
            timeout=10
        )
        if result3.returncode != 0:
            print("❌ PROP MATCHING FAILED!")
            print(f"Error: {result3.stderr}")
            return jsonify({
                'error': 'Prop matching failed',
                'details': result3.stderr
            }), 500
        print("✅ PROPS MATCHED SUCCESSFULLY")
        print(f"Output preview: {result3.stdout[:200]}...")
        
        # Step 4: Calculate EV
        print("\n" + "💰" * 30)
        print("[4/4] 📈 RUNNING CALCULATE_EV.PY (with probability adjustments)...")
        print("💰" * 30)
        result4 = subprocess.run(
            ['python', 'backend/ev_calculation/calculate_ev.py'],
            capture_output=True,
            text=True,
            timeout=10
        )
        if result4.returncode != 0:
            print("❌ EV CALCULATION FAILED!")
            print(f"Error: {result4.stderr}")
            return jsonify({
                'error': 'EV calculation failed',
                'details': result4.stderr
            }), 500
        print("✅ EV CALCULATED SUCCESSFULLY")
        print(f"Output preview: {result4.stdout[:200]}...")
        
        print("\n" + "="*60)
        print("🎉 REFRESH COMPLETE! ALL SCRIPTS RAN SUCCESSFULLY")
        print("="*60)
        
        # Load and return the new data
        print("\n📂 Loading new ev_analysis.json file...")
        with open(DATA_FILE, 'r') as f:
            data = json.load(f)
        
        print(f"✅ Loaded {len(data)} props from new data")
        print(f"⏰ Completed at: {__import__('datetime').datetime.now()}")
        print("\n" + "="*60 + "\n")
        
        return jsonify({
            'status': 'success',
            'message': 'Data refreshed successfully',
            'prop_count': len(data)
        }), 200
        
    except subprocess.TimeoutExpired:
        return jsonify({
            'error': 'Refresh timeout',
            'message': 'One of the scripts took too long to run'
        }), 500
    except Exception as e:
        return jsonify({
            'error': 'Refresh failed',
            'message': str(e)
        }), 500

@app.route('/api/health', methods=['GET'])
def health_check():
    """Simple health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'message': 'API server is running'
    }), 200

# ============================================================================
# USER ANALYTICS ENDPOINTS
# ============================================================================

@app.route('/api/analytics/top-winners', methods=['GET'])
def api_top_winners():
    """
    GET top 10 winning users
    Query params:
        - sort_by: 'revenue' or 'count' (default: 'revenue')
        - state: US state code or None for all (default: None)
        - start_date: YYYY-MM-DD format (default: None)
        - end_date: YYYY-MM-DD format (default: None)
        - limit: number of results (default: 10)
    """
    try:
        sort_by = request.args.get('sort_by', 'revenue')
        state = request.args.get('state', None)
        start_date = request.args.get('start_date', None)
        end_date = request.args.get('end_date', None)
        limit = request.args.get('limit', 10, type=int)
        
        result = get_top_winners(
            sort_by=sort_by,
            state=state,
            start_date=start_date,
            end_date=end_date,
            limit=limit
        )
        
        return jsonify(result), 200
        
    except Exception as e:
        return jsonify({
            'error': 'Failed to fetch top winners',
            'message': str(e)
        }), 500

@app.route('/api/analytics/top-hit-lines', methods=['GET'])
def api_top_hit_lines():
    """
    GET top 10 hit lines (player props that won)
    Query params:
        - sort_by: 'revenue' or 'count' (default: 'revenue')
        - state: US state code or None for all (default: None)
        - start_date: YYYY-MM-DD format (default: None)
        - end_date: YYYY-MM-DD format (default: None)
        - limit: number of results (default: 10)
    """
    try:
        sort_by = request.args.get('sort_by', 'revenue')
        state = request.args.get('state', None)
        start_date = request.args.get('start_date', None)
        end_date = request.args.get('end_date', None)
        limit = request.args.get('limit', 10, type=int)
        
        result = get_top_hit_lines(
            sort_by=sort_by,
            state=state,
            start_date=start_date,
            end_date=end_date,
            limit=limit
        )
        
        return jsonify(result), 200
        
    except Exception as e:
        return jsonify({
            'error': 'Failed to fetch top hit lines',
            'message': str(e)
        }), 500

@app.route('/api/analytics/user-search', methods=['GET'])
def api_user_search():
    """
    Search for a user by username or email
    Query params:
        - q: search query (username or email)
    """
    try:
        query = request.args.get('q', '')
        
        if not query:
            return jsonify({
                'error': 'Missing search query',
                'message': 'Please provide a search query using ?q=username'
            }), 400
        
        result = search_user(query)
        
        return jsonify(result), 200
        
    except Exception as e:
        return jsonify({
            'error': 'Failed to search user',
            'message': str(e)
        }), 500

@app.route('/api/analytics/states', methods=['GET'])
def api_get_states():
    """
    GET list of all states with users (for dropdown)
    """
    try:
        states = get_available_states()
        return jsonify({
            'status': 'success',
            'states': states
        }), 200
        
    except Exception as e:
        return jsonify({
            'error': 'Failed to fetch states',
            'message': str(e)
        }), 500

@app.route('/api/analytics/date-range', methods=['GET'])
def api_get_date_range():
    """
    GET min and max dates from entries (for date picker bounds)
    """
    try:
        date_range = get_date_range()
        return jsonify({
            'status': 'success',
            'date_range': date_range
        }), 200
        
    except Exception as e:
        return jsonify({
            'error': 'Failed to fetch date range',
            'message': str(e)
        }), 500

if __name__ == '__main__':
    print("\n" + "🚀" * 30)
    print("PRIZEPICKS EV DASHBOARD API SERVER")
    print("🚀" * 30)
    
    print("\n📊 EV Analysis Endpoints:")
    print("  GET  /api/ev-data              - Get current EV analysis")
    print("  POST /api/refresh              - Refresh all data")
    print("  GET  /api/health               - Health check")
    
    print("\n👥 User Analytics Endpoints:")
    print("  GET  /api/analytics/top-winners    - Top winning users")
    print("  GET  /api/analytics/top-hit-lines  - Top hit player props")
    print("  GET  /api/analytics/user-search    - Search for user (param: q)")
    
    print("\n🔧 Helper Endpoints:")
    print("  GET  /api/analytics/states         - List of available states")
    print("  GET  /api/analytics/date-range     - Min/max dates for filters")
    
    print("\n💡 Example Usage:")
    print("  http://localhost:5000/api/analytics/top-winners?sort_by=revenue&state=NY")
    print("  http://localhost:5000/api/analytics/top-hit-lines?sort_by=count&limit=5")
    print("  http://localhost:5000/api/analytics/user-search?q=john")
    
    print("\nServer running at: http://localhost:5000")
    print("Frontend should connect from: http://localhost:3000")
    print("\n" + "="*60 + "\n")
    
    app.run(debug=True, port=5000)