#!/bin/bash

PATH="/app/.venv/bin:$PATH"

source /app/.venv/bin/activate

cd /app

if [ "$ENV" = "production" ]; then
    echo "Starting backend server in production mode..."

    uvicorn backend.main:backend --host 0.0.0.0 --port 5001 --workers 4 

    echo "Backend server started."
else
    
    echo "Starting backend server in development mode..."

    uvicorn backend.main:backend --host 0.0.0.0 --port 5001 --reload 

    echo "Backend server started."
fi




