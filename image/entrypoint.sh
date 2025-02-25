#!/bin/bash
set -e

./start_all.sh
./novnc_startup.sh

python http_server.py > /tmp/server_logs.txt 2>&1 &

# Start the FastAPI server
echo "Starting FastAPI server on port 7500..."
python -m computer_use_demo.server > /tmp/fastapi_stdout.log 2>&1 &

STREAMLIT_SERVER_PORT=8501 python -m streamlit run computer_use_demo/streamlit.py > /tmp/streamlit_stdout.log &

echo "✨ Computer Use Demo is ready!"
echo "➡️  Open http://localhost:8080 in your browser to begin"
echo "🔌 API server available at http://localhost:7500"

# Keep the container running
tail -f /dev/null
