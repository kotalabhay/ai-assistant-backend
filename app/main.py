"""FastAPI application factory and configuration."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from guard import SecurityMiddleware, SecurityConfig

from app.api.routes import auth, health, query
from app.core.config import settings

# Initialize fastapi-guard SecurityConfig with a higher rate limit for robust testing
guard_config = SecurityConfig(rate_limit=100)

app = FastAPI(
    title=settings.project_name,
    description="Backend API for AI Assistant Application",
    version="1.0.0",
)

# Apply CORS middleware using settings list
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Apply fastapi-guard security middleware
app.add_middleware(SecurityMiddleware, config=guard_config)

# Map grouped routes to application instances
app.include_router(auth.router, prefix=f"{settings.api_v1_prefix}/auth", tags=["auth"])
app.include_router(query.router, prefix=settings.api_v1_prefix, tags=["query"])
app.include_router(health.router, prefix=settings.api_v1_prefix, tags=["health"])

# Root redirect or message
@app.get("/", include_in_schema=False)
async def root():
    """Root redirect message."""
    return {"message": "AI Assistant API is running. Check /docs for documentation."}
