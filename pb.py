import requests
import re
from bs4 import BeautifulSoup
import time

# Configuration
BASE_URL = "https://plusbox.tv/"
M3U_FILE = "playlist.m3u"

def get_video_link(channel_url):
    """Visits the channel page and extracts the raw .m3u8 link."""
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36",
        "Referer": BASE_URL
    }
    try:
        response = requests.get(channel_url, headers=headers, timeout=10)
        # Look for the m3u8 pattern in the HTML (even if inside scripts)
        m3u8_pattern = re.compile(r'(https?://[^\s"\']+\.m3u8[^\s"\']*)')
        match = m3u8_pattern.search(response.text)
        
        if match:
            return match.group(1)
    except Exception as e:
        print(f"Failed to extract video from {channel_url}: {e}")
    return None

def main():
    headers = {"User-Agent": "Mozilla/5.0"}
    response = requests.get(BASE_URL, headers=headers)
    soup = BeautifulSoup(response.text, 'html.parser')
    
    channels = []
    # Adjust 'a' tag logic based on the actual site structure
    for link in soup.find_all('a', href=True):
        href = link['href']
        name = link.get_text(strip=True)
        
        # Skip footer/nav links
        if "play" in href or "channel" in href:
            full_url = href if href.startswith('http') else BASE_URL + href
            print(f"Checking channel: {name}...")
            
            video_url = get_video_link(full_url)
            if video_url:
                channels.append({"name": name, "url": video_url})
                print(f"Found Video Link: {video_url}")
            
            # Avoid getting rate-limited
            time.sleep(1)

    # Save to M3U
    with open(M3U_FILE, "w", encoding="utf-8") as f:
        f.write("#EXTM3U\n")
        for ch in channels:
            f.write(f'#EXTINF:-1, {ch["name"]}\n')
            # You might need to add headers for players like VLC/TiviMate
            f.write(f'#EXTVLCOPT:http-user-agent={headers["User-Agent"]}\n')
            f.write(f'{ch["url"]}\n')

if __name__ == "__main__":
    main()
