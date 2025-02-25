"""
Pydantic schemas for API request and response validation.
"""

from datetime import datetime
from enum import Enum
from typing import List, Optional

from pydantic import BaseModel


class CommandStatus(str, Enum):
    """Status of a command submitted to the Computer Use Agent."""

    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


class CommandRequest(BaseModel):
    """Request model for submitting a command to the Computer Use Agent."""

    message: str
    session_id: Optional[str] = None


class CommandResponse(BaseModel):
    """Response model after submitting a command."""

    command_id: str
    status: CommandStatus = CommandStatus.PROCESSING


class ResultResponse(BaseModel):
    """Response model for retrieving command results."""

    status: CommandStatus
    text_response: Optional[str] = None
    screenshots: List[str] = []
    completed_at: Optional[datetime] = None
    error: Optional[str] = None


class StatusResponse(BaseModel):
    """Response model for the server status endpoint."""

    status: str = "ready"
    version: str = "1.0.0"
    uptime: str
