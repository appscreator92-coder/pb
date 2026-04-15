import requests
import os
from datetime import datetime, timezone

# Configuration
CHANNELS_API = "https://plusbox.tv/channels.php"
TOKEN_API = "https://plusbox.tv/token.php"
BACKEND_BASE = "https://backend.plusbox.tv/"
OUTPUT_FILE = "playlist.m3u"

def get_precise_headers():
    """
    Returns the exact headers found in the browser's request, 
    including the specific Sec-CH-UA and Fetch Metadata.
    """
    return {
        "authority": "plusbox.tv",
        "accept": "*/*",
        "accept-encoding": "gzip, deflate, br, zstd",
        "accept-language": "en-US,en;q=0.9",
        "connection": "keep-alive",
        "content-type": "application/x-www-form-urlencoded; charset=UTF-8",
        "host": "plusbox.tv",
        "origin": "https://plusbox.tv",
        "referer": "https://plusbox.tv/",
        "sec-ch-ua": '"Google Chrome";v="147", "Not.A/Brand";v="8", "Chromium";v="147"',
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": '"Windows"',
        "sec-fetch-dest": "empty",
        "sec-fetch-mode": "cors",
        "sec-fetch-site": "same-origin",
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/147.0.0.0 Safari/537.36",
        "x-requested-with": "XMLHttpRequest"
    }

def main():
    # Session keeps cookies like PHPSESSID, which is vital for token.php
    session = requests.Session()
    session.headers.update(get_precise_headers())

    try:
        # Step 1: Sync with Server Date
        print(f"[*] Starting Capture - Local Time: {datetime.now(timezone.utc)} GMT")
        
        response = session.get(CHANNELS_API, timeout=15)
        server_date = response.headers.get('Date')
        print(f"[*] Server Response Date: {server_date}")

        data = response.json()
        channel_list = data.get('channels', [])
        final_channels = []

        # Step 2: Loop and Fetch Tokens
        for ch in channel_list:
            data_name = ch.get('data_name', '').strip()
            display_name = ch.get('name', data_name)
            logo_url = ch.get('icon', '')
            
            if not data_name:
                continue

            # Every POST request to token.php must be treated as a fresh CORS request
            payload = {'ch_name': data_name}
            
            try:
                # We use 'data=' for x-www-form-urlencoded content
                token_resp = session.post(TOKEN_API, data=payload, timeout=10)
                
                if token_resp.status_code == 200:
                    # Strip HTML whitespace from the text/html response
                    token = token_resp.text.strip()
                    
                    if token:
                        video_url = f"{BACKEND_BASE}{data_name}/tracks-v1/index.fmp4.m3u8?token={token}"
                        final_channels.append({
                            "name": display_name, 
                            "url": video_url,
                            "logo": logo_url
                        })
                        print(f"  [OK] Token captured for {display_name}")
                else:
                    print(f"  [FAIL] {display_name} returned status {token_resp.status_code}")
                    
            except Exception as e:
                print(f"  [ERR] Error fetching token for {display_name}: {e}")

        # Step 3: Write M3U
        if final_channels:
            with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
                f.write("#EXTM3U\n")
                for ch in final_channels:
                    f.write(f'#EXTINF:-1 tvg-logo="{ch["logo"]}", {ch["name"]}\n')
                    f.write(f'{ch["url"]}\n')
            
            print(f"\n[SUCCESS] Saved {len(final_channels)} channels to {OUTPUT_FILE}")
        else:
            print("\n[!] No channels were successfully processed.")

    except Exception as e:
        print(f"[FATAL] Script error: {e}")

if __name__ == "__main__":
    main()
