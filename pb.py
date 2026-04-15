import requests
import json
import os

# Endpoints from the site's JavaScript
CHANNELS_API = "https://plusbox.tv/channels.php"
TOKEN_API = "https://plusbox.tv/token.php"
BACKEND_BASE = "https://backend.plusbox.tv/"
OUTPUT_FILE = "playlist.m3u"

def main():
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
        "Referer": "https://plusbox.tv/",
        "X-Requested-With": "XMLHttpRequest"
    }

    try:
        print("Fetching channel list and logos...")
        response = requests.get(CHANNELS_API, headers=headers)
        data = response.json()
        
        channel_list = data.get('channels', [])
        final_channels = []

        for ch in channel_list:
            data_name = ch.get('data_name', '').strip()
            display_name = ch.get('name', data_name)
            logo_url = ch.get('icon', '') # Extracting the logo URL
            
            if not data_name:
                continue

            print(f"Requesting token for: {display_name}")
            
            # Step 2: POST to get the unique session token
            payload = {'ch_name': data_name}
            token_response = requests.post(TOKEN_API, data=payload, headers=headers)
            
            if token_response.status_code == 200:
                token = token_response.text.strip()
                
                # Construct the video stream URL
                video_url = f"{BACKEND_BASE}{data_name}/tracks-v1/index.fmp4.m3u8?token={token}"
                
                final_channels.append({
                    "name": display_name, 
                    "url": video_url,
                    "logo": logo_url
                })
            
        # Step 3: Write to M3U with tvg-logo support
        with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
            f.write("#EXTM3U\n")
            for ch in final_channels:
                # Adding tvg-logo for players like TiviMate, OTT Navigator, or VLC
                f.write(f'#EXTINF:-1 icon="{ch["logo"]}", {ch["name"]}\n')
                f.write(f'{ch["url"]}\n')
        
        print(f"Done! Created {len(final_channels)} channels with logos.")

    except Exception as e:
        print(f"Error: {e}")
        if not os.path.exists(OUTPUT_FILE):
            with open(OUTPUT_FILE, "w") as f: f.write("#EXTM3U\n")

if __name__ == "__main__":
    main()
