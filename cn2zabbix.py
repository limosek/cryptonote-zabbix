#!/usr/bin/python3 -u

import configargparse
import getopt
import json
import logging
import os
from pprint import pprint
import requests
import socket
import sys
import time

cfg = {}

def json_daemon_call(burl, method, params):
    if (method != ""):
        d = {
            "id": "0",
            "method": method,
            "jsonrpc": "2.0",
            "params": params
        }
        url = burl + "/json_rpc"
        logging.warning("Calling RPC " + url)
        r = requests.post(url, data=json.dumps(d), headers={"Content-Type": "application/json"})
    else:
        logging.warning("Calling RPC " + burl)
        r = requests.post(burl, data="", headers={"Content-Type": "application/json"})
    if (r.status_code == 200):
        return(r.text)
    else:
        logging.error("RPC error %s!" % (r.status_code))
        return(None)

def zsend(key, value, timestamp):
    global cfg
    line = '"%s" "%s" "%s" "%s"' % (cfg.zhost, key, round(timestamp), value)
    logging.debug("Sending data to zabbix: " + line)
    print(line)
    sys.stdout.flush()

def main(argv):
    global cfg

    p = configargparse.getArgumentParser()
    p.add('-f', '--config', metavar='CONFIGFILE', required=None, is_config_file=True, help='Config file')
    p.add('-h', '--help', metavar='HELP', required=None, action='store_const', dest='h', const='h', help='Help')
    p.add('-d', '--debug', dest='d', metavar='LEVEL', help='Debug level', default='ERROR')
    p.add('-c', '--currency', dest='currency', metavar='CURRENCY', required=None, help='Currency prefix', default='itns')
    p.add('-D', '--daemon-url', dest='burl', metavar='URL', required=None, help='Daemon url', default='http://127.0.0.1:48782')
    p.add('-H', '--zabbix-host', dest='zhost', metavar='HOSTNAME', required=None, help='Zabbix hostname for this daemon', default=socket.gethostname())
    p.add('-W', '--wait-time', dest='wait', metavar='S', required=None, help='Wait seconds between queries', default=3)

    Log = logging.getLogger()
    cfg = p.parse_args()
    Log.setLevel(cfg.d)

    if (cfg.h):
        print(p.format_help())
        print(p.format_values())
        sys.exit()

    getlastblockheader = json.loads(json_daemon_call(cfg.burl, "getlastblockheader", {}))
    get_transaction_pool_stats_tmp = json_daemon_call(cfg.burl + "/get_transaction_pool_stats", "", {})

    last_height = 0
    last_tp_size = -1
    last_time = 0

    while (getlastblockheader):
        cur_time = time.time()
        cur_height = getlastblockheader['result']['block_header']['height']
        height_changed = (cur_height != last_height)

        if (height_changed or cur_time > last_time + 60*5):
            last_time = cur_time
            getblockheadersrange = {}

            if (height_changed):
                if (last_height > 0 and cur_height - last_height > 1):
                  getblockheadersrange = json.loads(json_daemon_call(cfg.burl, "getblockheadersrange", { "start_height": last_height + 1, "end_height": cur_height - 1 }))
                logging.warning("Change in height (%s => %s)" % (last_height, cur_height))
            else:
                logging.warning("Same height %s" % (last_height))

            blocks = []
            if ("result" in getblockheadersrange):
              blocks.extend(getblockheadersrange['result']['headers'])
            blocks.append(getlastblockheader['result']['block_header'])

            for block in blocks:
              if (cur_time - block['timestamp'] > 3600):
                  timestamp = block['timestamp']
              else:
                  timestamp = cur_time
              zsend(cfg.currency + '.bc_height', block["height"], timestamp)
              zsend(cfg.currency + '.bc_difficulty', block['difficulty'], timestamp)
              zsend(cfg.currency + '.bc_size', block['block_size'], timestamp)
              zsend(cfg.currency + '.bc_timestamp', block['timestamp'], timestamp)

        i1 = get_transaction_pool_stats_tmp.find('"histo"')
        if (i1 != -1):
            i2 = get_transaction_pool_stats_tmp.find("histo_98pc", i1) - 1
            get_transaction_pool_stats_tmp = get_transaction_pool_stats_tmp[0:i1] + get_transaction_pool_stats_tmp[i2:len(get_transaction_pool_stats_tmp)]
        get_transaction_pool_stats = json.loads(get_transaction_pool_stats_tmp)
        if (get_transaction_pool_stats['pool_stats']['bytes_total'] != last_tp_size):
            logging.warning("Change in tp_size (%s => %s)" % (last_tp_size, get_transaction_pool_stats['pool_stats']['bytes_total']))
            zsend(cfg.currency + '.tp_total', get_transaction_pool_stats['pool_stats']['bytes_total'], cur_time)
            zsend(cfg.currency + '.tp_num', get_transaction_pool_stats['pool_stats']['txs_total'], cur_time)
        else:
            logging.warning("Same tp_size %s" % (last_tp_size))

        time.sleep(cfg.wait)
        last_height = cur_height
        last_tp_size = get_transaction_pool_stats['pool_stats']['bytes_total']
        getlastblockheader = json.loads(json_daemon_call(cfg.burl, "getlastblockheader", {}))
        get_transaction_pool_stats_tmp = json_daemon_call(cfg.burl + "/get_transaction_pool_stats", "", {})

if __name__ == "__main__":
    main(sys.argv[1:])
