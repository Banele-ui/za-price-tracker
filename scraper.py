import os, requests, re
from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup
from supabase import create_client, Client

SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY")
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

def get_price_takealot(url):
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()
            page.goto(url, wait_until='domcontentloaded', timeout=60000)
            page.wait_for_selector('span[data-ref="buybox-price-main"], div[class*="price"], [data-testid="price"]', timeout=20000)
            price_text = page.locator('span[data-ref="buybox-price-main"], div[class*="price"], [data-testid="price"]').first.inner_text()
            browser.close()
            print(f"Status: 200")
            price = re.sub(r'[^\d.]', '', price_text)
            return float(price)
    except Exception as e:
        print(f"Takealot error {url}: {e}")
        return None

def get_price_makro(url):
    try:
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
        r = requests.get(url, headers=headers, timeout=15)
        soup = BeautifulSoup(r.text, 'lxml')
        price_tag = soup.find('p', class_=re.compile('price'))
        if price_tag:
            price = re.sub(r'[^\d.]', '', price_tag.text)
            return float(price)
    except Exception as e:
        print(f"Makro error {url}: {e}")
    return None

def main():
    urls = supabase.table('product_urls').select('*').execute()
    
    if not urls.data:
        print("No product URLs found in database")
        return
    
    for item in urls.data:
        url = item['url']
        store_name = item['stores']['name']
        product_url_id = item['id']
        
        price = None
        if store_name == 'Takealot':
            price = get_price_takealot(url)
        elif store_name == 'Makro':
            price = get_price_makro(url)
        
        if price:
            supabase.table('prices').insert({
                'product_url_id': product_url_id,
                'price': price,
                'in_stock': True
            }).execute()
            print(f"Saved {store_name}: R{price}")
    
    print("Scrape done.")

if __name__ == "__main__":
    main()
