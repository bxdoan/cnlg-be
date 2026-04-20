#!/bin/bash
# ================================================
# DEV SCRIPT - CNLG Price Tracker
# ================================================

set -e

echo "🚀 CNLG Price Tracker - Local Dev Script"

COMMAND=${1:-"run"}

case $COMMAND in
    "install")
        echo "📦 Installing dependencies..."
        pipenv install
        echo "✅ Done! Chạy 'pipenv shell' để vào môi trường."
        ;;

    "migrate")
        echo "🔄 Running database migrations..."
        pipenv run alembic upgrade head
        echo "✅ Migration completed!"
        ;;

    "test-crawl")
        echo "🧪 Testing crawl 1 sản phẩm..."
        URL=${2:-"https://cungnhaulamgiau.vn/tong-do-cat-toc-thong-minh-huawei-dynacare-hut-toc-tu-dong-khi-cat_p121951"}
        echo "URL: $URL"
        pipenv run python test_crawl.py "$URL"
        ;;

    "run")
        echo "🌐 Starting FastAPI server..."
        pipenv run uvicorn main:app --host 0.0.0.0 --port 8000 --reload
        ;;

    "shell")
        pipenv shell
        ;;

    *)
        echo "❓ Usage:"
        echo "   ./dev.sh install          # Cài dependencies"
        echo "   ./dev.sh migrate          # Chạy migration"
        echo "   ./dev.sh test-crawl       # Test crawl (mặc định)"
        echo "   ./dev.sh test-crawl [URL] # Test crawl với link khác"
        echo "   ./dev.sh run              # Chạy server"
        echo "   ./dev.sh shell            # Vào shell pipenv"
        ;;
esac