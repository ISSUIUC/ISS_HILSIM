#!/bin/bash

case "$1" in
start)
/opt/testrack.sh start
;;
stop)
/opt/testrack.sh stop
;;
restart)
/opt/testrack.sh restart
;;
*)
echo "Usage: /etc/init.d/testrack.sh {start|stop|restart}"
exit 1
;;
esac

exit 0
