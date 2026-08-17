#!/bin/bash

# 1. Pehle Flask API ko background me run karke DB initialize hone dein
gunicorn backend_api:app &

# DB setup ke liye 3 sec ka pause
sleep 3

# 2. Master Admin Bot ko background me run karein
python master_admin_bot.py &

# 3. Multi-Bot Engine ko main process banayein
exec python multi_bot_engine.py