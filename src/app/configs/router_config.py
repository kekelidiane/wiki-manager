# src/app/configs/router_config.py
from fastapi import APIRouter

from app.api.routes.health.health_check_api import router

api_router = APIRouter(prefix="/api/v1/wiki")

api_router.include_router(router, tags=["Health"])
