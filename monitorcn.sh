#!/bin/sh
export PATH=$PATH:/usr/local/bin

if [ -z "$CNONE" ] && [ -d /etc/cn2zabbix ] && [ -n "/etc/cn2zabbix/*conf" ];  then
  CONFIGS=/etc/cn2zabbix/*conf
  for conf in $CONFIGS; do
    (
      export CNONE=1
      LOCKFILE=/tmp/monitorcn_$(basename $conf .conf).pid
      . $conf
      export ZABBIX_SERVER ZABBIX_PORT ZABBIX_SENDER LOCKFILE CN2ZOPTS DAEMON_RPC ZABBIX_HOST
      $0 $@
    )
  done
  exit
fi

[ -z "$ZABBIX_SERVER" ] && ZABBIX_SERVER=localhost
[ -z "$ZABBIX_PORT" ] && ZABBIX_PORT=10051
[ -z "$ZABBIX_SENDER" ] && ZABBIX_SENDER=zabbix_sender
[ -z "$LOCKFILE" ] && LOCKFILE=/tmp/monitorbc.pid
[ -n "$ZABBIX_HOST" ] && ZABBIX_HOST="-H $ZABBIX_HOST"
[ -n "$DAEMON_RPC" ] && DAEMON_RPC="-D $DAEMON_RPC"
[ -z "$LOCKFILE" ] && LOCKFILE=/tmp/monitorbc.pid
[ -z "$CN2ZOPTS" ] && CN2ZOPTS="$DAEMON_RPC $ZABBIX_HOST"

start() {
  if ! [ -f "$LOCKFILE" ]; then
     echo $$ >"$LOCKFILE"
     while [ -f "$LOCKFILE" ]; do
        ./cn2zabbix.py $CN2ZOPTS | $ZABBIX_SENDER -T -i - -z "$ZABBIX_SERVER" -p "$ZABBIX_PORT" -r
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
[ "$1" = "stop" ] && { stop; exit; }
[ "$1" = "restart" ] && { stop; start; exit; }
[ "$1" = "show" ] && {
  echo ZABBIX_SERVER=$ZABBIX_SERVER;
  echo ZABBIX_PORT=$ZABBIX_PORT;
  echo ZABBIX_SENDER=$ZABBIX_SENDER;
  echo LOCKFILE=$LOCKFILE;
  echo CN2ZOPTS=\"$CN2ZOPTS\"
  echo cn2zabbix.py $CN2ZOPTS \| $ZABBIX_SENDER -T -i - -z "$ZABBIX_SERVER" -p "$ZABBIX_PORT" -r
  echo
  exit;
}

echo "$0 [start|stop|restart|show]"
exit 2
