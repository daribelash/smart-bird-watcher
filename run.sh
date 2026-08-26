#!/bin/bash

# Activate virtual environment
source birds-env/bin/activate

echo "🔁 Starting FastAPI server..."
uvicorn app.server:app --reload &
SERVER_PID=$!

sleep 2

echo "📸 Starting bird detection inference loop..."
python app/main.py  # or main.py if you haven't renamed it yet

# Wait for user to terminate the process (optional)
wait

# Kill FastAPI server when done
echo "🛑 Stopping FastAPI server..."
kill $SERVER_PID
