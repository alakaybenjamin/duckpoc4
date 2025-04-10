from fastapi import FastAPI
from app.api.routes import router as api_router
from app.core.config import settings, logger
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
import httpx
import json

app = FastAPI(
    title=settings.PROJECT_NAME,
    description=settings.PROJECT_DESCRIPTION,
    version=settings.VERSION,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json"
)

# Add OpenTelemetry instrumentation to FastAPI
if settings.APPINSIGHTS_CONNECTION_STRING:
    FastAPIInstrumentor.instrument_app(app)

app.include_router(api_router)

@app.get("/health")
async def health_check():
    healthy = True
    services_status = {}
    
    async with httpx.AsyncClient() as client:
        # Check search service health
        try:
            search_response = await client.get(f"{settings.SEARCH_SERVICE_URL}/health")
            services_status["search_service"] = "healthy" if search_response.status_code == 200 else "unhealthy"
            if search_response.status_code != 200:
                healthy = False
                logger.error(f"Search service health check failed: {search_response.status_code} - {search_response.text}")
        except Exception as e:
            services_status["search_service"] = "unreachable"
            healthy = False
            logger.error(f"Failed to reach search service: {str(e)}")
        
        # Check user history service health
        try:
            user_history_response = await client.get(f"{settings.USER_HISTORY_SERVICE_URL}/health")
            services_status["user_history_service"] = "healthy" if user_history_response.status_code == 200 else "unhealthy"
            if user_history_response.status_code != 200:
                healthy = False
                logger.error(f"User history service health check failed: {user_history_response.status_code} - {user_history_response.text}")
        except Exception as e:
            services_status["user_history_service"] = "unreachable"
            healthy = False
            logger.error(f"Failed to reach user history service: {str(e)}")
    
    status = {
        "status": "healthy" if healthy else "unhealthy",
        "services": services_status
    }
    logger.info(f"Health check result: {json.dumps(status, indent=2)}")
    return status
 