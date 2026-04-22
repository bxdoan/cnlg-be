"""
CNLG Price Tracker - Main FastAPI Application
FINAL CUSTOM CORS (Chrome Extension + Website)
"""

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware  # vẫn giữ để an toàn
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response

from src.api.routes import router
from src.scheduler import scheduler

app = FastAPI(title="Price Tracker - cungnhaulamgiau.vn")


# ====================== CUSTOM CORS MIDDLEWARE (ROBUST NHẤT) ======================
class CustomCORSMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        # Xử lý preflight OPTIONS ngay
        if request.method == "OPTIONS":
            response = Response()
        else:
            response = await call_next(request)

        origin = request.headers.get("origin")

        # Danh sách origin được phép
        allowed_origins = [
            "https://cungnhaulamgiau.vn",
            "http://cungnhaulamgiau.vn",
        ]

        if origin and (origin in allowed_origins or origin.startswith("chrome-extension://")):
            response.headers["Access-Control-Allow-Origin"] = origin
            response.headers["Access-Control-Allow-Credentials"] = "true"
        else:
            response.headers["Access-Control-Allow-Origin"] = "*"

        # Headers đầy đủ
        response.headers.update({
            "Access-Control-Allow-Methods": "GET, POST, PUT, DELETE, OPTIONS, PATCH",
            "Access-Control-Allow-Headers": "Authorization, Content-Type, Accept, X-Requested-With, X-CSRF-Token, Dnt",
            "Access-Control-Expose-Headers": "Content-Length, X-Requested-With",
            "Access-Control-Max-Age": "600",
        })

        return response


# ====================== THÊM MIDDLEWARE ======================
app.add_middleware(CustomCORSMiddleware)

# ====================== ROUTES ======================
app.include_router(router, prefix="/api")


# ====================== HEALTH CHECK ======================
@app.get("/")
@app.get("/health")
async def health_check():
    return {"status": "ok", "message": "FINAL CUSTOM CORS ENABLED"}


# ====================== STARTUP ======================
@app.on_event("startup")
async def startup_event():
    scheduler.start()
    print("✅ Backend chạy với FINAL CUSTOM CORS cho Chrome Extension")


print("🚀 CNLG Backend started with FINAL CUSTOM CORS FIX")