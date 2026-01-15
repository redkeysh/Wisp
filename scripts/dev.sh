#!/bin/bash
# Development runner script

set -e

echo "Starting Wisp Framework in development mode..."

# Load environment variables
if [ -f .env.local ]; then
    export $(cat .env.local | grep -v '^#' | xargs)
fi

# Set environment
export ENV=local

# Run the bot
python -m runner_bot.main
