from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from .config import FRONTEND_DIR, PDF_DIR
from .pages import live_trend, pdf_viewer, start_dialog, test_details

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Page-specific routers
app.include_router(live_trend.router)
app.include_router(pdf_viewer.router)
app.include_router(start_dialog.router)
app.include_router(test_details.router)

# Static / frontend
app.mount("/static", StaticFiles(directory=str(PDF_DIR.parent)), name="static")
app.mount("/", StaticFiles(directory=str(FRONTEND_DIR), html=True), name="frontend")