import requests
import re
import os

# Configuration
BASE_URL = "https://plusbox.tv"
# This is the most likely endpoint for KODEVITE-built players
DATA_URL = "https://plusbox.tv/config/channels.json" 
OUTPUT_FILE = "playlist.m3u"

def main():
    print("Connecting to Plusbox API...")
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
        "Referer": BASE_URL,
        "Accept": "application/json"
    }

    try:
        # Step 1: Try to fetch the channel list directly
        response = requests.get(DATA_URL, headers=headers, timeout=15)
        
        # If the JSON file isn't at /config/, we scan the main page for the list
        if response.status_code != 200:
            print("Direct JSON not found. Scanning main page scripts...")
            response = requests.get(BASE_URL, headers=headers)
            content = response.text
        else:
            content = response.text

        # Step 2: Use Regex to find any backend links with tokens
        # This matches the pattern you provided earlier
        links = re.findall(r'(https://backend\.plusbox\.tv/[^\s"\']+\.m3u8\?token=[^\s"\']+)', content)
        
        # Step 3: Extract names and build the list
        channels = []
        for link in set(links):
            clean_link = link.replace('\\', '')
            # Extract name from URL (e.g., StarSports1HD)
            name_match = re.search(r'plusbox\.tv/([^/]+)/', clean_link)
            name = name_match.group(1) if name_match else "Live Channel"
            channels.append({"name": name, "url": clean_link})

        # Step 4: Finalize the M3U
        with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
            f.write("#EXTM3U\n")
            if not channels:
                print("FAILURE: No links detected. The site is likely using a POST request for tokens.")
            else:
                for ch in channels:
                    f.write(f'#EXTINF:-1, {ch["name"]}\n')
                    f.write(f'{ch["url"]}\n')
                print(f"SUCCESS: {len(channels)} channels added to {OUTPUT_FILE}")

    except Exception as e:
        print(f"Error: {e}")
        # Make sure file exists for GitHub Actions
        if not os.path.exists(OUTPUT_FILE):
            with open(OUTPUT_FILE, "w") as f: f.write("#EXTM3U\n")

if __name__ == "__main__":
    main()
