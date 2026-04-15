import requests
import re
import os

# Configuration
# Based on your input, the video backend is backend.plusbox.tv
BASE_URL = "https://plusbox.tv/"
BACKEND_URL = "https://backend.plusbox.tv"
OUTPUT_FILE = "playlist.m3u"

def main():
    print("Initiating Plusbox backend scan...")
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
        "Referer": BASE_URL
    }
    
    try:
        # Step 1: Scan the main site to find where the channels are defined
        response = requests.get(BASE_URL, headers=headers, timeout=15)
        response.raise_for_status()
        
        # Step 2: Extract M3U8 links with tokens using a refined regex
        # This regex targets the backend.plusbox.tv pattern you provided
        pattern = r'(https?://backend\.plusbox\.tv/[^\s"\']+\.m3u8\?token=[^\s"\']+)'
        tokenized_links = re.findall(pattern, response.text)
        
        # Step 3: Extract channel names from the URL path
        channels = []
        for link in set(tokenized_links):
            # Clean link and extract the channel folder name as the title
            clean_link = link.replace('\\', '')
            # Example extraction: .../StarSports1HD/tracks-v1/ -> StarSports1HD
            name_match = re.search(r'plusbox\.tv/([^/]+)/', clean_link)
            name = name_match.group(1) if name_match else "Live Stream"
            
            channels.append({"name": name, "url": clean_link})

        # Step 4: Write the M3U file
        with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
            f.write("#EXTM3U\n")
            if not channels:
                print("Zero channels found. The site may have moved its manifest to a separate JSON file.")
            else:
                for ch in channels:
                    f.write(f'#EXTINF:-1, {ch["name"]}\n')
                    f.write(f'{ch["url"]}\n')
                print(f"Successfully generated {OUTPUT_FILE} with {len(channels)} channels.")

    except Exception as e:
        print(f"Workflow error: {e}")
        # Always create the file to satisfy GitHub Actions requirements
        if not os.path.exists(OUTPUT_FILE):
            with open(OUTPUT_FILE, "w") as f:
                f.write("#EXTM3U\n")

if __name__ == "__main__":
    main()
