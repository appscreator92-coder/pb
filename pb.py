import requests
from bs4 import BeautifulSoup
import os

# Configuration
URL = "https://plusbox.tv/"
FILE_NAME = "playlist.m3u"

def scrape_channels():
    channels = []
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
        "Referer": "https://plusbox.tv/"
    }

    try:
        response = requests.get(URL, headers=headers, timeout=15)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')

        # Look for links that likely point to channel players
        # Adjust the selector if you see specific classes like 'channel-card'
        for link in soup.find_all('a', href=True):
            href = link['href']
            name = link.get_text(strip=True) or "Unknown Channel"
            
            # Filter for links that aren't external social media or nav links
            if href.startswith('http') or href.endswith('.php') or 'play' in href:
                # Ensure the URL is absolute
                full_url = href if href.startswith('http') else f"https://plusbox.tv/{href.lstrip('/')}"
                channels.append({"name": name, "url": full_url})

    except Exception as e:
        print(f"Error during scraping: {e}")

    return channels

def save_to_m3u(channels):
    # Always create/overwrite the file to prevent Git pathspec errors
    with open(FILE_NAME, "w", encoding="utf-8") as f:
        f.write("#EXTM3U\n")
        if not channels:
            print("No channels found, creating empty M3U.")
            return
            
        for ch in channels:
            # We add a User-Agent and Referer to the M3U link for better compatibility
            f.write(f'#EXTINF:-1, {ch["name"]}\n')
            f.write(f'{ch["url"]}\n')
            
    print(f"Successfully saved {len(channels)} channels to {FILE_NAME}")

if __name__ == "__main__":
    found_channels = scrape_channels()
    save_to_m3u(found_channels)
