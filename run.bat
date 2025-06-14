@echo off
title Task Queue System
start cmd /k "redis-server redis.windows.conf"
timeout /t 3
start cmd /k "python backend\app.py"
timeout /t 2
start cmd /k "python backend\worker.py"
start http://localhost:5000