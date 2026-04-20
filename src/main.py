from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api.routes import router
from scheduler import scheduler

app = FastAPI(title="Price Tracker - cungnhaulamgiau.vn")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router, prefix="/api")

@app.on_event("startup")
async def startup_event():
    scheduler.start()
    print("✅ Backend đã chạy - API Key authentication bật")