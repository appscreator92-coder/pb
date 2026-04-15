import requests
import re
from bs4 import BeautifulSoup
import os

# Configuration
BASE_URL = "https://plusbox.tv/"
OUTPUT_FILE = "playlist.m3u"

def get_video_source(page_url):
    """Scrapes a single channel page for the .m3u8 link."""
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36",
        "Referer": BASE_URL
    }
    try:
        response = requests.get(page_url, headers=headers, timeout=10)
        # Search for m3u8 patterns in scripts or source
        m3u8_pattern = re.compile(r'(https?://[^\s"\']+\.m3u8[^\s"\']*)')
        match = m3u8_pattern.search(response.text)
        if match:
            return match.group(1).replace('\\', '') # Clean any escaped slashes
    except Exception as e:
        print(f"Error checking {page_url}: {e}")
    return None

def main():
    print("Starting scraper...")
    headers = {"User-Agent": "Mozilla/5.0"}
    
    try:
        response = requests.get(BASE_URL, headers=headers)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        
        channels = []
        # Find all channel links (usually <a> tags with 'play' or specific IDs)
        for link in soup.find_all('a', href=True):
            href = link['href']
            name = link.get_text(strip=True)
            
            # Filter for video/play links and ignore generic dev links
            if "play" in href or "channel" in href:
                full_url = href if href.startswith('http') else BASE_URL + href.lstrip('/')
                
                print(f"Extracting video for: {name}")
                video_url = get_video_source(full_url)
                
                if video_url:
                    channels.append({"name": name, "url": video_url})

        # Write the M3U file
        with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
            f.write("#EXTM3U\n")
            if not channels:
                print("No video links found.")
            for ch in channels:
                f.write(f'#EXTINF:-1, {ch["name"]}\n')
                f.write(f'{ch["url"]}\n')
        
        print(f"Successfully saved {len(channels)} channels to {OUTPUT_FILE}")

    except Exception as e:
        print(f"Main scraper error: {e}")
        # Ensure file exists even on failure to prevent Git errors
        if not os.path.exists(OUTPUT_FILE):
            open(OUTPUT_FILE, 'w').close()

if __name__ == "__main__":
    main()
