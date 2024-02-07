#!/bin/sh
service postgresql start
service redis-server start
cd /hide && uvicorn app.app:app --host 0.0.0.0 --port 80 --workers 4
# tail -f /dev/null
