"""
Thread-safe storage for command results.
"""

import threading
from datetime import datetime, timedelta
from typing import Any, Dict, Optional


class ResultStore:
    """Thread-safe storage for command results."""

    def __init__(self):
        """Initialize an empty result store with a thread lock."""
        self._results: Dict[str, Dict[str, Any]] = {}
        self._lock = threading.Lock()

    def create_result(self, command_id: str, initial_data: Dict[str, Any]) -> None:
        """Create a new result entry with initial data."""
        with self._lock:
            self._results[command_id] = initial_data

    def get_result(self, command_id: str) -> Optional[Dict[str, Any]]:
        """Get a result by command ID."""
        with self._lock:
            return self._results.get(command_id)

    def update_result(self, command_id: str, update_data: Dict[str, Any]) -> None:
        """Update an existing result with new data."""
        with self._lock:
            if command_id in self._results:
                self._results[command_id].update(update_data)

    def cleanup_old_results(self, max_age_hours: int = 24) -> None:
        """Remove results older than the specified age."""
        cutoff_time = datetime.now() - timedelta(hours=max_age_hours)

        with self._lock:
            to_remove = []

            for command_id, result in self._results.items():
                completed_at = result.get("completed_at")
                if completed_at and isinstance(completed_at, datetime):
                    if completed_at < cutoff_time:
                        to_remove.append(command_id)

            for command_id in to_remove:
                del self._results[command_id]
