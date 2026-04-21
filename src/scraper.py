import requests
from src.database import SessionLocal
from src.models import Product, PriceHistory

# ==================== GOOGLE DOC COOKIES ====================
GOOGLE_DOC_COOKIE_URL = "https://docs.google.com/document/d/1Iu-vrR3iu9zsSKa-UlG5dCqAXzHAltTY0WcY7UV7Dcc/export?format=txt"
PAGE_SIZE = 24
CNLG_URL = "https://cungnhaulamgiau.vn"
CNLG_API = f"{CNLG_URL}/api/proxy/bff"

def load_cookies_from_google_doc():
    try:
        r = requests.get(GOOGLE_DOC_COOKIE_URL, timeout=10)
        r.raise_for_status()
        cookie_string = r.content.decode('utf-8-sig').strip().replace('\ufeff', '')
        print(f"✅ Đã tải cookies từ Google Doc ({len(cookie_string)} ký tự)")
        return cookie_string
    except Exception as e:
        print(f"❌ Không tải được cookies: {e}")
        return ""

def get_headers():
    return {
        "Accept": "application/json, text/plain, */*",
        "Accept-Language": "vi,en;q=0.9",
        "Content-Type": "application/json",
        "Origin": CNLG_URL,
        "Referer": CNLG_URL,
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        "x-tenant-domain": "cungnhaulamgiau.vn",
        "x-tenant-id": "1",
        "x-foxing-sid": "3a26551225ec4beea2fdce53775b6be9",
        "x-foxing-uid": "106293",
        "Cookie": load_cookies_from_google_doc()
    }

def build_price_query(items):
    res = []
    for item in items:
        variation_id = item.get("unique_id") or item.get("variation_id")
        sku = item.get("sku")
        product_id = item.get("product_id")
        res.append({
            "product_id": product_id,
            "variation_id": variation_id,
            "sku": sku
        })
    return res

def crawl_price(db, product_items, price_items):
    for idx, price_item in enumerate(price_items):
        pro = product_items[idx]
        retail_price = price_item.get("fe_price_public")
        current_price = int(price_item.get("fe_price_override") or price_item.get("fe_price_group") or 0)
        original_price = int(price_item.get("fe_price_group") or 0)
        sku = price_item.get("sku")
        title = pro.get("product_name")
        discount_percent = round(
            (original_price - current_price) / original_price * 100) if original_price > current_price else 0
        print(f"\n✅ CRAWL THÀNH CÔNG!")
        print(f"   Product         : {title}")
        print(f"   SKU             : {sku}")
        print(f"   Giá hiện tại    : {current_price:,} ₫")
        print(f"   Giá gốc         : {original_price:,} ₫")

        # Lưu vào database
        product = db.query(Product).filter(Product.sku == sku).first()
        if not product:
            product = Product(sku=sku, url=pro.get('product_id'), title=title)
            db.add(product)
            db.commit()

        history = PriceHistory(
            sku=sku,
            retail_price=retail_price,
            original_price=original_price,
            current_price=current_price,
            discount_percent=discount_percent
        )
        db.add(history)
        db.commit()

def scrape_product(url = None):
    try:
        headers = get_headers()
        # ==================== BƯỚC 1: GỌI API SEARCH ====================
        search_payload = {
            "is_flash_sale": "F",
            "page_num": 1,
            "page_size": 24
        }

        print("🔍 Đang gọi API /variations/search ...")
        search_resp = requests.post(
            f"P{CNLG_API}/variations/search",
            headers=headers,
            json=search_payload,
            timeout=15
        )

        if search_resp.status_code != 200 or not search_resp.json().get("success"):
            print(f"❌ Search API lỗi {search_resp.status_code}")
            print(search_resp.text[:400])
            return
        search_resp_json = search_resp.json()

        items = search_resp_json["data"]["items"]
        if not items:
            print("❌ Không tìm thấy sản phẩm qua API search")
            return

        # ==================== BƯỚC 2: GỌI API GET-PRICE ====================
        price_payload = {
            "items": build_price_query(items)
        }

        print("🔍 Đang gọi API /variations/get-price ...")
        price_resp = requests.post(
            f"{CNLG_API}/variations/get-price",
            headers=headers,
            json=price_payload,
            timeout=15
        )

        if price_resp.status_code != 200:
            print(f"❌ Get-price API lỗi {price_resp.status_code}")
            return

        data = price_resp.json()
        if not data.get("success") or not data.get("data"):
            print("❌ Get-price không trả dữ liệu")
            return

        db = SessionLocal()
        crawl_price(db, data["data"], price_payload)

        # next other page base on total_pages
        total_records = search_resp_json["data"]["total_records"]

        db.close()

    except Exception as e:
        print(f"❌ Error crawling {url}: {e}")
