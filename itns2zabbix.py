#!/usr/bin/python3 -u

import getopt
import json
import sys
import os
from pprint import pprint
import requests
import sys
import time

burl = "http://127.0.0.1:48782/json_rpc"
zserver = "localhost"
zport = 10051
zhost = "itnsd"

def getlastblockheader(burl):
    d = {
        "id": "0",
        "method": "getlastblockheader",
        "jsonrpc": "2.0"
    }
    r = requests.post(burl, data=json.dumps(d), headers={"Content-Type": "application/json"})
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

    response = json.loads(getlastblockheader(burl))
    last_height=0
    while (response):
        if (response['result']['block_header']['height']!=last_height):
            if (time.time()-response['result']['block_header']['timestamp']>3600):
                timestamp=response['result']['block_header']['timestamp']
            else:
                timestamp=time.time()
            zsend('itns.bc_height', response['result']['block_header']['height'], timestamp)
            zsend('itns.bc_difficulty', response['result']['block_header']['difficulty'], timestamp)
            zsend('itns.bc_size', response['result']['block_header']['block_size'], timestamp)
            zsend('itns.bc_timestamp', response['result']['block_header']['timestamp'], timestamp)
        time.sleep(1)
        last_height=response['result']['block_header']['height']
        response = json.loads(getlastblockheader(burl))

if __name__ == "__main__":
    main(sys.argv[1:])
