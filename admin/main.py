import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from admin.core.security import get_current_user
from admin.core.database import init_db
from admin.routers import candidates, vacancies, notes, analytics, telegram

logging.basicConfig(
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting admin panel backend...")
    init_db()
    yield
    logger.info("Shutting down...")


app = FastAPI(
    title="HR Admin Panel API",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(candidates.router, prefix="/candidates", tags=["candidates"],
                   dependencies=[Depends(get_current_user)])
app.include_router(vacancies.router, prefix="/vacancies", tags=["vacancies"],
                   dependencies=[Depends(get_current_user)])
app.include_router(notes.router, prefix="/notes", tags=["notes"],
                   dependencies=[Depends(get_current_user)])
app.include_router(analytics.router, prefix="/analytics", tags=["analytics"],
                   dependencies=[Depends(get_current_user)])
app.include_router(telegram.router, prefix="/telegram", tags=["telegram"],
                   dependencies=[Depends(get_current_user)])


@app.get("/health")
def health():
    return {"status": "ok"}
