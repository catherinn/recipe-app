from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from database import init_db
from config import get_settings
from routes import auth, onboarding, profile, recipes, meal_plans

settings = get_settings()

app = FastAPI(
    title="Recipe App API",
    description="AI-powered personalized recipe and meal planning app",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.frontend_url, "http://localhost:5173"],
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
    init_db()


@app.get("/")
async def root():
    return {
        "message": "Recipe App API",
        "version": "1.0.0",
        "docs": "/docs"
    }


@app.get("/health")
async def health_check():
    return {"status": "healthy"}
