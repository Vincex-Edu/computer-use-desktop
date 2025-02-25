"""
Service for processing commands using the Claude computer use environment.
"""

from datetime import datetime
from typing import Optional

from computer_use_demo.api.schema import CommandStatus
from computer_use_demo.api.utils.result_store import ResultStore
from computer_use_demo.api.utils.streamlit_bridge import add_command
from computer_use_demo.loop import (
    APIProvider,
)


class CommandProcessor:
    """Service for processing commands using Claude's computer use environment."""

    def __init__(self, result_store: ResultStore):
        """Initialize the command processor with a result store."""
        self.result_store = result_store

    async def process_command(
        self,
        command_id: str,
        message: str,
        session_id: Optional[str] = None,
        model: str = "claude-3-7-sonnet-20250219",
        provider: APIProvider = APIProvider.ANTHROPIC,
        api_key: str = "",
        system_prompt_suffix: str = "",
        max_tokens: int = 4096,
        tool_version: str = "computer_use_20250124",
        thinking_budget: Optional[int] = None,
    ):
        """Queue a command for processing by Streamlit."""
        try:
            # Add the command to the shared queue for Streamlit to process
            add_command(command_id, message, session_id)

            # Update result store with queued status
            self.result_store.update_result(
                command_id,
                {
                    "status": CommandStatus.PROCESSING,
                    "message": "Command queued for processing by Streamlit interface. Please check status later for results.",
                    "queued_at": datetime.now().isoformat(),
                },
            )

            return True

        except Exception as e:
            self.result_store.update_result(
                command_id,
                {
                    "status": CommandStatus.FAILED,
                    "error": f"Failed to queue command: {str(e)}",
                    "completed_at": datetime.now().isoformat(),
                },
            )
            return False
