import requests
from bs4 import BeautifulSoup

# Configuration
BASE_URL = "https://plusbox.tv"
OUTPUT_FILE = "playlist.m3u"

def get_channels():
    channels = []
    try:
        # User-Agent is essential to avoid being blocked
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        }
        
        response = requests.get(BASE_URL, headers=headers)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Note: You may need to adjust the selectors (e.g., 'a', 'div.channel-item') 
        # based on the specific HTML structure of the site.
        for item in soup.find_all('a', href=True):
            name = item.get_text(strip=True)
            link = item['href']
            
            # Filter for video links or specific channel pages
            if "play" in link or link.endswith(".m3u8"):
                if not link.startswith("http"):
                    link = BASE_URL + link
                channels.append({"name": name, "url": link})
                
        return channels

    except Exception as e:
        print(f"Error scraping site: {e}")
        return []

def create_m3u(channels):
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write("#EXTM3U\n")
        for ch in channels:
            f.write(f'#EXTINF:-1, {ch["name"]}\n')
            f.write(f'{ch["url"]}\n')
    print(f"Successfully created {OUTPUT_FILE} with {len(channels)} channels.")

if __name__ == "__main__":
    channel_list = get_channels()
    if channel_list:
        create_m3u(channel_list)
    else:
        print("No channels found.")
