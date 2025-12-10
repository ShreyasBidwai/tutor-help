#!/bin/bash

# Tutor Help - Production Startup Script

# Load environment variables
if [ -f .env ]; then
    export $(cat .env | grep -v '^#' | xargs)
fi

# Create necessary directories
mkdir -p uploads/homework
mkdir -p logs

# Run database migrations and add indexes
echo "Initializing database and indexes..."
python3 -c "from database import migrate_db, add_indexes; migrate_db(); add_indexes()"

# Start Gunicorn
echo "Starting Tutor Help application..."
gunicorn -c gunicorn_config.py app:app

