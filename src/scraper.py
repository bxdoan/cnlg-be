import requests
import json
from src.database import SessionLocal
from src.models import Product, PriceHistory
from datetime import datetime

HEADERS = {
    "Accept": "application/json, text/plain, */*",
    "Accept-Language": "vi,en;q=0.9",
    "Content-Type": "application/json",
    "Origin": "https://cungnhaulamgiau.vn",
    "Referer": "https://cungnhaulamgiau.vn/",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.0.0 Safari/537.36",
    "x-tenant-domain": "cungnhaulamgiau.vn",
    "x-tenant-id": "1",
}

def scrape_product(url: str):
    try:
        # Bước 1: Lấy product_id từ URL (ví dụ: ..._p129310 → 129310)
        product_id = url.split("_p")[-1].split("?")[0].strip()
        if not product_id.isdigit():
            print("❌ Không tìm thấy product_id trong URL")
            return

        # Bước 2: Gọi API get-price (cách nhanh nhất)
        payload = {
            "items": [{
                "product_id": int(product_id),
                "variation_id": None,   # trang sẽ tự xử lý nếu không có
                "sku": None
            }]
        }

        response = requests.post(
            "https://cungnhaulamgiau.vn/api/proxy/bff/variations/get-price",
            headers=HEADERS,
            json=payload,
            timeout=15
        )

        if response.status_code != 200:
            print(f"❌ API error {response.status_code}")
            return

        data = response.json()
        if not data.get("success") or not data.get("data"):
            print("❌ API trả về không thành công")
            return

        item = data["data"][0]

        sku = item.get("sku")
        current_price = int(item.get("fe_price_override") or item.get("fe_price_public") or 0)
        original_price = int(item.get("fe_price_public") or 0)

        print(f"✅ Crawled thành công!")
        print(f"   SKU          : {sku}")
        print(f"   Giá hiện tại : {current_price:,} ₫")
        print(f"   Giá gốc      : {original_price:,} ₫")

        # Bước 3: Lưu vào database
        db = SessionLocal()
        product = db.query(Product).filter(Product.sku == sku).first()
        if not product:
            product = Product(sku=sku, url=url, title=f"Product {sku}")
            db.add(product)

        history = PriceHistory(
            sku=sku,
            retail_price=original_price,      # giá lẻ cao nhất
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
    session = SessionLocal()