#!/bin/bash
daemon() {
    while true; do
    python server.py
    sleep 1
    done
}

start() {
    daemon &
    PID=$!
    echo $PID > /var/run/testrack.pid
}

stop() {
    kill
}
