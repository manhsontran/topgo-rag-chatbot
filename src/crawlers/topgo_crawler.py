# src/crawlers/topgo_crawler.py
import requests
from bs4 import BeautifulSoup
import json
import time
from tqdm import tqdm
from typing import List, Dict
import re

class TopGoCrawler:
    def __init__(self):
        self.base_url = "https://topgo.vn"
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
    
    def get_restaurant_urls(self, max_pages_per_category: int | None = None) -> List[str]:
        """Lấy danh sách URLs của tất cả nhà hàng
        
        Args:
            max_pages_per_category: Số trang tối đa crawl cho mỗi category (None = không giới hạn)
        """
        urls = []
        seen_urls = set()  # Track URLs to detect duplicates
        
        # Crawl từ các category pages
        categories = [
            '/category/nha-hang/',
            '/category/karaoke/',
            '/category/bar-lounge/',
        ]
        
        for category in categories:
            print(f"\n📂 Category: {category}")
            page = 1
            pages_crawled = 0
            no_new_urls_count = 0  # Count pages with no new URLs
            
            while True:
                # Check limit nếu có
                if max_pages_per_category and pages_crawled >= max_pages_per_category:
                    print(f"  ⏸️  Reached limit of {max_pages_per_category} pages")
                    break
                
                # Stop if we've seen 10 consecutive pages with no new URLs (pagination loop detected)
                if no_new_urls_count >= 10:
                    print(f"  🔄 Detected pagination loop - stopping category")
                    break
                
                url = f"{self.base_url}{category}page/{page}/"
                page_info = f"  Page {page}" + (f"/{max_pages_per_category}" if max_pages_per_category else "")
                print(f"{page_info}: {url}")
                
                try:
                    response = self.session.get(url, timeout=10)
                    if response.status_code != 200:
                        print(f"  ⚠️ Status {response.status_code}, stopping category")
                        break
                    
                    soup = BeautifulSoup(response.content.decode('utf-8'), 'html.parser')
                    
                    # Tìm links đến restaurant pages
                    posts = soup.find_all('div', class_='column-post')
                    if not posts:
                        print(f"  ⚠️ No posts found, stopping category")
                        break
                    
                    new_urls_this_page = 0
                    for post in posts:
                        link = post.find('a', href=True)
                        if link and link['href'].startswith('https://topgo.vn/'):
                            # Loại bỏ các link không phải nhà hàng
                            url_lower = link['href'].lower()
                            if not any(skip in url_lower for skip in ['/category/', '/wp-', '/tag/', '/combo-deals/', '/top-goi-y/', '/nha-tai-tro/', '/blog/', '/diem-nhan/', '/trip/']):
                                if link['href'] not in seen_urls:
                                    seen_urls.add(link['href'])
                                    urls.append(link['href'])
                                    new_urls_this_page += 1
                    
                    if new_urls_this_page == 0:
                        no_new_urls_count += 1
                        print(f"  ⚠️  No new URLs (duplicate page {no_new_urls_count}/10)")
                    else:
                        no_new_urls_count = 0  # Reset counter
                        print(f"  ✓ Found {new_urls_this_page} NEW restaurant links")
                    
                    page += 1
                    pages_crawled += 1
                    time.sleep(0.5)  # Rate limiting
                    
                except Exception as e:
                    print(f"  ❌ Error: {e}")
                    break
        
        unique_urls = list(set(urls))  # Remove duplicates
        print(f"\n✅ Total unique restaurant URLs: {len(unique_urls)}")
        return unique_urls
    
    def extract_phone(self, soup) -> str:
        """Extract số điện thoại"""
        phone_link = soup.find('a', href=re.compile(r'tel:'))
        if phone_link:
            return phone_link.get('href', '').replace('tel:', '')
        return ""
    
    def extract_address(self, soup) -> str:
        """Extract địa chỉ"""
        # Pattern 1: Tìm trong column-post-adress (trên trang listing)
        addr_div = soup.find('div', class_='column-post-adress')
        if addr_div:
            text = addr_div.text.strip()
            # Clean: loại bỏ số điện thoại duplicate
            text = re.sub(r'\d{10,}', '', text)
            text = re.sub(r'\s+', ' ', text).strip()
            if len(text) > 10:
                return text[:300]
        
        # Pattern 2: Tìm text có "địa chỉ:"
        addr_text = soup.find(string=re.compile(r'địa chỉ:', re.IGNORECASE))
        if addr_text:
            # Lấy text sau "địa chỉ:"
            match = re.search(r'địa chỉ:\s*([^\n]+)', addr_text, re.IGNORECASE)
            if match:
                return match.group(1).strip()[:300]
        
        # Pattern 3: Tìm trong intro-in
        intro = soup.find('div', class_='intro-in')
        if intro:
            addr_p = intro.find('p', string=re.compile(r'địa chỉ:', re.IGNORECASE))
            if addr_p:
                text = addr_p.text.strip()
                match = re.search(r'địa chỉ:\s*([^\n]+)', text, re.IGNORECASE)
                if match:
                    return match.group(1).strip()[:300]
        
        return ""
    
    def parse_restaurant(self, url: str) -> Dict | None:
        """Parse thông tin 1 nhà hàng"""
        try:
            response = self.session.get(url, timeout=10)
            soup = BeautifulSoup(response.content.decode('utf-8'), 'html.parser')
            
            # Extract title/name
            title_tag = soup.find('h1') or soup.find('title')
            name = title_tag.text.strip() if title_tag else ""
            
            # Extract description - PATTERN 1: Tìm trong div#abouts (GIỚI THIỆU)
            description = ""
            abouts = soup.find('div', id='abouts')
            if abouts:
                paragraphs = abouts.find_all('p')
                desc_parts = []
                for p in paragraphs[:3]:
                    text = p.text.strip()
                    # Bỏ qua các paragraph quá ngắn hoặc chỉ có số điện thoại
                    if len(text) > 30 and not re.match(r'^\d+$', text):
                        desc_parts.append(text)
                description = ' '.join(desc_parts)[:800]
            
            # PATTERN 2: Nếu không có, thử tìm trong intro-in
            if not description:
                intro = soup.find('div', class_='intro-in')
                if intro:
                    paragraphs = intro.find_all('p')
                    desc_parts = []
                    for p in paragraphs[:3]:
                        text = p.text.strip()
                        if len(text) > 30 and not re.match(r'^\d+$', text):
                            desc_parts.append(text)
                    description = ' '.join(desc_parts)[:800]
            
            # PATTERN 3: Tìm các paragraph sau heading "GIỚI THIỆU"
            if not description:
                intro_heading = soup.find(string=re.compile(r'giới thiệu', re.IGNORECASE))
                if intro_heading and intro_heading.parent:
                    parent = intro_heading.parent
                    desc_parts = []
                    # Tìm các paragraph tiếp theo
                    for sibling in parent.find_next_siblings(limit=5):
                        if sibling.name == 'p':
                            text = sibling.text.strip()
                            if len(text) > 30:
                                desc_parts.append(text)
                    if desc_parts:
                        description = ' '.join(desc_parts[:3])[:800]
            
            # Extract metadata
            phone = self.extract_phone(soup)
            address = self.extract_address(soup)
            
            # Infer cuisine type from content
            content_text = soup.get_text().lower()
            cuisine_keywords = {
                'việt': ['việt nam', 'cơm', 'phở', 'bún', 'món việt'],
                'nhật': ['nhật bản', 'sushi', 'ramen', 'izakaya', 'sake'],
                'hàn': ['hàn quốc', 'kimchi', 'bbq hàn', 'korean'],
                'âu': ['âu', 'steak', 'pasta', 'pizza', 'italian', 'french'],
                'trung': ['trung hoa', 'dimsum', 'quảng đông', 'hongkong', 'dim sum']
            }
            
            cuisine_type = []
            for cuisine, keywords in cuisine_keywords.items():
                if any(kw in content_text for kw in keywords):
                    cuisine_type.append(cuisine)
            
            # Infer price range - CẢI THIỆN LOGIC
            price_range = "trung_binh"  # Default
            
            # Tìm price text
            price_text = ""
            price_elements = soup.find_all(string=re.compile(r'(giá|price|vnđ)', re.IGNORECASE))
            for elem in price_elements:
                text = elem.strip()
                if 10 < len(text) < 300 and any(word in text.lower() for word in ['giá', 'price', 'vnđ', 'đồng']):
                    price_text += " " + text.lower()
            
            # Phân loại dựa trên keywords và số tiền
            if any(word in price_text for word in ['cao cấp', 'sang trọng', 'đẳng cấp', 'luxury', 'premium']):
                price_range = "cao_cap"
            elif any(word in price_text for word in ['bình dân', 'giá rẻ', 'phải chăng', 'affordable', 'budget']):
                price_range = "binh_dan"
            else:
                # Dựa trên số tiền
                numbers = re.findall(r'(\d{1,3}(?:[.,]\d{3})*)', price_text)
                if numbers:
                    try:
                        # Lấy số lớn nhất
                        max_price = max([int(n.replace('.', '').replace(',', '')) for n in numbers])
                        if max_price > 500000:
                            price_range = "cao_cap"
                        elif max_price < 200000:
                            price_range = "binh_dan"
                    except:
                        pass
            
            # Extract features
            features = []
            feature_keywords = {
                'view_dep': ['view đẹp', 'tầm nhìn', 'panorama', 'rooftop'],
                'sang_trong': ['sang trọng', 'đẳng cấp', 'cao cấp', 'luxury'],
                'am_cung': ['ấm cúng', 'thân thiện', 'gần gũi', 'cozy'],
                'hen_ho': ['hẹn hò', 'lãng mạn', 'tình nhân', 'romantic'],
                'gia_dinh': ['gia đình', 'trẻ em', 'sum họp', 'family'],
                'cong_ty': ['công ty', 'team building', 'tiệc', 'sự kiện']
            }
            
            for feature, keywords in feature_keywords.items():
                if any(kw in content_text for kw in keywords):
                    features.append(feature)
            
            restaurant = {
                'url': url,
                'name': name,
                'description': description,
                'phone': phone,
                'address': address,
                'cuisine_type': cuisine_type,
                'price_range': price_range,
                'features': features,
                'full_content': content_text[:2000]  # For better embedding
            }
            
            return restaurant
            
        except Exception as e:
            print(f"❌ Error parsing {url}: {e}")
            return None
    
    def crawl_all(self, output_file: str = 'data/raw/restaurants.json', max_pages_per_category: int = 5, max_restaurants: int | None = None):
        """Crawl tất cả nhà hàng
        
        Args:
            output_file: File đầu ra
            max_pages_per_category: Số trang tối đa cho mỗi category
            max_restaurants: Số lượng nhà hàng tối đa cần crawl (None = không giới hạn)
        """
        print("🔍 Getting restaurant URLs...")
        urls = self.get_restaurant_urls(max_pages_per_category=max_pages_per_category)
        
        if max_restaurants:
            urls = urls[:max_restaurants]
            print(f"📊 Limiting to {len(urls)} restaurants")
        
        print(f"✅ Will crawl {len(urls)} restaurants\n")
        
        restaurants = []
        for url in tqdm(urls, desc="🍽️  Crawling"):
            restaurant = self.parse_restaurant(url)
            if restaurant:
                restaurants.append(restaurant)
            time.sleep(0.5)  # Rate limiting
        
        # Save to JSON
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(restaurants, f, ensure_ascii=False, indent=2)
        
        print(f"\n✅ Saved {len(restaurants)} restaurants to {output_file}")
        return restaurants

# Chạy crawler
if __name__ == "__main__":
    crawler = TopGoCrawler()
    restaurants = crawler.crawl_all()