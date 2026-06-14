import os, requests, re
from bs4 import BeautifulSoup
from supabase import create_client, Client

SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY")
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
}

def get_price_takealot(url):
    try:
        r = requests.get(url, headers=headers, timeout=15)
        soup = BeautifulSoup(r.text, 'lxml')
print(f"Status: {r.status_code}")  # Add this line
price_tag = soup.find('span', {'data-ref': 'buybox-price-main'})  # Fixed line
        price_tag = soup.find('span', {'data-ref': 'buybox-price-main'})
        if price_tag:
            price = re.sub(r'[^\d.]', '', price_tag.text)
            return float(price)
    except Exception as e:
        print(f"Takealot error {url}: {e}")
    return None

def get_price_makro(url):
    try:
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
    urls = supabase.table('product_urls').select('*, stores(name)').execute()
    
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
        else:
            print(f"Failed to get price for {url}")

if __name__ == "__main__":
    main()
