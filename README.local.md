# Local Setup for Anthropic Computer Use Demo

This document provides instructions for running the Anthropic Computer Use Demo locally.

## Prerequisites

- Docker installed and running
- An Anthropic API key (stored in `.env` file)

## Quick Start

1. Make sure your `.env` file contains your Anthropic API key:
   ```
   ANTHROPIC_API_KEY=your_api_key_here
   ```

2. Run the demo:
   ```bash
   ./run.sh
   ```

3. Access the demo:
   - Combined interface: [http://localhost:8080](http://localhost:8080)
   - Streamlit interface only: [http://localhost:8501](http://localhost:8501)
   - Desktop view only: [http://localhost:6080/vnc.html](http://localhost:6080/vnc.html)
   - Direct VNC connection: `vnc://localhost:5900` (for VNC clients)

4. To stop the demo:
   ```bash
   ./stop.sh
   ```

## Troubleshooting

- If you encounter port conflicts, make sure no other applications are using ports 5900, 8501, 6080, or 8080.
- If the Docker build fails, check your Docker installation and ensure you have sufficient disk space.
- If the container fails to start, check that your API key is valid and properly set in the `.env` file.

## Development

For development purposes, the local `computer_use_demo` directory is mounted into the container. Any changes you make to the code will be reflected in the running container.

## Additional Information

For more detailed information about the project, refer to the main [README.md](README.md) file.
