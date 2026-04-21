"""
CNLG Price Tracker - Main FastAPI Application
CORS CUSTOM MIDDLEWARE - FIX HOÀN TOÀN CHO CHROME EXTENSION
"""

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from src.api.routes import router
from src.scheduler import scheduler

app = FastAPI(title="Price Tracker - cungnhaulamgiau.vn")


# ====================== CUSTOM CORS MIDDLEWARE (MẠNH NHẤT) ======================
@app.middleware("http")
async def add_cors_headers(request: Request, call_next):
    # Xử lý Preflight (OPTIONS) request
    if request.method == "OPTIONS":
        response = JSONResponse(content={"message": "CORS Preflight OK"})
        response.headers["Access-Control-Allow-Origin"] = "*"
        response.headers["Access-Control-Allow-Methods"] = "GET, POST, OPTIONS"
        response.headers["Access-Control-Allow-Headers"] = "Authorization, Content-Type, Accept"
        response.headers["Access-Control-Max-Age"] = "600"
        return response

    # Xử lý các request bình thường
    response = await call_next(request)

    # Thêm CORS header cho mọi response
    response.headers["Access-Control-Allow-Origin"] = "*"
    response.headers["Access-Control-Allow-Methods"] = "GET, POST, OPTIONS"
    response.headers["Access-Control-Allow-Headers"] = "Authorization, Content-Type, Accept"
    response.headers["Access-Control-Expose-Headers"] = "*"

    return response


# ====================== ROUTES ======================
app.include_router(router, prefix="/api")


# ====================== HEALTH CHECK ======================
@app.get("/")
@app.get("/health")
async def health_check():
    return {
        "status": "ok",
        "message": "CNLG Backend is running - CUSTOM CORS ENABLED"
    }


# ====================== STARTUP ======================
@app.on_event("startup")
async def startup_event():
    scheduler.start()
    print("✅ Backend đã chạy - CUSTOM CORS đã kích hoạt cho Chrome Extension")


print("🚀 CNLG Backend started with STRONG CUSTOM CORS for Extension")