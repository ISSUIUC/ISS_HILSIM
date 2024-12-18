#!/bin/bash

case "$1" in
start)
./testrack.sh start
;;
stop)
./testrack.sh stop
;;
restart)
./testrack.sh restart
;;
*)
echo "Usage: /etc/init.d/testrack.sh {start|stop|restart}"
exit 1
;;
esac

exit 0