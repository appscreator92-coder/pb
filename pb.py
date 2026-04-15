import requests
import re
import os

def main():
    # Use a Session to keep cookies alive
    session = requests.Session()
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
        "Referer": "https://plusbox.tv/",
        "Origin": "https://plusbox.tv",
        "X-Requested-With": "XMLHttpRequest"
    }
    
    # 1. First, visit the homepage to get initial cookies
    session.get("https://plusbox.tv/", headers=headers)
    
    # 2. Get the channel list
    ch_response = session.get("https://plusbox.tv/channels.php", headers=headers)
    channels = ch_response.json().get('channels', [])
    
    playlist_content = "#EXTM3U\n"
    
    for ch in channels:
        data_name = ch['data_name'].strip()
        print(f"Processing: {data_name}")
        
        # 3. Get the token (Session will automatically send cookies back)
        token_payload = {'ch_name': data_name}
        token_res = session.post("https://plusbox.tv/token.php", data=token_payload, headers=headers)
        token = token_res.text.strip()
        
        if token:
            # Construct link
            url = f"https://backend.plusbox.tv/{data_name}/tracks-v1/index.fmp4.m3u8?token={token}"
            
            # 4. TEST the link immediately within the same session
            # This 'activates' the token for this session/IP
            test_res = session.head(url, headers=headers)
            
            if test_res.status_code == 200:
                playlist_content += f'#EXTINF:-1 tvg-logo="{ch["icon"]}", {ch["name"]}\n{url}\n'
            else:
                print(f"--- Failed to validate {data_name} (Status: {test_res.status_code})")

    with open("playlist.m3u", "w") as f:
        f.write(playlist_content)

if __name__ == "__main__":
    main()
