"""
Entry point for running the Computer Use Agent FastAPI server.
"""

import logging
import os
import sys
from pathlib import Path

import uvicorn

# Create log directory if it doesn't exist
log_dir = Path("/tmp")
log_dir.mkdir(exist_ok=True)

# Ensure bridge directory exists
bridge_dir = Path("/home/computeruse/.anthropic")
bridge_dir.mkdir(exist_ok=True, parents=True)

# Configure file handler to write logs to a file
file_handler = logging.FileHandler(log_dir / "fastapi_detailed.log")
file_handler.setLevel(logging.DEBUG)

# Configure console handler
console_handler = logging.StreamHandler(sys.stdout)
console_handler.setLevel(logging.INFO)

# Create formatter
formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
file_handler.setFormatter(formatter)
console_handler.setFormatter(formatter)

# Configure root logger
logging.basicConfig(
    level=logging.DEBUG,
    handlers=[file_handler, console_handler],
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)

# Configure specific loggers
for logger_name in ["uvicorn", "uvicorn.access", "fastapi", "computer_use_demo.api"]:
    logger = logging.getLogger(logger_name)
    logger.handlers = []
    logger.propagate = True
    logger.setLevel(logging.DEBUG)

logger = logging.getLogger(__name__)


def main():
    """Run the FastAPI server."""
    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", "7500"))

    logger.info(f"Starting Computer Use Agent API server on {host}:{port}")
    logger.info(f"Bridge directory: {bridge_dir}")

    try:
        uvicorn.run(
            "computer_use_demo.api.main:app",
            host=host,
            port=port,
            reload=os.getenv("ENVIRONMENT") == "development",
            log_level="debug",
            access_log=True,
        )
    except Exception as e:
        logger.error(f"Error starting FastAPI server: {str(e)}", exc_info=True)
        raise


if __name__ == "__main__":
    main()
