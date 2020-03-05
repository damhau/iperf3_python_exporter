#!/bin/python
from flask import Flask, jsonify, request
import iperf3
from concurrent.futures import ThreadPoolExecutor
import random
import argparse

app = Flask(__name__)
executor = ThreadPoolExecutor(64)

parser = argparse.ArgumentParser()
   
parser.add_argument('-s', '--start_port', action='store_true', 
    help="Random iperf3 server range start port")

parser.add_argument('-e', '--end_port', action='store_true', 
    help="Random iperf3 server range end port")

parser.add_argument('-n', '--name', action='store_true', 
    help="Iperf3 server hostname")

args = parser.parse_args()


# vars
iperf3_start_port = args.start_port
iperf3_end_port = args.end_port
iperf3_hostname = args.name
iperf3_port = iperf3_start_port + 1

def start_iperf3_thread(port):
    server = iperf3.Server()
    server.port = port
    server.run()

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
    executor.submit(start_iperf3_thread, iperf3_port)
    return jsonify({'started': True, 'port': iperf3_port, 'hostname': iperf3_hostname })

@app.route('/iperf3_increment')
def route_iperf3_increment():
    if iperf3_port > iperf3_end_port:
        iperf3_port = iperf3_start_port + 1
    else:
        iperf3_port = iperf3_start_port
    iperf3_port = random.randrange(iperf3_start_port, iperf3_end_port)
    executor.submit(start_iperf3_thread, iperf3_port)
    return jsonify({'started': True, 'port': iperf3_port, 'hostname': iperf3_hostname })

if __name__ == '__main__':
    app.run(host='0.0.0.0')