#!/bin/python
from flask import Flask, jsonify, request
from gevent.pywsgi import WSGIServer
import iperf3
from concurrent.futures import ThreadPoolExecutor
import random
import argparse
import logging

app = Flask(__name__)
app.debug = False
executor = ThreadPoolExecutor(256)

# Parse args
parser = argparse.ArgumentParser()  
parser.add_argument('-s', '--start_port', action='store', dest='start_port', type=int, help="Random iperf3 server range start port")
parser.add_argument('-e', '--end_port', action='store', dest='end_port', type=int, help="Random iperf3 server range end port")
parser.add_argument('-p', '--port', action='store', dest='port', type=int, help="Random iperf3 server api port")
parser.add_argument('-n', '--name', action='store', dest='name', help="Iperf3 server hostname")
parser.add_argument('-v', '--verbose', action = 'count', default = 2, help = 'Increase verbosity')
args = parser.parse_args()

# Instanciate Logger
try:
    loglevel = {
        0: logging.ERROR,
        1: logging.WARN,
        2: logging.INFO,
        3: logging.DEBUG
    }[args.verbose]
except KeyError:
    loglevel = logging.INFO
logging.basicConfig(level=loglevel)
logging.info('Starting iperf_server')




# vars
iperf3_server_port = args.port
iperf3_start_port = args.start_port
iperf3_end_port = args.end_port
iperf3_hostname = args.name
iperf3_port = iperf3_start_port + 1

logging.debug('iperf3_server_port: ' + str(iperf3_server_port))

def start_iperf3_thread(port):
    logging.info('Started iperf thread on port ' + str(port))
    server = iperf3.Server()
    logging.debug('server' + str(server))
    server.port = port
    logging.debug('server.port' + str(server.port))
    server.run()
    logging.debug('server.run' + str(server))
    logging.info('Stopped iperf thread')

@app.route('/iperf3')
def route_iperf3():
    iperf3_port = request.args.get('port')
    if iperf3_port:
        executor.submit(start_iperf3_thread, iperf3_port)
        return jsonify({'started': True, 'port': iperf3_port })
    else:
        return jsonify({'started': False, 'Error': 'Missing port parameter' })

@app.route('/iperf3_random')
def route_iperf3_random():
    iperf3_port = random.randrange(iperf3_start_port, iperf3_end_port)
    future = executor.submit(start_iperf3_thread, iperf3_port)
    return jsonify({'started': True, 'port': iperf3_port, 'hostname': iperf3_hostname })

@app.route('/iperf3_increment')
def route_iperf3_increment():
    global iperf3_port
    if iperf3_port == iperf3_end_port:
        iperf3_port = iperf3_start_port
    else:
        iperf3_port = iperf3_port + 1
    
    # executor.submit(start_iperf3_thread, iperf3_port)
    logging.info('Started iperf thread on port ' + str(iperf3_port))
    server = iperf3.Server()
    logging.debug('server' + str(server))
    server.port = iperf3_port
    logging.debug('server.port' + str(server.port))
    server.run()
    logging.debug('server.run' + str(server))
    logging.info('Stopped iperf thread')
    return jsonify({'started': True, 'port': iperf3_port, 'hostname': iperf3_hostname })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=iperf3_server_port, threaded=True)
    #http_server = WSGIServer(('', iperf3_server_port), app)
    #http_server.serve_forever()