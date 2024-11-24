from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import time

class BettingScraper:
    def __init__(self, url):
        self.url = url
        self.known_events = {}
        self.setup_driver()
    
    def setup_driver(self):
        try:
            chrome_options = Options()
            chrome_options.add_argument('--headless')
            chrome_options.add_argument('--disable-gpu')
            chrome_options.add_argument('--no-sandbox')
            chrome_options.add_argument('--disable-dev-shm-usage')
            chrome_options.add_argument('--window-size=1920,1080')
            
            self.driver = webdriver.Chrome(options=chrome_options)
            self.driver.get(self.url)  # Initial page load
            
            # Wait for initial page load
            time.sleep(10)
            WebDriverWait(self.driver, 20).until(
                EC.presence_of_element_located((By.CLASS_NAME, "space-between"))
            )
            
            print("✅ Driver setup successful")
        except Exception as e:
            print(f"❌ Driver setup failed: {e}")
            raise e
    
    def parse_event(self, button):
        try:
            title = button.find('div', class_='title').text.strip()
            odd = button.find('span').text.strip()
            return title, float(odd)
        except Exception as e:
            print(f"❌ Error parsing event: {e}")
            raise e
    
    def notify(self, title, odd, old_odd=None):
        print("\n=== Betting Event Update! ===")
        print(f"Title: {title}")
        if old_odd:
            print(f"Odd changed: {old_odd} -> {odd}")
        else:
            print(f"New event! Odd: {odd}")
        print("=======================\n")
    
    def scrape(self):
        try:
            print("\n🔄 Refreshing page...")
            self.driver.refresh()
            
            print("⏳ Waiting for elements to load...")
            WebDriverWait(self.driver, 20).until(
                EC.presence_of_all_elements_located((By.CLASS_NAME, "space-between"))
            )
            
            time.sleep(5)
            
            print("🔍 Parsing page content...")
            soup = BeautifulSoup(self.driver.page_source, 'html.parser')
            buttons = soup.find_all('button', class_='space-between')
            
            if not buttons:
                print("⚠️ No events found. Retrying...")
                return
                
            print(f"📊 Found {len(buttons)} events")
            
            # If this is the first scrape (known_events is empty), list all events
            is_first_scrape = not self.known_events
            if is_first_scrape:
                print("\n📋 Initial events list:")
                print("=" * 50)
            
            for button in buttons:
                title, odd = self.parse_event(button)
                
                # If this is the first scrape, print all events
                if is_first_scrape:
                    print(f"Title: {title}")
                    print(f"Odd: {odd}")
                    print("-" * 50)
                
                if title not in self.known_events:
                    # Completely new event
                    self.known_events[title] = odd
                    if not is_first_scrape:
                        self.notify(title, odd)
                elif self.known_events[title] != odd:
                    # Event exists but odd changed
                    old_odd = self.known_events[title]
                    self.known_events[title] = odd
                    if not is_first_scrape:
                        self.notify(title, odd, old_odd)
            
            if is_first_scrape:
                print("=" * 50)
                print("✅ Initial events recorded")
            
            print(f"✅ Scrape completed successfully, found {len(buttons)} events")
                    
        except Exception as e:
            print(f"❌ Error during scraping: {e}")
    
    def monitor(self, interval=300):  # interval in seconds
        print(f"🚀 Starting monitor with {interval} seconds interval")
        retry_count = 0
        max_retries = 3
        
        while True:
            try:
                self.scrape()
                retry_count = 0  # Reset counter on successful scrape
                print(f"💤 Sleeping for {interval} seconds...")
                time.sleep(interval)
            except KeyboardInterrupt:
                print("\n⛔ Monitoring stopped by user")
                break
            except Exception as e:
                print(f"❌ Error in monitor loop: {e}")
                retry_count += 1
                if retry_count >= max_retries:
                    print("⛔ Maximum retries reached. Restarting driver...")
                    self.driver.quit()
                    self.setup_driver()
                    retry_count = 0
                time.sleep(interval)
    
    def __del__(self):
        try:
            self.driver.quit()
            print("👋 Driver closed successfully")
        except:
            pass

if __name__ == "__main__":
    #betting_url = "https://www.brbet.com/home/events-area/s/CG"
    betting_url = "https://www.brbet.com/home/events-area/s/CGR?group_type=GROUP&identifier=LeozinTips&name=Leozin%20Tips"
    
    
    scraper = BettingScraper(betting_url)
    scraper.monitor()
