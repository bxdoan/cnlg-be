from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from src.database import SessionLocal
from src.scraper import scrape_all_products
from datetime import datetime
from sqlalchemy import text

scheduler = AsyncIOScheduler()

async def cleanup_old_data():
    print(f"🧹 Cleanup data > 90 ngày lúc {datetime.now()}")
    db = SessionLocal()
    result = db.execute(text("DELETE FROM price_history WHERE timestamp < NOW() - INTERVAL '90 days'"))
    db.commit()
    db.close()
    print(f"✅ Đã xóa {result.rowcount} records cũ")

# Crawl 3 lần/ngày (8h, 14h, 20h)
scheduler.add_job(scrape_all_products, CronTrigger(hour="8,14,20", minute=0))
scheduler.add_job(cleanup_old_data, CronTrigger(hour=3, minute=0))