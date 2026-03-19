from fastapi import APIRouter

from app.api.v1.endpoints import auth, itinerary, itineraries, users

api_router = APIRouter()
api_router.include_router(auth.router, prefix="")
api_router.include_router(users.router, prefix="")
api_router.include_router(itinerary.router, prefix="")
api_router.include_router(itineraries.router, prefix="")
