import os
from datetime import datetime, timezone
from curl_cffi import requests  # Mimics Chrome's TLS fingerprint

# Configuration
BASE_URL = "https://plusbox.tv"
CHANNELS_API = f"{BASE_URL}/channels.php"
TOKEN_API = f"{BASE_URL}/token.php"
BACKEND_BASE = "https://backend.plusbox.tv/"
OUTPUT_FILE = "playlist.m3u"

def get_precise_headers():
    """
    Returns the exact headers matching the browser capture provided.
    Includes the specific Chrome v147 signatures.
    """
    return {
        "authority": "plusbox.tv",
        "accept": "*/*",
        "accept-language": "en-US,en;q=0.9",
        "content-type": "application/x-www-form-urlencoded; charset=UTF-8",
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
    # 'impersonate' makes the underlying C library act like a real Chrome browser
    session = requests.Session(impersonate="chrome110")
    session.headers.update(get_precise_headers())

    try:
        print(f"[*] Starting Capture at {datetime.now(timezone.utc)} GMT")
        
        # 1. Warm up the session by visiting the home page (crucial for cookies/WAF)
        print("[*] Warming up session...")
        session.get(BASE_URL, timeout=15)

        # 2. Fetch the channel list
        print("[*] Fetching channel list...")
        response = session.get(CHANNELS_API, timeout=15)
        response.raise_for_status()
        
        data = response.json()
        channel_list = data.get('channels', [])
        final_channels = []

        # 3. Request tokens for each channel
        for ch in channel_list:
            data_name = ch.get('data_name', '').strip()
            display_name = ch.get('name', data_name)
            logo_url = ch.get('icon', '')
            
            if not data_name:
                continue

            print(f"  [>] Capturing: {display_name}")
            payload = {'ch_name': data_name}
            
            try:
                # We use the 'chrome110' impersonation for the POST as well
                token_resp = session.post(TOKEN_API, data=payload, timeout=10)
                
                # Strip potential HTML or whitespace
                token = token_resp.text.strip()

                if "Unauthorized" in token or token_resp.status_code == 403:
                    print(f"    [!] Error: Streamer protection blocked {display_name}.")
                    continue
                
                if token:
                    # Construct URL. Note: we add the Referer to the stream URL too.
                    video_url = f"{BACKEND_BASE}{data_name}/tracks-v1/index.fmp4.m3u8?token={token}"
                    final_channels.append({
                        "name": display_name, 
                        "url": video_url,
                        "logo": logo_url
                    })
            except Exception as e:
                print(f"    [!] Error for {display_name}: {e}")

        # 4. Generate M3U File
        if final_channels:
            with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
                f.write("#EXTM3U\n")
                for ch in final_channels:
                    # KODI/VLC need the Referer header passed to the stream itself
                    f.write(f'#EXTINF:-1 tvg-logo="{ch["logo"]}", {ch["name"]}\n')
                    f.write(f'#EXTVLCOPT:http-referrer=https://plusbox.tv/\n')
                    f.write(f'#EXTVLCOPT:http-user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/147.0.0.0 Safari/537.36\n')
                    f.write(f'{ch["url"]}\n')
            
            print(f"\n[SUCCESS] Created {len(final_channels)} channels.")
            print(f"[NOTE] Playlist saved to {os.path.abspath(OUTPUT_FILE)}")
        else:
            print("\n[!] Failed to generate any valid streams.")

    except Exception as e:
        print(f"\n[CRITICAL ERROR] {e}")

if __name__ == "__main__":
    main()
