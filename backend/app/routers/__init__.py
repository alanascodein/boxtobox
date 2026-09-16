"""API routers."""
from . import auth as auth_routes
from . import listings as listings_routes
from . import orders as orders_routes
from . import vendor as vendor_routes
from . import public as public_routes
from . import admin as admin_routes

api_router = auth_routes.router.include_router(listings_routes.router)
# assembled explicitly below to keep prefixes/tags clean
from fastapi import APIRouter

api_router = APIRouter()
api_router.include_router(auth_routes.router)
api_router.include_router(public_routes.router)
api_router.include_router(listings_routes.router)
api_router.include_router(orders_routes.router)
api_router.include_router(vendor_routes.router)
api_router.include_router(admin_routes.router)
