from playwright.async_api import async_playwright
from database import SessionLocal
from models import Product, PriceHistory
import asyncio
from datetime import datetime

async def scrape_product(url: str):
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        await page.goto(url, wait_until="networkidle", timeout=60000)

        try:
            # === TODO: Mở trang sản phẩm → F12 → thay selector chính xác ===
            sku_text = await page.locator("text=SKU:").locator("..").inner_text()
            sku = sku_text.replace("SKU:", "").strip()

            retail_price = None
            try:
                retail_text = await page.locator(".retail-price, .price-label, .original-price del").first.inner_text()
                retail_price = int(''.join(filter(str.isdigit, retail_text)))
            except:
                pass

            original_price = None
            try:
                original_text = await page.locator(".price del .amount, .original-price").first.inner_text()
                original_price = int(''.join(filter(str.isdigit, original_text)))
            except:
                pass

            current_text = await page.locator(".woocommerce-Price-amount.amount, .price .amount").first.inner_text()
            current_price = int(''.join(filter(str.isdigit, current_text)))

            title = await page.title()

            discount = None
            if retail_price and current_price and retail_price > current_price:
                discount = round((retail_price - current_price) / retail_price * 100)

            db = SessionLocal()
            product = db.query(Product).filter(Product.sku == sku).first()
            if not product:
                product = Product(sku=sku, url=url, title=title)
                db.add(product)
            else:
                product.last_crawled = datetime.utcnow()

            history = PriceHistory(
                sku=sku,
                retail_price=retail_price,
                original_price=original_price,
                current_price=current_price,
                discount_percent=discount
            )
            db.add(history)
            db.commit()
            db.close()

            print(f"✅ Crawled {sku} | Lẻ:{retail_price:,} | Gốc:{original_price:,} | Hiện:{current_price:,}đ")
        except Exception as e:
            print(f"❌ Error crawling {url}: {e}")
        finally:
            await browser.close()