import requests
import os
from datetime import datetime, timezone

# Endpoints from the site's JavaScript
CHANNELS_API = "https://plusbox.tv/channels.php"
TOKEN_API = "https://plusbox.tv/token.php"
BACKEND_BASE = "https://backend.plusbox.tv/"
OUTPUT_FILE = "playlist.m3u"

def get_gmt_string():
    """Generates a standard RFC 1123 GMT timestamp for headers."""
    return datetime.now(timezone.utc).strftime('%a, %d %b %Y %H:%M:%S GMT')

def main():
    session = requests.Session()
    
    # Standard headers with dynamic GMT timestamp
    # Some backends use the 'Date' header to verify the freshness of the request
    current_gmt = get_gmt_string()
    
    session.headers.update({
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
        "Referer": "https://plusbox.tv/",
        "X-Requested-With": "XMLHttpRequest",
        "Date": current_gmt  # Informing the server of our current GMT time
    })

    try:
        print(f"Starting capture at: {current_gmt}")
        print("Fetching channel list...")
        
        response = session.get(CHANNELS_API, timeout=15)
        response.raise_for_status()
        
        data = response.json()
        channel_list = data.get('channels', [])
        final_channels = []

        for ch in channel_list:
            data_name = ch.get('data_name', '').strip()
            display_name = ch.get('name', data_name)
            logo_url = ch.get('icon', '')
            
            if not data_name:
                continue

            print(f"Requesting token for: {display_name}")
            
            # Step 2: POST to get the unique session token
            # We refresh the GMT header for each post to ensure accuracy
            session.headers.update({"Date": get_gmt_string()})
            payload = {'ch_name': data_name}
            
            try:
                token_response = session.post(TOKEN_API, data=payload, timeout=10)
                
                if token_response.status_code == 200:
                    token = token_response.text.strip()
                    
                    # Construct the video stream URL
                    # Note: These tokens are usually GMT-bound and expire quickly
                    video_url = f"{BACKEND_BASE}{data_name}/tracks-v1/index.fmp4.m3u8?token={token}"
                    
                    final_channels.append({
                        "name": display_name, 
                        "url": video_url,
                        "logo": logo_url
                    })
                else:
                    print(f"  [!] Failed to get token for {display_name} (Status: {token_response.status_code})")
                    
            except requests.RequestException as e:
                print(f"  [!] Connection error for {display_name}: {e}")

        # Step 3: Write to M3U
        if final_channels:
            with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
                f.write("#EXTM3U\n")
                for ch in final_channels:
                    # tvg-logo is essential for TiviMate and IPTV Smarters
                    f.write(f'#EXTINF:-1 tvg-logo="{ch["logo"]}", {ch["name"]}\n')
                    f.write(f'{ch["url"]}\n')
            
            print("-" * 30)
            print(f"Done! Created {len(final_channels)} channels.")
            print(f"Playlist saved to: {os.path.abspath(OUTPUT_FILE)}")
        else:
            print("No channels were processed successfully.")

    except Exception as e:
        print(f"Critical Error: {e}")

if __name__ == "__main__":
    main()
