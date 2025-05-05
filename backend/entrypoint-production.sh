#!/bin/sh

echo "Starting backend server in production mode..."

uvicorn backend.main:backend --host 0.0.0.0 --port 5001 --workers 4 

echo "Backend server started."