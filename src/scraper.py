"""
CNLG Price Tracker Scraper
Fetches all products using internal APIs of cungnhaulamgiau.vn.
Supports full pagination based on total_records.
Saves products with thumbnail_url and price history.
"""
import time
from datetime import datetime

import requests
from src.database import SessionLocal
from src.models import Product, PriceHistory

# ==================== CONFIG ====================
GOOGLE_DOC_COOKIE_URL = "https://docs.google.com/document/d/1Iu-vrR3iu9zsSKa-UlG5dCqAXzHAltTY0WcY7UV7Dcc/export?format=txt"
PAGE_SIZE = 24
CNLG_URL = "https://cungnhaulamgiau.vn"
IMG_URL= "https://r6i-dl.pen.dropbuy.vn"
CNLG_API = f"{CNLG_URL}/api/proxy/bff"


def load_cookies_from_google_doc() -> str:
    """Load dynamic cookies from Google Doc (updated manually 1-2 days)."""
    try:
        r = requests.get(GOOGLE_DOC_COOKIE_URL, timeout=10)
        r.raise_for_status()
        cookie_string = r.content.decode('utf-8-sig').strip().replace('\ufeff', '')
        print(f"[INFO] Loaded cookies from Google Doc ({len(cookie_string)} chars)")
        return cookie_string
    except Exception as e:
        print(f"[ERROR] Failed to load cookies: {e}")
        return ""


def get_headers() -> dict:
    """Return headers required by CNLG internal APIs."""
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


def build_price_query(items: list) -> list:
    """Build payload for /variations/get-price API."""
    return [
        {
            "product_id": item.get("product_id"),
            "variation_id": item.get("unique_id") or item.get("variation_id"),
            "sku": item.get("sku")
        }
        for item in items
    ]


def save_product_and_price(db, product_item: dict, price_item: dict):
    """Save/Update Product with thumbnail_url and create PriceHistory record."""
    sku = price_item.get("sku")
    title = product_item.get("product_name")
    thumbnail_url = product_item.get("res_thumbnail_url")

    retail_price = price_item.get("fe_price_public")
    current_price = int(price_item.get("fe_price_override") or price_item.get("fe_price_group") or 0)
    original_price = int(price_item.get("fe_price_group") or 0)
    discount_percent = round((original_price - current_price) / original_price * 100) if original_price > current_price > 0 else 0

    print(f"\n[CRAWL SUCCESS]")
    print(f"   Title      : {title}")
    print(f"   SKU        : {sku}")
    print(f"   Current    : {current_price:,} ₫")
    print(f"   Original   : {original_price:,} ₫")
    print(f"   Thumbnail  : {thumbnail_url or 'N/A'}")

    # Upsert Product
    product = db.query(Product).filter(Product.sku == sku).first()
    if not product:
        product = Product(
            sku=sku,
            url=product_item.get('product_id'),
            title=title,
            thumbnail_url=thumbnail_url
        )
        db.add(product)
    else:
        product.title = title
        product.thumbnail_url = thumbnail_url
        product.last_crawled = datetime.utcnow()

    db.commit()

    # Save price history
    history = PriceHistory(
        sku=sku,
        retail_price=retail_price,
        original_price=original_price,
        current_price=current_price,
        discount_percent=discount_percent
    )
    db.add(history)
    db.commit()


def scrape_all_products():
    """Main function: crawl ALL products with full pagination."""
    start_time = time.time()

    try:
        headers = get_headers()
        db = SessionLocal()

        page_num = 1
        total_records = 0

        while True:
            # Step 1: Search API
            search_payload = {
                "is_flash_sale": "F",
                "page_num": page_num,
                "page_size": PAGE_SIZE
            }

            print(f"[INFO] Fetching page {page_num} ...")
            search_resp = requests.post(
                f"{CNLG_API}/variations/search",
                headers=headers,
                json=search_payload,
                timeout=15
            )

            if search_resp.status_code != 200 or not search_resp.json().get("success"):
                print(f"[ERROR] Search API failed: {search_resp.status_code}")
                break

            search_data = search_resp.json()["data"]
            items = search_data.get("items", [])

            if page_num == 1:
                total_records = search_data.get("total_records", 0)
                print(f"[INFO] Total records found: {total_records}")

            if not items:
                break

            # Step 2: Get price API
            price_payload = {"items": build_price_query(items)}
            price_resp = requests.post(
                f"{CNLG_API}/variations/get-price",
                headers=headers,
                json=price_payload,
                timeout=15
            )

            if price_resp.status_code != 200:
                print(f"[ERROR] Get-price API failed: {price_resp.status_code}")
                break

            price_data = price_resp.json()
            if not price_data.get("success") or not price_data.get("data"):
                print("[ERROR] No price data returned")
                break

            # Step 3: Save to DB
            for idx, price_item in enumerate(price_data["data"]):
                product_item = items[idx]
                save_product_and_price(db, product_item, price_item)

            # Check if finished
            if len(items) < PAGE_SIZE or (page_num * PAGE_SIZE >= total_records):
                break

            page_num += 1

        end_time = time.time()
        total_seconds = end_time - start_time
        print(f"\n[SUCCESS] Finished crawling {total_records} products.")
        print(f"          Total execution time: {total_seconds:.2f} seconds ({total_seconds/60:.2f} minutes)")
        db.close()

    except Exception as e:
        print(f"[ERROR] Scraper failed: {e}")
        end_time = time.time()
        print(f"          Execution time until error: {end_time - start_time:.2f} seconds")