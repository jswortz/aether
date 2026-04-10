#!/bin/bash

# schedule_dream_mode.sh
# Sets up a local cron job to run Aether Dream Mode background reflections.

PROJECT_ROOT="/usr/local/google/home/jwortz/aether"
DREAM_MODE_SCRIPT="$PROJECT_ROOT/core/dream_mode.py"
PYTHON_EXEC=$(which python3)

# Check if script exists
if [ ! -f "$DREAM_MODE_SCRIPT" ]; then
    echo "Error: Dream Mode script not found at $DREAM_MODE_SCRIPT"
    exit 1
fi

# Create a temporary crontab file
crontab -l > mycron 2>/dev/null

# Add Dream Mode entry: Run every day at 2 AM (idle time)
# 0 2 * * * cd $PROJECT_ROOT && $PYTHON_EXEC $DREAM_MODE_SCRIPT >> $PROJECT_ROOT/logs/dream_mode.log 2>&1
CRON_ENTRY="0 2 * * * cd $PROJECT_ROOT && export PYTHONPATH=\$PYTHONPATH:$PROJECT_ROOT && $PYTHON_EXEC $DREAM_MODE_SCRIPT >> $PROJECT_ROOT/logs/dream_mode.log 2>&1"

# Check if entry already exists
if grep -q "dream_mode.py" mycron; then
    echo "Dream Mode already scheduled."
else
    echo "$CRON_ENTRY" >> mycron
    crontab mycron
    echo "Successfully scheduled Aether Dream Mode (Daily at 2 AM)."
fi

rm mycron

# Create logs directory if it doesn't exist
mkdir -p "$PROJECT_ROOT/logs"

echo "Aether Dream Mode Setup Complete."
