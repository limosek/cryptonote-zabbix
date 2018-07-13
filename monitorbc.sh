#!/bin/sh

[ -z "$ZABBIX_SERVER" ] && ZABBIX_SERVER=localhost
[ -z "$ZABBIX_PORT" ] && ZABBIX_PORT=10051
[ -z "$ZABBIX_SENDER" ] && ZABBIX_SENDER=zabbix_sender
[ -z "$LOCKFILE" ] && LOCKFILE=/tmp/monitorbc.pid

start() {
  if ! [ -f "$LOCKFILE" ]; then
     echo $$ >"$LOCKFILE"
     while [ -f "$LOCKFILE" ]; do
        ./cn2zabbix.py | $ZABBIX_SENDER -T -i - -z "$ZABBIX_SERVER" -p "$ZABBIX_PORT" -r
        sleep 10
     done
  else
    echo "Daemon is already runing? Please cleanup $LOCKFILE and try again"
    exit 2
  fi
}

stop() {
  if [ -f "$LOCKFILE" ]; then
    kill $(cat "$LOCKFILE")
    rm -f "$LOCKFILE"
  else
    echo "No monitorbc runing?" 
    exit 2
  fi
}

if ! $ZABBIX_SENDER -V >/dev/null; then
   echo "Zabbix sender $ZABBIX_SENDER is not installed!"
   exit 3
fi

[ "$1" = "start" ] && { start ; exit; }
[ "$1" = "startbg" ] && { start & exit; }
[ "$1" = "stop" ] && { stop; exit; }
[ "$1" = "restart" ] && { stop; start; exit; }

echo "$0 [start|startbg|stop|restart]"
exit 2

