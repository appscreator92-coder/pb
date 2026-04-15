import os
import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def get_plusbox_channels():
    # Setup Chrome Options for GitHub Actions
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    
    driver = webdriver.Chrome(options=chrome_options)
    channels = []

    try:
        driver.get("https://plusbox.tv/")
        
        # Wait up to 10 seconds for channel elements to appear
        # Adjust the 'a' or class name if you inspect the site and find a better selector
        wait = WebDriverWait(driver, 10)
        wait.until(EC.presence_of_element_located((By.TAG_NAME, "a")))
        
        # Give it an extra second for any JS to finish rendering
        time.sleep(2)

        elements = driver.find_all(By.TAG_NAME, "a")
        
        for el in elements:
            href = el.get_attribute("href")
            name = el.text.strip()
            
            # Filter out external links like Kodevite or Social Media
            if href and "plusbox.tv" in href and name and "KODEVITE" not in name.upper():
                channels.append({"name": name, "url": href})

    except Exception as e:
        print(f"Error: {e}")
    finally:
        driver.quit()
    
    return channels

def save_m3u(channels):
    with open("playlist.m3u", "w", encoding="utf-8") as f:
        f.write("#EXTM3U\n")
        for ch in channels:
            f.write(f'#EXTINF:-1, {ch["name"]}\n')
            f.write(f'{ch["url"]}\n')
    print(f"Generated playlist.m3u with {len(channels)} channels.")

if __name__ == "__main__":
    ch_list = get_plusbox_channels()
    save_m3u(ch_list)
