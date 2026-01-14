from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from database import init_db
from config import get_settings
from routes import auth, onboarding, profile, recipes, meal_plans
import os

settings = get_settings()

app = FastAPI(
    title="Recipe App API",
    description="AI-powered personalized recipe and meal planning app",
    version="1.0.0"
)

# Allow all hosts for development
from starlette.middleware.trustedhost import TrustedHostMiddleware
app.add_middleware(TrustedHostMiddleware, allowed_hosts=["*"])

# CORS middleware - Allow all origins for development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify exact origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router, prefix="/api/auth", tags=["Authentication"])
app.include_router(onboarding.router, prefix="/api/onboarding", tags=["Onboarding"])
app.include_router(profile.router, prefix="/api/profile", tags=["Profile"])
app.include_router(recipes.router, prefix="/api/recipes", tags=["Recipes"])
app.include_router(meal_plans.router, prefix="/api/meal-plans", tags=["Meal Plans"])


@app.on_event("startup")
async def startup_event():
    """Initialize database on startup"""
    try:
        init_db()
        print("✓ Database initialized successfully")
    except Exception as e:
        print(f"⚠ Error initializing database: {e}")
        # Don't crash - let the app start anyway


@app.get("/")
async def root():
    return {
        "message": "Recipe App API",
        "version": "1.0.0",
        "docs": "/docs"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint for Railway and monitoring"""
    return {
        "status": "healthy",
        "service": "recipe-app-api",
        "version": "1.0.0"
    }


# Serve static files from frontend build (for production deployment)
dist_path = os.path.join(os.path.dirname(__file__), "dist")
if os.path.exists(dist_path):
    # Mount static assets (JS, CSS, images, etc.)
    app.mount("/assets", StaticFiles(directory=os.path.join(dist_path, "assets")), name="assets")

    # Catch-all route to serve index.html for client-side routing
    # This must be after all API routes
    @app.get("/{full_path:path}")
    async def serve_frontend(full_path: str):
        """Serve the React frontend for all non-API routes"""
        # Don't serve frontend for API routes or docs
        if full_path.startswith("api/") or full_path.startswith("docs") or full_path.startswith("openapi.json"):
            return {"error": "Not found"}

        # Serve index.html for all other routes (client-side routing)
        index_path = os.path.join(dist_path, "index.html")
        if os.path.exists(index_path):
            return FileResponse(index_path)

        return {"error": "Frontend not built"}
