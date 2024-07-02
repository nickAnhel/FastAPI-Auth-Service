from fastapi import APIRouter

from auth_service.auth.router import auth_router, user_router


def get_routes() -> list[APIRouter]:
    return [
        auth_router,
        user_router,
    ]
