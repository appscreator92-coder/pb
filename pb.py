import requests
import re
import os

# The main site and the observed backend
BASE_URL = "https://plusbox.tv/"
OUTPUT_FILE = "playlist.m3u"

def main():
    print("Scraping Plusbox for tokenized streams...")
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
        "Referer": BASE_URL
    }
    
    try:
        # Step 1: Fetch the main page content
        response = requests.get(BASE_URL, headers=headers, timeout=15)
        response.raise_for_status()
        html = response.text

        # Step 2: Extract tokenized backend links using Regex
        # Matches the pattern: https://backend.plusbox.tv/...index.m3u8?token=...
        pattern = r'(https://backend\.plusbox\.tv/[^\s"\']+\.m3u8\?token=[^\s"\']+)'
        found_links = re.findall(pattern, html)
        
        # Deduplicate links
        unique_links = list(set(found_links))
        
        channels = []
        for link in unique_links:
            # Clean up escaped slashes if any
            clean_link = link.replace('\\', '')
            
            # Extract a name from the URL path (e.g., StarSports1HD)
            name_match = re.search(r'backend\.plusbox\.tv/([^/]+)/', clean_link)
            name = name_match.group(1) if name_match else "Live Channel"
            
            channels.append({"name": name, "url": clean_link})

        # Step 3: Generate the M3U file
        with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
            f.write("#EXTM3U\n")
            if not channels:
                print("No active tokenized links found in the source.")
            else:
                for ch in channels:
                    f.write(f'#EXTINF:-1, {ch["name"]}\n')
                    f.write(f'{ch["url"]}\n')
        
        print(f"Success! {len(channels)} channels added to {OUTPUT_FILE}.")

    except Exception as e:
        print(f"Error: {e}")
        # Ensure file exists to prevent GitHub Action errors
        if not os.path.exists(OUTPUT_FILE):
            with open(OUTPUT_FILE, "w") as f: f.write("#EXTM3U\n")

if __name__ == "__main__":
    main()
