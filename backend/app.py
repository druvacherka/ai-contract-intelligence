from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from routes.health import router as health_router
from routes.analyze import router as analyze_router
from routes.upload import router as upload_router
from routes.analyze_file import router as analyze_file_router

app = FastAPI(
    title="AI Contract Intelligence Backend"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health_router)
app.include_router(analyze_router)
app.include_router(upload_router)
app.include_router(analyze_file_router)