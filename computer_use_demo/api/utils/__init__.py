"""
Utility functions and classes for the API server.
"""

import logging
import os
from pathlib import Path

# Ensure the bridge directory exists
# Use user's home directory for the bridge directory
BRIDGE_DIR = Path.home() / ".computer_use_demo" / ".anthropic"
os.makedirs(BRIDGE_DIR, exist_ok=True)

logger = logging.getLogger(__name__)
logger.info(f"Initialized API utilities. Bridge directory: {BRIDGE_DIR}")
