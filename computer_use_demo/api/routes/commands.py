"""
API routes for command submission and result retrieval.
"""

import uuid
from typing import Callable

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException

from computer_use_demo.api.schema import (
    CommandRequest,
    CommandResponse,
    CommandStatus,
    ResultResponse,
)
from computer_use_demo.api.services.command_processor import CommandProcessor
from computer_use_demo.api.utils.result_store import ResultStore
from computer_use_demo.api.utils.streamlit_bridge import read_commands

router = APIRouter()

# Module-level singleton for ResultStore
_result_store: ResultStore | None = None

# Module-level singleton for CommandProcessor
_command_processor: CommandProcessor | None = None


def get_result_store() -> ResultStore:
    """Get or create the ResultStore instance."""
    global _result_store
    if _result_store is None:
        _result_store = ResultStore()
    return _result_store


def get_command_processor() -> CommandProcessor:
    """Get or create the CommandProcessor instance."""
    global _command_processor
    if _command_processor is None:
        _command_processor = CommandProcessor(get_result_store())
    return _command_processor


# Create dependency providers
result_store_dependency: Callable[[], ResultStore] = Depends(get_result_store)
command_processor_dependency: Callable[[], CommandProcessor] = Depends(
    get_command_processor
)


@router.post("/command", response_model=CommandResponse)
async def submit_command(
    request: CommandRequest,
    background_tasks: BackgroundTasks,
    result_store: ResultStore = result_store_dependency,
    command_processor: CommandProcessor = command_processor_dependency,
):
    """Submit a command to be processed by Claude."""
    command_id = str(uuid.uuid4())

    # Initialize the result
    result_store.create_result(command_id, {"status": CommandStatus.PROCESSING})

    # Process the command in the background
    background_tasks.add_task(
        command_processor.process_command,
        command_id=command_id,
        message=request.message,
        session_id=request.session_id,
    )

    return CommandResponse(command_id=command_id)


@router.get("/result/{command_id}", response_model=ResultResponse)
async def get_result(
    command_id: str, result_store: ResultStore = result_store_dependency
):
    """Get the result of a previously submitted command."""
    result = result_store.get_result(command_id)
    if not result:
        raise HTTPException(status_code=404, detail="Command not found")

    return ResultResponse(**result)


@router.get("/command-status/{command_id}")
async def get_command_status(
    command_id: str, result_store: ResultStore = result_store_dependency
):
    """Get detailed status of a command from both result store and bridge file."""
    # First check the bridge file
    commands = read_commands()
    bridge_command = None

    for command in commands:
        if command["id"] == command_id:
            bridge_command = command
            break

    # Then check the result store
    result = result_store.get_result(command_id)

    if not result and not bridge_command:
        raise HTTPException(status_code=404, detail="Command not found")

    # Combine information
    response = {
        "command_id": command_id,
        "result_store": result,
        "bridge_status": bridge_command,
    }

    return response


@router.get("/pending-commands")
async def get_pending_commands():
    """Get all commands that are pending or in progress."""
    # Read from the bridge file
    commands = read_commands()

    # Filter for pending or processing commands
    active_commands = [
        cmd for cmd in commands if cmd["status"] in ("pending", "processing")
    ]

    return {"pending_count": len(active_commands), "commands": active_commands}
