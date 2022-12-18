from fastapi import APIRouter

from . import shows

router = APIRouter()

router.include_router(shows.router)
