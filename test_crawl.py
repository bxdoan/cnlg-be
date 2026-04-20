import asyncio
import sys
from src.scraper import scrape_product


async def main():
    if len(sys.argv) > 1:
        url = sys.argv[1]
    else:
        url = "https://cungnhaulamgiau.vn/tong-do-cat-toc-thong-minh-huawei-dynacare-hut-toc-tu-dong-khi-cat_p121951"

    print(f"🔍 Đang test crawl: {url}")
    await scrape_product(url)


if __name__ == "__main__":
    asyncio.run(main())