import os
from pydantic import BaseSettings
from typing import Optional
from dotenv import load_dotenv
import logging
import sys
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.sdk.resources import Resource
from azure.monitor.opentelemetry.exporter import AzureMonitorTraceExporter
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.instrumentation.httpx import HTTPXClientInstrumentor
from opentelemetry.instrumentation.logging import LoggingInstrumentor

# Load .env file
load_dotenv()

class Settings(BaseSettings):
    PROJECT_NAME: str = "Orchestrator Service"
    PROJECT_DESCRIPTION: str = "Service Orchestration for Search Platform"
    VERSION: str = "1.0.0"
    
    # Service URLs
    SEARCH_SERVICE_URL: str = os.getenv("SEARCH_SERVICE_URL", "http://search-service:5001")
    USER_HISTORY_SERVICE_URL: str = os.getenv("USER_HISTORY_SERVICE_URL", "http://user-history-service:5002")
    
    # Azure Application Insights
    APPINSIGHTS_CONNECTION_STRING: str = os.getenv("APPINSIGHTS_CONNECTION_STRING")
    
    class Config:
        env_file = ".env"

settings = Settings()

# Set up logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# Console handler
console_handler = logging.StreamHandler(sys.stdout)
console_handler.setLevel(logging.INFO)
console_formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
console_handler.setFormatter(console_formatter)
logger.addHandler(console_handler)

# Set up OpenTelemetry
if settings.APPINSIGHTS_CONNECTION_STRING:
    # Create a resource with service information
    resource = Resource.create({
        "service.name": settings.PROJECT_NAME,
        "service.version": settings.VERSION,
        "service.instance.id": os.getenv("HOSTNAME", "unknown"),
    })

    # Initialize TraceProvider with the resource
    trace_provider = TracerProvider(resource=resource)
    
    # Set up Azure Monitor exporter
    azure_exporter = AzureMonitorTraceExporter.from_connection_string(
        settings.APPINSIGHTS_CONNECTION_STRING
    )
    
    # Add BatchSpanProcessor with Azure Monitor exporter
    trace_provider.add_span_processor(BatchSpanProcessor(azure_exporter))
    
    # Set the global trace provider
    trace.set_tracer_provider(trace_provider)
    
    # Get a tracer
    tracer = trace.get_tracer(__name__)
    
    # Initialize automatic instrumentation
    HTTPXClientInstrumentor().instrument()
    LoggingInstrumentor().instrument()
    
    logger.info("OpenTelemetry with Azure Monitor configured successfully")
else:
    logger.warning("APPINSIGHTS_CONNECTION_STRING not found. Telemetry disabled.")
    tracer = trace.get_tracer(__name__)

# Log service URLs
logger.info(f"SEARCH_SERVICE_URL: {settings.SEARCH_SERVICE_URL}")
logger.info(f"USER_HISTORY_SERVICE_URL: {settings.USER_HISTORY_SERVICE_URL}") 