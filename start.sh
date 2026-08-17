#!/bin/bash

# Master Admin Bot ko background me run karein
python master_admin_bot.py &

# Multi-Bot Engine ko background me run karein
python multi_bot_engine.py &

# Web API ko foreground me run karein (main process)
exec gunicorn backend_api:app