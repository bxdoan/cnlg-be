"""
CNLG Price Tracker - Main FastAPI Application
FINAL FIX CORS CHO CHROME EXTENSION
"""
import re
from fastapi import FastAPI, Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response

from src.api.routes import router
from src.scheduler import scheduler

app = FastAPI(title="Price Tracker - cungnhaulamgiau.vn")

# ====================== THÊM CLASS NÀY TRƯỚC KHI TẠO APP ======================
class ChromeExtensionCORSMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        # Xử lý preflight OPTIONS ngay lập tức
        if request.method == "OPTIONS":
            response = Response()
        else:
            response = await call_next(request)

        origin = request.headers.get("origin")

        # Chỉ áp dụng cho Chrome Extension
        if origin and re.match(r"^chrome-extension://", origin):
            response.headers["Access-Control-Allow-Origin"] = origin
            response.headers["Access-Control-Allow-Credentials"] = "true"
        else:
            response.headers["Access-Control-Allow-Origin"] = "*"

        # Headers đầy đủ
        response.headers.update({
            "Access-Control-Allow-Methods": "GET, POST, PUT, DELETE, OPTIONS, PATCH",
            "Access-Control-Allow-Headers": "Authorization, Content-Type, Accept, X-Requested-With, X-CSRF-Token, Dnt",
            "Access-Control-Expose-Headers": "Content-Length, X-Requested-With",
            "Access-Control-Max-Age": "600",  # cache preflight 10 phút
        })

        return response
app.add_middleware(ChromeExtensionCORSMiddleware)

# ====================== ROUTES ======================
app.include_router(router, prefix="/api")


@app.get("/")
@app.get("/health")
async def health_check():
    return {"status": "ok", "message": "FINAL CORS ENABLED"}


@app.on_event("startup")
async def startup_event():
    scheduler.start()
    print("✅ Backend chạy với FINAL CUSTOM CORS cho Chrome Extension")


print("🚀 CNLG Backend started with FINAL CORS FIX")