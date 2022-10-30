#!/bin/sh

exec gunicorn --workers=5 --threads=2 --bind 0.0.0.0:5000 manage:app &
exec python docker-monitor/monitor.py &
#exec python converter-async/app.py &
