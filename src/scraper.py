import requests
import json
from src.database import SessionLocal
from src.models import Product, PriceHistory
from datetime import datetime

# ==================== GOOGLE DOC COOKIES ====================
GOOGLE_DOC_COOKIE_URL = (
    "https://docs.google.com/document/d/"
    "1Iu-vrR3iu9zsSKa-UlG5dCqAXzHAltTY0WcY7UV7Dcc"
    "/export?format=txt"
)

def load_cookies_from_google_doc():
    """Tải cookie mới nhất từ Google Doc của bạn"""
    try:
        r = requests.get(GOOGLE_DOC_COOKIE_URL, timeout=10)
        r.raise_for_status()
        cookie_string = r.text.strip()
        print(f"✅ Đã tải cookies từ Google Doc ({len(cookie_string)} ký tự)")
        return cookie_string
    except Exception as e:
        print(f"❌ Không tải được cookies từ Google Doc: {e}")
        return ""

# Headers cố định + Cookie động từ Google Doc
def get_headers():
    cookies = load_cookies_from_google_doc()
    return {
        "Accept": "application/json, text/plain, */*",
        "Accept-Language": "vi,en;q=0.9",
        "Content-Type": "application/json",
        "Origin": "https://cungnhaulamgiau.vn",
        "Referer": "https://cungnhaulamgiau.vn/",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.0.0 Safari/537.36",
        "x-tenant-domain": "cungnhaulamgiau.vn",
        "x-tenant-id": "1",
        "Cookie": cookies
    }

def scrape_product(url: str):
    try:
        # Lấy product_id từ URL
        product_id = url.split("_p")[-1].split("?")[0].strip()
        if not product_id.isdigit():
            print("❌ Không tìm thấy product_id trong URL")
            return

        payload = {
            "items": [{
                "product_id": int(product_id),
                "variation_id": None,
                "sku": None
            }]
        }

        headers = get_headers()

        response = requests.post(
            "https://cungnhaulamgiau.vn/api/proxy/bff/variations/get-price",
            headers=headers,
            json=payload,
            timeout=15
        )

        if response.status_code != 200:
            print(f"❌ API lỗi {response.status_code}")
            print("Response:", response.text[:400])
            return

        data = response.json()
        if not data.get("success") or not data.get("data"):
            print("❌ API không trả dữ liệu")
            return

        item = data["data"][0]

        sku = item.get("sku")
        current_price = int(item.get("fe_price_override") or item.get("fe_price_public") or 0)
        original_price = int(item.get("fe_price_public") or 0)

        print(f"✅ Crawled thành công!")
        print(f"   SKU          : {sku}")
        print(f"   Giá hiện tại : {current_price:,} ₫")
        print(f"   Giá gốc      : {original_price:,} ₫")

        # Lưu vào DB
        db = SessionLocal()
        product = db.query(Product).filter(Product.sku == sku).first()
        if not product:
            product = Product(sku=sku, url=url, title=f"Product {sku}")
            db.add(product)

        history = PriceHistory(
            sku=sku,
            retail_price=original_price,
            original_price=original_price,
            current_price=current_price,
            discount_percent=round((original_price - current_price) / original_price * 100) if original_price > current_price else 0
        )
        db.add(history)
        db.commit()
        db.close()

    except Exception as e:
        print(f"❌ Error crawling {url}: {e}")

if __name__ == "__main__":
    import sys
    url = sys.argv[1] if len(sys.argv) > 1 else "https://cungnhaulamgiau.vn/tong-do-cat-toc-thong-minh-huawei-dynacare-hut-toc-tu-dong-khi-cat_p121951"
    scrape_product(url)