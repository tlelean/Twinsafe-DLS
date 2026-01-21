from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from .config import FRONTEND_DIR, PDF_DIR
from .pages import automation, channel_names, live_trend, pdf_viewer, pressure_display, sew, test_details, test_details_production

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Page-specific routers
app.include_router(automation.router)
app.include_router(channel_names.router)
app.include_router(test_details.router)
app.include_router(live_trend.router)
app.include_router(pdf_viewer.router)
app.include_router(pressure_display.router)
app.include_router(sew.router)
app.include_router(test_details_production.router)

# Static / frontend
app.mount("/static", StaticFiles(directory=str(PDF_DIR.parent)), name="static")
app.mount("/", StaticFiles(directory=str(FRONTEND_DIR), html=True), name="frontend")