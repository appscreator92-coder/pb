import requests
import os

CHANNELS_API = "https://plusbox.tv/channels.php"
PROXY_URL = "https://hdlive1.unaux.com/livetv/hotstar/proxy.php?id=" # Change this to your URL
OUTPUT_FILE = "playlist.m3u"

def main():
    headers = {"User-Agent": "Mozilla/5.0", "Referer": "https://plusbox.tv/"}
    try:
        response = requests.get(CHANNELS_API, headers=headers)
        data = response.json()
        channels = data.get('channels', [])

        with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
            f.write("#EXTM3U\n")
            for ch in channels:
                name = ch.get('name')
                data_name = ch.get('data_name')
                logo = ch.get('icon')
                
                # Point to your PHP Proxy instead of the direct backend
                f.write(f'#EXTINF:-1 tvg-logo="{logo}", {name}\n')
                f.write(f'{PROXY_URL}{data_name}\n')
        
        print("Playlist created pointing to PHP Proxy.")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()
