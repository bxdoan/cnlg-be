#!/bin/bash
# ================================================
# DEV SCRIPT - Local development & test
# ================================================

set -e

echo "🚀 CNLG Price Tracker - Local Dev Script"

COMMAND=${1:-"run"}

case $COMMAND in
    "install")
        echo "📦 Installing dependencies with Pipenv..."
        pipenv install
        echo "✅ Done! Run 'pipenv shell' để vào môi trường."
        ;;

    "migrate")
        echo "🔄 Running database migrations..."
        pipenv run alembic upgrade head
        echo "✅ Migration completed!"
        ;;

    "test-crawl")
        echo "🧪 Testing crawl 1 sản phẩm..."
        if [ -z "$2" ]; then
            URL="https://cungnhaulamgiau.vn/tong-do-cat-toc-thong-minh-huawei-dynacare-hut-toc-tu-dong-khi-cat_p121951"
        else
            URL="$2"
        fi
        echo "Testing URL: $URL"
        pipenv run python -c "
import asyncio
from scraper import scrape_product
asyncio.run(scrape_product('$URL'))
"
        ;;

    "run")
        echo "🌐 Starting FastAPI server locally..."
        pipenv run uvicorn main:app --host 0.0.0.0 --port 8000 --reload
        ;;

    "shell")
        echo "🐚 Opening Pipenv shell..."
        pipenv shell
        ;;

    *)
        echo "❓ Usage:"
        echo "   ./dev.sh install          # Cài dependencies"
        echo "   ./dev.sh migrate          # Chạy migration"
        echo "   ./dev.sh test-crawl       # Test crawl (dùng link mặc định)"
        echo "   ./dev.sh test-crawl [URL] # Test crawl với link cụ thể"
        echo "   ./dev.sh run              # Chạy server local"
        echo "   ./dev.sh shell            # Vào môi trường pipenv"
        ;;
esac