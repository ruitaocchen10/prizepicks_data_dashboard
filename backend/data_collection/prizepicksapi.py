import requests
import json
import os
import time

def get_prizepicks_props():
    """Fetch all NFL props from PrizePicks API"""
    url = 'https://api.prizepicks.com/projections'
    
    # More complete headers to mimic a real browser
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'application/json',
        'Accept-Language': 'en-US,en;q=0.9',
        'Accept-Encoding': 'gzip, deflate, br',
        'Referer': 'https://app.prizepicks.com/',
        'Origin': 'https://app.prizepicks.com',
        'Connection': 'keep-alive',
        'Sec-Fetch-Dest': 'empty',
        'Sec-Fetch-Mode': 'cors',
        'Sec-Fetch-Site': 'same-site',
    }
    
    params = {
        'league_id': '9',  # NFL
        'per_page': '250',
        'single_stat': 'true'
    }
    
    print("Fetching PrizePicks NFL props...")
    
    # Add a small delay to not look suspicious
    time.sleep(1)
    
    try:
        response = requests.get(url, headers=headers, params=params, timeout=10)
        
        print(f"Status code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            
            # Save to file
            os.makedirs('backend/data_storage', exist_ok=True)
            with open('backend/data_storage/prizepicks_props.json', 'w') as f:
                json.dump(data, f, indent=2)
            
            print(f"✅ Successfully fetched {len(data.get('data', []))} PrizePicks props")
            print(f"📁 Saved to backend/data_storage/prizepicks_props.json")
            return data
        elif response.status_code == 403:
            print("❌ Error 403: Access denied (bot protection triggered)")
            print("Response text (first 500 chars):")
            print(response.text[:500])
            print("\n💡 Try these solutions:")
            print("   1. Wait a few minutes and try again")
            print("   2. Use a different IP (try from your phone's hotspot)")
            print("   3. Visit https://app.prizepicks.com in your browser first")
            print("   4. Consider using a proxy or Selenium (more advanced)")
            return None
        else:
            print(f"❌ Error: {response.status_code}")
            print(f"Response: {response.text[:500]}")
            return None
            
    except requests.exceptions.JSONDecodeError:
        print("❌ JSON parsing failed: Response is not valid JSON (likely blocked)")
        print("Response text (first 500 chars):")
        print(response.text[:500])
        return None
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return None

if __name__ == "__main__":
    get_prizepicks_props()