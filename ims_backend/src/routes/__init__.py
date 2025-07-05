from .auth import router as auth_router
from .users import router as users_router
from .storerooms import router as storerooms_router
from .items import router as items_router
from .transfers import router as transfers_router

__all__ = [
    "auth_router",
    "users_router", 
    "storerooms_router",
    "items_router",
    "transfers_router"
]
