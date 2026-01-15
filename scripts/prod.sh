#!/bin/bash
# Production runner script

set -e

echo "Starting Wisp Framework in production mode..."

# Load environment variables
if [ -f .env.prod ]; then
    export $(cat .env.prod | grep -v '^#' | xargs)
fi

# Set environment
export ENV=prod

# Run the bot
wisp-framework-runner
