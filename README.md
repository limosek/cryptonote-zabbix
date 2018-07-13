# blockchain-zabbix
Zabbix scripts and templates used for blockchain monitoring.


## cn2zabbix.py
This is main script which needs to be run. It constantly monitors blockchain daemon and returns output suitable for zabbix_sender.
```
./cn2zabbix.py -h
usage: cn2zabbix.py [-f CONFIGFILE] [-h] [-d LEVEL] [-c CURRENCY] [-D URL]
                    [-H HOSTNAME] [-W S]

Args that start with '--' (eg. -h) can also be set in a config file (specified
via -f). Config file syntax allows: key=value, flag=true, stuff=[a,b,c] (for
details, see syntax at https://goo.gl/R74nmi). If an arg is specified in more
than one place, then commandline values override config file values which
override defaults.

optional arguments:
  -f CONFIGFILE, --config CONFIGFILE
                        Config file (default: /home/lm/cryptonote-
                        zabbix/cn2zabbix.ini)
  -h, --help            Help (default: None)
  -d LEVEL, --debug LEVEL
                        Debug level (default: WARNING)
  -c CURRENCY, --currency CURRENCY
                        Currency prefix (default: itns)
  -D URL, --daemon-url URL
                        Daemon url (default: http://127.0.0.1:48782)
  -H HOSTNAME, --zabbix-host HOSTNAME
                        Zabbix hostname for this daemon (default: lindev-jso-
                        cz)
  -W S, --wait-time S   Wait seconds between queries (default: 3)

Command Line Args:   -h
Config File (/home/lm/cryptonote-zabbix/cn2zabbix.ini):
  daemon-url:        http://monitor.intensecoin.com:48782
  zabbix-host:       bcdaemon
Defaults:
  --config:          /home/lm/cryptonote-zabbix/cn2zabbix.ini
  --debug:           WARNING
  --currency:        itns
  --wait-time:       3
```