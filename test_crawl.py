# test_crawl.py - Phiên bản đồng bộ (dùng trực tiếp với PyCharm)
import sys
from src.scraper import scrape_product


def main():
    if len(sys.argv) > 1:
        url = sys.argv[1]
    else:
        url = "https://cungnhaulamgiau.vn/tong-do-cat-toc-thong-minh-huawei-dynacare-hut-toc-tu-dong-khi-cat_p121951"

    print(f"🔍 Đang test crawl sản phẩm:")
    print(f"   URL: {url}")
    print("-" * 60)

    scrape_product(url)

    print("\n✅ Test crawl hoàn tất!")


if __name__ == "__main__":
    main()