"""
API routes for server status information.
"""

import time
from datetime import timedelta

from fastapi import APIRouter

from computer_use_demo.api.schema import StatusResponse

# Store server start time
START_TIME = time.time()

router = APIRouter()


def format_uptime() -> str:
    """Format the server uptime in a human-readable format."""
    uptime_seconds = time.time() - START_TIME
    uptime = timedelta(seconds=int(uptime_seconds))

    days = uptime.days
    hours, remainder = divmod(uptime.seconds, 3600)
    minutes, seconds = divmod(remainder, 60)

    if days > 0:
        return f"{days}d {hours}h {minutes}m {seconds}s"
    elif hours > 0:
        return f"{hours}h {minutes}m {seconds}s"
    elif minutes > 0:
        return f"{minutes}m {seconds}s"
    else:
        return f"{seconds}s"


@router.get("/status", response_model=StatusResponse)
async def get_status():
    """Get the current status of the server."""
    return StatusResponse(
        status="ready",  # This could be dynamic based on system load
        version="1.0.0",
        uptime=format_uptime(),
    )
