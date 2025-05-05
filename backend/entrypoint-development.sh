#!/bin/sh

echo "Starting backend server in development mode..."

uvicorn backend.main:backend --host 0.0.0.0 --port 5001 --reload

echo "Backend server started."