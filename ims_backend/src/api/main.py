from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from ..database import create_tables
from ..routes import auth_router, users_router, storerooms_router, items_router, transfers_router
from ..routes.dashboard import router as dashboard_router

app = FastAPI(
    title="Inventory Management System API",
    description="REST API for managing inventory across multiple storeroom locations",
    version="1.0.0",
    openapi_tags=[
        {
            "name": "Authentication",
            "description": "User authentication and authorization endpoints"
        },
        {
            "name": "Users",
            "description": "User management endpoints"
        },
        {
            "name": "Items",
            "description": "Item management endpoints"
        },
        {
            "name": "Storerooms",
            "description": "Storeroom management endpoints"
        },
        {
            "name": "Transfers",
            "description": "Transfer management endpoints"
        },
        {
            "name": "Dashboard",
            "description": "Dashboard statistics and overview endpoints"
        }
    ]
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth_router)
app.include_router(users_router)
app.include_router(items_router)
app.include_router(storerooms_router)
app.include_router(transfers_router)
app.include_router(dashboard_router)

@app.on_event("startup")
async def startup_event():
    """Initialize database tables on startup"""
    create_tables()

@app.get("/", tags=["Health"])
def health_check():
    """Health check endpoint"""
    return {"message": "Inventory Management System API is running", "status": "healthy"}
