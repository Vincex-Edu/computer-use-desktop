# Computer Use Agent (CUA) - Server Component Design

## Overview

This document outlines the design for the server component that enables remote interaction with the Claude Computer Use demo environment. For the MVP, we will focus on exposing a simple API that allows a web application to send commands to Claude's computer use environment and receive results.

## Architecture

### MVP Architecture

```
[Web Application] → HTTP Requests → [Server Component] → [Claude Computer Use Environment]
```

The MVP architecture consists of:
1. **Server Component**: A FastAPI server added to the Computer Use demo
2. **Claude Environment**: The existing Docker-based environment that Claude can interact with
3. **Web Application**: Your existing fullstack website that sends commands to the server

## Server Component Specification

### Technology Stack
- **Framework**: FastAPI (Python-based, async-compatible)
- **Integration**: Runs alongside the existing Streamlit interface
- **Communication**: REST API endpoints for commands and results

### Implementation Location
The server component will be implemented directly within the Claude Computer Use demo Docker container, running in parallel with the Streamlit interface.

### Endpoints

#### 1. Submit Command
- **Endpoint**: `POST /api/command`
- **Purpose**: Submit a user command to Claude
- **Request Body**:
  ```json
  {
    "message": "Navigate to github.com",
    "session_id": "optional-session-identifier"
  }
  ```
- **Response**:
  ```json
  {
    "command_id": "unique-command-id",
    "status": "processing"
  }
  ```

#### 2. Get Result
- **Endpoint**: `GET /api/result/{command_id}`
- **Purpose**: Retrieve results of a previously submitted command
- **Response**:
  ```json
  {
    "status": "completed|failed|processing",
    "text_response": "Claude's text response",
    "screenshots": ["base64-encoded-image-1", "base64-encoded-image-2"],
    "completed_at": "ISO-timestamp"
  }
  ```

#### 3. Status Check
- **Endpoint**: `GET /api/status`
- **Purpose**: Check if the server is operational
- **Response**:
  ```json
  {
    "status": "ready|busy",
    "version": "1.0.0",
    "uptime": "10h 30m"
  }
  ```

## Implementation Plan

### 1. Modifications to Computer Use Demo

#### Add FastAPI Server
```python
# New file: computer_use_demo/api_server.py
from fastapi import FastAPI, BackgroundTasks
import uuid
import asyncio
from datetime import datetime
from typing import Dict, List, Optional

from computer_use_demo.loop import sampling_loop
from computer_use_demo.tools import ToolResult

app = FastAPI()

# In-memory storage for command results
command_results = {}

@app.post("/api/command")
async def submit_command(request: dict, background_tasks: BackgroundTasks):
    command_id = str(uuid.uuid4())
    command_results[command_id] = {"status": "processing"}

    background_tasks.add_task(
        process_command,
        command_id=command_id,
        message=request["message"],
        session_id=request.get("session_id")
    )

    return {"command_id": command_id, "status": "processing"}

@app.get("/api/result/{command_id}")
async def get_result(command_id: str):
    if command_id not in command_results:
        return {"error": "Command not found"}
    return command_results[command_id]

@app.get("/api/status")
async def status():
    return {
        "status": "ready",
        "version": "1.0.0",
        "uptime": "placeholder"  # To be implemented
    }

async def process_command(command_id: str, message: str, session_id: Optional[str] = None):
    # Implementation will integrate with sampling_loop from the demo
    # Simplified pseudocode shown
    try:
        # Process command using sampling_loop
        # Store results in command_results[command_id]
        pass
    except Exception as e:
        command_results[command_id] = {
            "status": "failed",
            "error": str(e)
        }
```

#### Update Entrypoint Script
Modify the container entrypoint to start both Streamlit and the FastAPI server:

```bash
# Start FastAPI server
uvicorn computer_use_demo.api_server:app --host 0.0.0.0 --port 8000 &

# Start existing Streamlit app
streamlit run computer_use_demo/streamlit.py
```

### 2. Integration with Computer Use Loop

Modify the `sampling_loop` function to be usable by both Streamlit and the API server. Example modifications to `loop.py`:

```python
# Add ability to process a single message without the interactive loop
async def process_single_command(
    message: str,
    *,
    model: str,
    provider: APIProvider,
    api_key: str,
    # ... other parameters similar to sampling_loop
):
    # Setup similar to sampling_loop
    # Process single message and return results
    # This can be called by the API server
```

## Security Considerations

For the MVP, basic security measures to implement:

1. **API Key Authentication**: Simple API key in the request header
   ```
   X-API-Key: your-secret-key
   ```

2. **Rate Limiting**: Limit requests per IP address

3. **Input Validation**: Validate all input parameters

## Testing

1. Manual testing with curl:
   ```bash
   curl -X POST http://localhost:8000/api/command \
     -H "Content-Type: application/json" \
     -H "X-API-Key: your-secret-key" \
     -d '{"message": "Navigate to github.com"}'
   ```

2. Integration testing with your web application

omputer_use_demo/
├── __init__.py
├── api/                       # New API module
│   ├── __init__.py
│   ├── main.py                # FastAPI app creation and configuration
│   ├── models.py              # Pydantic models for request/response
│   ├── routes/                # Route modules
│   │   ├── __init__.py
│   │   ├── commands.py        # Endpoints for submitting commands
│   │   └── status.py          # Status endpoints
│   ├── services/              # Business logic
│   │   ├── __init__.py
│   │   └── command_processor.py  # Integration with Claude
│   └── utils/                 # Utility functions
│       ├── __init__.py
│       └── result_storage.py  # Management of command results
├── loop.py                    # Existing code
├── streamlit.py               # Existing code
├── tools/                     # Existing code
│   └── ...
└── server.py                  # New entry point for the API server

## Deployment

For the MVP, the server will be exposed locally. The web application will need to know the IP/hostname and port to connect to it.

## Future Enhancements

These items are not part of the MVP but documented for future reference:

### 1. Desktop Application
- Electron-based wrapper for easier installation
- Auto-updates for the desktop app
- System tray integration for status and control

### 2. Advanced Communication
- WebSocket support for real-time updates
- Streaming responses
- Progress notifications

### 3. Security Enhancements
- Token-based authentication
- End-to-end encryption
- Permission scoping

### 4. Connectivity Solutions
- NAT traversal for connecting through firewalls
- Proxy service for web-to-desktop connections
- Connection management and reconnection logic

### 5. User Experience
- Local UI for monitoring status
- Configuration options
- Resource usage monitoring and throttling

## Usage Example (for Web App Integration)

```javascript
// Web app code example (JavaScript)
async function sendCommandToAgent(message) {
  const response = await fetch('http://localhost:8000/api/command', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'X-API-Key': 'your-secret-key'
    },
    body: JSON.stringify({ message })
  });

  const { command_id } = await response.json();
  return command_id;
}

async function pollForResults(command_id) {
  let complete = false;

  while (!complete) {
    const response = await fetch(`http://localhost:8000/api/result/${command_id}`, {
      headers: {
        'X-API-Key': 'your-secret-key'
      }
    });

    const result = await response.json();

    if (result.status !== 'processing') {
      complete = true;
      return result;
    }

    await new Promise(resolve => setTimeout(resolve, 2000)); // Poll every 2 seconds
  }
}
```
