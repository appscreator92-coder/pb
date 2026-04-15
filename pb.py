import requests
import re
import os

# Configuration
BASE_URL = "https://plusbox.tv/"
OUTPUT_FILE = "playlist.m3u"

def main():
    print("Fetching Plusbox main page...")
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36",
        "Referer": "https://google.com"
    }
    
    try:
        response = requests.get(BASE_URL, headers=headers, timeout=15)
        response.raise_for_status()
        html_content = response.text

        # 1. Look for M3U8 links directly in the page source (often in scripts)
        # Regex to find links ending in .m3u8, capturing the URL
        streams = re.findall(r'(https?://[^\s"\']+\.m3u8[^\s"\']*)', html_content)
        
        # 2. Look for common JSON patterns like { "title": "...", "file": "..." }
        # This is common in web players
        json_streams = re.findall(r'["\']title["\']\s*:\s*["\']([^"\']+)["\'].*?["\']file["\']\s*:\s*["\']([^"\']+\.m3u8[^"\']*)["\']', html_content)

        channels = []
        
        # Process direct M3U8 finds
        for i, url in enumerate(set(streams)):
            clean_url = url.replace('\\', '')
            channels.append({"name": f"Channel {i+1}", "url": clean_url})

        # Process JSON finds (better names)
        for name, url in json_streams:
            clean_url = url.replace('\\', '')
            channels.append({"name": name, "url": clean_url})

        # Deduplicate and save
        unique_channels = {ch['url']: ch['name'] for ch in channels}
        
        with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
            f.write("#EXTM3U\n")
            if not unique_channels:
                print("Warning: No streams found. The site may be using an iframe protector.")
            else:
                for url, name in unique_channels.items():
                    f.write(f'#EXTINF:-1, {name}\n')
                    f.write(f'{url}\n')
        
        print(f"Success! Found {len(unique_channels)} video streams.")

    except Exception as e:
        print(f"Scraper Error: {e}")
        # Create empty file to keep Git happy
        with open(OUTPUT_FILE, "w") as f:
            f.write("#EXTM3U\n")

if __name__ == "__main__":
    main()
