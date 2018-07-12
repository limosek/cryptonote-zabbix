#!/usr/bin/python3 -u

import getopt
import json
import sys
import os
from pprint import pprint
import requests
import sys
import time

burl = "http://127.0.0.1:48782"
zserver = "localhost"
zport = 10051
zhost = "itnsd"

def json_daemon_call(burl, method):
    if (method != ""):
			d = {
					"id": "0",
					"method": method,
					"jsonrpc": "2.0"
			}
			r = requests.post(burl + "/json_rpc", data=json.dumps(d), headers={"Content-Type": "application/json"})
		else:
			r = requests.post(burl, data="", headers={"Content-Type": "application/json"})
    if (r.status_code==200):
        return(r.text)
    else:
        return(None)

def zsend(key, value, timestamp):
    print('"%s" "%s" "%s" "%s"' % (zhost, key, round(timestamp), value))

def main(argv):
    global zserver,burl,zhost,zport
    try:
        opts, args = getopt.getopt(argv, "h", ["help", "burl=", "zserver=", "zhost=", "zport="])
    except getopt.GetoptError:
        print('itnsd2zabbix.py --burl url ..')
        sys.exit(2)
    for opt, arg in opts:
        if opt in ("-h", "--help"):
            print('itnsd2zabbix.py blockchain_url zabbix_url')
            sys.exit()
        elif opt in ("--burl"):
            burl = arg
        elif opt in ("--zserver"):
            zserver = arg
        elif opt in ("--zport"):
            zport = arg
        elif opt in ("--zhost"):
            zhost = arg

    getlastblockheader = json.loads(json_daemon_call(burl, "getlastblockheader"))
    get_transaction_pool_stats = json.loads(json_daemon_call(burl + "/get_transaction_pool_stats", ""))
    last_height=0
    while (getlastblockheader):
        if (getlastblockheader['result']['block_header']['height']!=last_height):
            if (time.time()-getlastblockheader['result']['block_header']['timestamp']>3600):
                timestamp=getlastblockheader['result']['block_header']['timestamp']
            else:
                timestamp=time.time()
            zsend('itns.bc_height', getlastblockheader['result']['block_header']['height'], timestamp)
            zsend('itns.bc_difficulty', getlastblockheader['result']['block_header']['difficulty'], timestamp)
            zsend('itns.bc_size', getlastblockheader['result']['block_header']['block_size'], timestamp)
            zsend('itns.bc_timestamp', getlastblockheader['result']['block_header']['timestamp'], timestamp)
            zsend('itns.tp_total', get_transaction_pool_stats['result']['pool_stats']['bytes_total'], timestamp)
        time.sleep(1)
        last_height=getlastblockheader['result']['block_header']['height']
        getlastblockheader = json.loads(json_daemon_call(burl, "getlastblockheader"))
        get_transaction_pool_stats = json.loads(json_daemon_call(burl + "/get_transaction_pool_stats", ""))

if __name__ == "__main__":
    main(sys.argv[1:])
