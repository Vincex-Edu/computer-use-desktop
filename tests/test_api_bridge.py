#!/usr/bin/env python
"""
Test script for the API-to-Streamlit bridge.
This script sends a command to the FastAPI server and monitors its progress.
"""

import argparse
import base64
import logging
import os
import sys
import time
from datetime import datetime
from pathlib import Path

# Add the parent directory to the path to find the computer_use_demo module
sys.path.insert(0, str(Path(__file__).parent.parent))

import httpx

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(message)s", datefmt="%H:%M:%S"
)
logger = logging.getLogger(__name__)


def format_time(dt_str):
    """Format an ISO datetime string to a human-readable format."""
    dt = datetime.fromisoformat(dt_str)
    return dt.strftime("%Y-%m-%d %H:%M:%S")


def save_screenshots(screenshots, output_dir=None):
    """Save base64 encoded screenshots to files."""
    if not screenshots:
        return

    if not output_dir:
        output_dir = Path.cwd() / "screenshots"

    os.makedirs(output_dir, exist_ok=True)

    for i, screenshot in enumerate(screenshots):
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"screenshot_{timestamp}_{i+1}.png"
        filepath = output_dir / filename

        try:
            with open(filepath, "wb") as f:
                f.write(base64.b64decode(screenshot))
            logger.info(f"Screenshot saved to {filepath}")
        except Exception as e:
            logger.error(f"Error saving screenshot: {e}")


def main():
    parser = argparse.ArgumentParser(description="Test the API-to-Streamlit bridge")
    parser.add_argument(
        "--message", "-m", required=True, help="Message to send to Claude"
    )
    parser.add_argument("--host", default="localhost", help="API host")
    parser.add_argument("--port", default=7500, type=int, help="API port")
    parser.add_argument(
        "--api-key",
        default=os.environ.get("API_KEY", "your-secret-key"),
        help="API key for authentication",
    )
    parser.add_argument(
        "--save-screenshots", action="store_true", help="Save screenshots to files"
    )
    args = parser.parse_args()

    base_url = f"http://{args.host}:{args.port}"
    headers = {"X-API-Key": args.api_key, "Content-Type": "application/json"}

    logger.info(f"Sending command to API: {args.message}")

    # Submit the command
    try:
        with httpx.Client() as client:
            response = client.post(
                f"{base_url}/api/command",
                headers=headers,
                json={"message": args.message},
            )
            response.raise_for_status()
            command_data = response.json()
            command_id = command_data["command_id"]
    except Exception as e:
        logger.error(f"Error submitting command: {e}")
        return

    logger.info(f"Command submitted successfully. ID: {command_id}")
    logger.info("Monitoring command status...")

    # Poll for status changes
    last_status = None
    start_time = time.time()
    timeout = 300  # 5 minutes timeout

    while time.time() - start_time < timeout:
        try:
            with httpx.Client() as client:
                response = client.get(
                    f"{base_url}/api/command-status/{command_id}", headers=headers
                )
                response.raise_for_status()
                status_data = response.json()

                # Extract the current status
                bridge_status = status_data.get("bridge_status", {})
                result_store = status_data.get("result_store", {})

                current_status = None
                if bridge_status:
                    current_status = bridge_status.get("status")
                elif result_store:
                    current_status = result_store.get("status")

                # Log status changes
                if current_status != last_status:
                    logger.info(f"Status: {current_status}")

                    if bridge_status and "timestamp" in bridge_status:
                        logger.info(
                            f"  Queued at: {format_time(bridge_status['timestamp'])}"
                        )

                    if bridge_status and "completed_at" in bridge_status:
                        logger.info(
                            f"  Completed at: {format_time(bridge_status['completed_at'])}"
                        )

                    if (
                        current_status == "completed"
                        and bridge_status
                        and "result" in bridge_status
                    ):
                        result = bridge_status["result"]
                        if "text_response" in result:
                            logger.info("\nResponse from Claude:")
                            logger.info("-" * 40)
                            logger.info(result["text_response"])
                            logger.info("-" * 40)

                        if "screenshots" in result and result["screenshots"]:
                            screenshot_count = len(result["screenshots"])
                            logger.info(f"Screenshots captured: {screenshot_count}")

                            if args.save_screenshots:
                                save_screenshots(result["screenshots"])

                        # Command completed, we can stop polling
                        break

                last_status = current_status

        except Exception as e:
            logger.error(f"Error checking status: {e}")

        # Wait before polling again
        time.sleep(2)

    if time.time() - start_time >= timeout:
        logger.warning("Timeout reached. Command may still be processing.")


if __name__ == "__main__":
    main()
