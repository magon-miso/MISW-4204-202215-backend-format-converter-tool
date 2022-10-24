#!/bin/sh

# Start the first process
# ./my_first_process &
exec gunicorn --workers=5 --threads=2 --bind 0.0.0.0:5000 manage:app &
#

# Start the second process
# ./my_second_process &
exec python converter-async/app.py &

exec python docker-monitor/monitor.py &

# Wait for any process to exit
wait -n
  
# Exit with status of process that exited first
exit $?



# if [ "$DATABASE" = "postgres" ]
# then
#     echo "Waiting for postgres..."

#     while ! nc -z $SQL_HOST $SQL_PORT; do
#       sleep 0.1
#     done

#     echo "PostgreSQL started"
# fi

# exec "$@"
