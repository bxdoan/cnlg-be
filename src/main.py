"""
CNLG Price Tracker - Main FastAPI Application
FINAL FIX CORS CHO CHROME EXTENSION
"""

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from src.api.routes import router
from src.scheduler import scheduler

app = FastAPI(title="Price Tracker - cungnhaulamgiau.vn")


# ====================== FINAL CUSTOM CORS (STRONGEST) ======================
@app.middleware("http")
async def final_cors_middleware(request: Request, call_next):
    # Xử lý Preflight OPTIONS
    if request.method == "OPTIONS":
        response = JSONResponse(content={"status": "ok"})
        response.headers["Access-Control-Allow-Origin"] = "*"
        response.headers["Access-Control-Allow-Methods"] = "GET, POST, OPTIONS"
        response.headers["Access-Control-Allow-Headers"] = "*"
        response.headers["Access-Control-Max-Age"] = "86400"
        return response

    response = await call_next(request)

    # Thêm header cho mọi response
    response.headers["Access-Control-Allow-Origin"] = "*"
    response.headers["Access-Control-Allow-Methods"] = "GET, POST, OPTIONS"
    response.headers["Access-Control-Allow-Headers"] = "*"
    response.headers["Access-Control-Expose-Headers"] = "*"

    return response


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