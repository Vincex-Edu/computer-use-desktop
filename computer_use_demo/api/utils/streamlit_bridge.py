"""
Bridge utility for FastAPI to trigger Streamlit chat functionality.
Enables communication between FastAPI and Streamlit through a shared file.
"""

import json
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

# Use a location both services can access
COMMANDS_FILE = Path("/home/computeruse/.anthropic/api_commands.json")


def init_commands_file():
    """Initialize the commands file if it doesn't exist"""
    if not COMMANDS_FILE.parent.exists():
        COMMANDS_FILE.parent.mkdir(parents=True, exist_ok=True)

    if not COMMANDS_FILE.exists():
        write_commands([])


def read_commands() -> List[Dict[str, Any]]:
    """Read all pending commands"""
    init_commands_file()
    try:
        with open(COMMANDS_FILE) as f:
            return json.load(f)
    except (json.JSONDecodeError, FileNotFoundError):
        # Reset if corrupted
        write_commands([])
        return []


def write_commands(commands: List[Dict[str, Any]]):
    """Write commands to file"""
    init_commands_file()
    with open(COMMANDS_FILE, "w") as f:
        json.dump(commands, f)


def add_command(command_id: str, message: str, session_id: Optional[str] = None):
    """Add a new command to be processed by Streamlit"""
    commands = read_commands()
    commands.append(
        {
            "id": command_id,
            "message": message,
            "session_id": session_id,
            "status": "pending",
            "timestamp": datetime.now().isoformat(),
        }
    )
    write_commands(commands)
    return True


def mark_command_as_processing(command_id: str):
    """Mark a command as being processed"""
    commands = read_commands()
    for command in commands:
        if command["id"] == command_id:
            command["status"] = "processing"
            write_commands(commands)
            return True
    return False


def mark_command_as_completed(command_id: str, result: Dict[str, Any]):
    """Mark a command as completed with results"""
    commands = read_commands()
    for command in commands:
        if command["id"] == command_id:
            command["status"] = "completed"
            command["result"] = result
            command["completed_at"] = datetime.now().isoformat()
            write_commands(commands)
            return True
    return False


def get_pending_commands() -> List[Dict[str, Any]]:
    """Get all pending commands that need processing"""
    commands = read_commands()
    return [cmd for cmd in commands if cmd["status"] == "pending"]


def cleanup_old_commands(hours: int = 24):
    """Remove commands older than specified hours"""
    commands = read_commands()
    now = datetime.now()
    threshold = now.timestamp() - (hours * 3600)

    cleaned = []
    for cmd in commands:
        cmd_time = datetime.fromisoformat(cmd["timestamp"]).timestamp()
        if cmd_time > threshold:
            cleaned.append(cmd)

    write_commands(cleaned)
