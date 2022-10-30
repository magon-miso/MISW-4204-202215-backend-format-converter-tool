#!/bin/sh

exec python app.py &
exec python monitor.py &
#exec python converter-async/app.py &
#exec python docker-monitor/monitor.py &
