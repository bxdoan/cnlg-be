from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger
from apscheduler.triggers.cron import CronTrigger
from database import SessionLocal
from models import Product
from scraper import scrape_product
import asyncio
from datetime import datetime
from sqlalchemy import text

scheduler = AsyncIOScheduler()

async def crawl_all_products():
    print(f"🚀 Crawl tất cả sản phẩm lúc {datetime.now()}")
    db = SessionLocal()
    products = db.query(Product).all()
    db.close()
    for product in products:
        await scrape_product(product.url)
        await asyncio.sleep(4)

async def cleanup_old_data():
    print(f"🧹 Cleanup data > 90 ngày lúc {datetime.now()}")
    db = SessionLocal()
    result = db.execute(text("DELETE FROM price_history WHERE timestamp < NOW() - INTERVAL '90 days'"))
    db.commit()
    db.close()
    print(f"✅ Đã xóa {result.rowcount} records cũ")

# Crawl 3 lần/ngày (8h, 14h, 20h)
scheduler.add_job(crawl_all_products, CronTrigger(hour="8,14,20", minute=0))
scheduler.add_job(cleanup_old_data, CronTrigger(hour=3, minute=0))