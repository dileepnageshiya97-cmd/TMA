#!/bin/bash

# Background processes
python master_admin_bot.py &
python multi_bot_engine.py &

# Main foreground process (Prevents container exit)
exec gunicorn backend_api:app