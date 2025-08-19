from fastapi import APIRouter
from .auth import router as auth_router
from .users import router as users_router
from .companies import router as companies_router

api_router = APIRouter(prefix="/api/v1")

api_router.include_router(auth_router)
api_router.include_router(users_router)
api_router.include_router(companies_router)