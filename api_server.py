"""
Flask API Server for PrizePicks EV Dashboard
Serves ev_analysis.json and handles data refresh requests
"""
from flask import Flask, jsonify, request
from flask_cors import CORS
import json
import subprocess
import os

app = Flask(__name__)
CORS(app)  # Enable CORS for React frontend

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
    1. sportsbookapi.py - Get sportsbook TD lines
    2. prizepicksapi.py - Get PrizePicks props
    3. match_props.py - Match the props
    4. calculate_ev.py - Calculate EV
    """
    try:
        print("\n" + "="*60)
        print("🔄 REFRESH REQUEST RECEIVED FROM FRONTEND")
        print("="*60)
        print(f"⏰ Timestamp: {__import__('datetime').datetime.now()}")
        
        # Step 1: Get sportsbook data
        print("\n" + "🏈" * 30)
        print("[1/4] 📊 RUNNING SPORTSBOOKAPI.PY...")
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
        print("[3/4] 🔀 RUNNING MATCH_PROPS.PY...")
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
        print("[4/4] 📈 RUNNING CALCULATE_EV.PY...")
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

if __name__ == '__main__':
    print("\n" + "🚀" * 30)
    print("PRIZEPICKS EV DASHBOARD API SERVER")
    print("🚀" * 30)
    print("\nEndpoints:")
    print("  GET  /api/ev-data  - Get current EV analysis")
    print("  POST /api/refresh  - Refresh all data")
    print("  GET  /api/health   - Health check")
    print("\nServer running at: http://localhost:5000")
    print("Frontend should connect from: http://localhost:3000")
    print("\n" + "="*60 + "\n")
    
    app.run(debug=True, port=5000)