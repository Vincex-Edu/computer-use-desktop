"""
Main FastAPI application entry point and configuration.
"""

import logging
import os
import sys
from typing import Optional

from fastapi import Depends, FastAPI, Header, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from computer_use_demo.api.routes import commands, status

# Configure basic logging to stderr for Docker
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler(sys.stderr)],
)

# Setup logger
logger = logging.getLogger(__name__)
logger.info("FastAPI main module initialized")

# Load API key from environment
API_KEY = os.getenv("API_KEY", "your-secret-key")

# Create FastAPI app
app = FastAPI(
    title="Computer Use Agent API",
    description="API for interacting with Claude's computer use environment",
    version="1.0.0",
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, restrict this to specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# API key verification dependency
async def verify_api_key(x_api_key: Optional[str] = Header(None)):
    """Verify that the request includes a valid API key."""
    if not x_api_key or x_api_key != API_KEY:
        raise HTTPException(status_code=401, detail="Invalid or missing API key")
    return x_api_key


# Include routers with security
app.include_router(
    commands.router, prefix="/api", dependencies=[Depends(verify_api_key)]
)

app.include_router(status.router, prefix="/api", dependencies=[Depends(verify_api_key)])


@app.get("/")
async def root():
    """Root endpoint providing basic information about the API."""
    logger.info("Root endpoint accessed")
    return {
        "message": "Computer Use Agent API",
        "documentation": "/docs",
        "version": "1.0.0",
    }


@app.get("/health")
async def health_check():
    """Health check endpoint that doesn't require authentication."""
    logger.info("Health check endpoint accessed")
    return {"status": "healthy", "message": "FastAPI server is running"}
