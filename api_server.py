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
        print("REFRESH REQUEST RECEIVED")
        print("="*60)
        
        # Step 1: Get sportsbook data
        print("\n[1/4] Running sportsbookapi.py...")
        result1 = subprocess.run(
            ['python', 'backend/data_collection/sportsbookapi.py'],
            capture_output=True,
            text=True,
            timeout=60  # 60 second timeout
        )
        if result1.returncode != 0:
            return jsonify({
                'error': 'Sportsbook API failed',
                'details': result1.stderr
            }), 500
        print("✅ Sportsbook data collected")
        
        # Step 2: Get PrizePicks data
        print("\n[2/4] Running prizepicksapi.py...")
        result2 = subprocess.run(
            ['python', 'backend/data_collection/prizepicksapi.py'],
            capture_output=True,
            text=True,
            timeout=30
        )
        if result2.returncode != 0:
            return jsonify({
                'error': 'PrizePicks API failed',
                'details': result2.stderr
            }), 500
        print("✅ PrizePicks data collected")
        
        # Step 3: Match props
        print("\n[3/4] Running match_props.py...")
        result3 = subprocess.run(
            ['python', 'backend/data_processing/match_props.py'],
            capture_output=True,
            text=True,
            timeout=10
        )
        if result3.returncode != 0:
            return jsonify({
                'error': 'Prop matching failed',
                'details': result3.stderr
            }), 500
        print("✅ Props matched")
        
        # Step 4: Calculate EV
        print("\n[4/4] Running calculate_ev.py...")
        result4 = subprocess.run(
            ['python', 'backend/ev_calculation/calculate_ev.py'],
            capture_output=True,
            text=True,
            timeout=10
        )
        if result4.returncode != 0:
            return jsonify({
                'error': 'EV calculation failed',
                'details': result4.stderr
            }), 500
        print("✅ EV calculated")
        
        print("\n" + "="*60)
        print("REFRESH COMPLETE!")
        print("="*60 + "\n")
        
        # Load and return the new data
        with open(DATA_FILE, 'r') as f:
            data = json.load(f)
        
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