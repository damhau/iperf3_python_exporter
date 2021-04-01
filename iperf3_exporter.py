#!/bin/python
from flask import Flask, send_file, request, Response
from gevent.pywsgi import WSGIServer
from prometheus_client import start_http_server, Counter, generate_latest, Gauge
import logging
import requests
import iperf3
import logging


# Instanciate Flask app
app = Flask(__name__)
app.debug = False

# Instanciate Logger
logging.basicConfig(level=logging.INFO)
logging.info('Starting iperf_server')
 
# Misc vars
CONTENT_TYPE_LATEST = str('text/plain; version=0.0.4; charset=utf-8')
 
# Prometheus metrics definition for TCP
iperf3_tcp_tcp_mss_default = Gauge('iperf3_tcp_tcp_mss_default', 'The default tcp maximum segment size',)
iperf3_tcp_retransmits = Gauge('iperf3_tcp_retransmits', 'The amount of retransmits (Only returned from client)',)
iperf3_tcp_sent_bytes = Gauge('iperf3_tcp_sent_bytes', 'Sent bytes',)
iperf3_tcp_sent_bps = Gauge('iperf3_tcp_sent_bps', 'Sent bits per second',)
iperf3_tcp_received_bytes = Gauge('iperf3_tcp_received_bytes', 'Received bytes',)
iperf3_tcp_received_bps = Gauge('iperf3_tcp_received_bps', 'Received bits per second',)

# Prometheus metrics definition for UDP
iperf3_udp_bytes = Gauge('iperf3_udp_bytes', 'Bytes',)
iperf3_udp_bps = Gauge('iperf3_udp_bps', 'Bits per second',)
iperf3_udp_jitter_ms = Gauge('iperf3_udp_jitter_ms', 'Jitter in millieseconds',)
iperf3_udp_packets = Gauge('iperf3_udp_packets', 'Number of packet',)
iperf3_udp_lost_packets = Gauge('iperf3_udp_lost_packets', 'Number of lost packet',)
iperf3_udp_lost_percent = Gauge('iperf3_udp_lost_percent', 'Percent of lost packet',)
iperf3_udp_seconds = Gauge('iperf3_udp_seconds', 'DUration of test in seconds',)


def start_iperf3_tcp_thread(port, server, duration, omit):
    logging.info('Started iperf thread on port ' + str(port))
    server = iperf3.Server()
    logging.debug('server' + str(server))
    server.port = port
    logging.debug('server.port' + str(server.port))
    server.run()
    logging.debug('server.run' + str(server))
    logging.info('Stopped iperf thread')

def start_iperf3_udp_thread(port):
    logging.info('Started iperf thread on port ' + str(port))
    server = iperf3.Server()
    logging.debug('server' + str(server))
    server.port = port
    logging.debug('server.port' + str(server.port))
    server.run()
    logging.debug('server.run' + str(server))
    logging.info('Stopped iperf thread')

@app.route('/metrics', methods=['GET'])
def get_data():
    iperf3_server = request.args.get('server')
    iperf3_proto = request.args.get('proto')
    iperf3_omit = request.args.get('omit')
    iperf3_duration = request.args.get('duration')
    iperf3_bandwidth = request.args.get('bandwidth')
    iperf3_num_streams = request.args.get('streams')
    iperf3_reverse = request.args.get('reverse')
    iperf3_api_port = request.args.get('apiport')
    logging.info('Received http request to /metric')
    logging.debug('iperf3_server:' + str(iperf3_server))
    logging.debug('iperf3_proto:' + str(iperf3_proto))
    logging.debug('iperf3_omit:' + str(iperf3_omit))
    logging.debug('iperf3_duration:' + str(iperf3_duration))
    logging.debug('iperf3_bandwidth:' + str(iperf3_bandwidth))
    logging.debug('iperf3_num_streams:' + str(iperf3_num_streams))
    logging.debug('iperf3_reverse:' + str(iperf3_reverse))
    logging.debug('iperf3_api_port:' + str(iperf3_api_port))

    logging.debug("http://" + iperf3_server + ":" + iperf3_api_port + "/iperf3_random")
    url = "http://" + iperf3_server + ":" + iperf3_api_port + "/iperf3_random"
    response = requests.get(url)
    json_data = response.json()
    logging.debug("Json data:")
    logging.debug(json_data)
    iperf3_server_port = json_data['port']
    logging.debug("iperf3_server_port:" + str(iperf3_server_port))


    if iperf3_proto == 'tcp':
        client = iperf3.Client()
        if iperf3_duration:
            client.duration = int(iperf3_duration)
        client.protocol = 'tcp'
        if iperf3_omit:
            client.omit = int(iperf3_omit)
        client.server_hostname = iperf3_server
        client.port = iperf3_server_port
        
        logging.info('Started tcp iperf test')
        logging.debug('client:' + str(client))
        logging.debug('client.port:' + str(client.port))
        result = client.run()
        logging.debug('client:' + str(result))
        iperf3_tcp_tcp_mss_default.set(result.tcp_mss_default)
        iperf3_tcp_retransmits.set(result.retransmits)
        iperf3_tcp_sent_bytes.set(result.sent_bytes)
        iperf3_tcp_sent_bps.set(result.sent_bps)
        iperf3_tcp_received_bytes.set(result.received_bytes)
        iperf3_tcp_received_bps.set(result.received_bps)
        del client # This fix a crash happening on Centos 8
        
    elif iperf3_proto == 'udp':
        client = iperf3.Client()
        if iperf3_duration:
            client.duration = int(iperf3_duration)
        client.protocol = 'udp'
        if iperf3_omit:
            client.omit = int(iperf3_omit)
        if iperf3_bandwidth:
            client.bandwidth = int(iperf3_bandwidth)
        client.server_hostname = iperf3_server
        client.port = iperf3_server_port
        logging.info('Started udp iperf test')
        result = client.run()
        iperf3_udp_bytes.set(result.bytes)
        iperf3_udp_bps.set(result.bps)
        iperf3_udp_jitter_ms.set(result.jitter_ms)
        iperf3_udp_packets.set(result.packets)
        iperf3_udp_lost_packets.set(result.lost_packets)
        iperf3_udp_lost_percent.set(result.lost_percent)
        iperf3_udp_seconds.set(result.seconds)
        del client # This fix a crash happening on Centos 8
        
    return Response(generate_latest(), mimetype=CONTENT_TYPE_LATEST)
 

if __name__ == '__main__':
    app.run(host='0.0.0.0', port='9100', threaded=True)
    #http_server = WSGIServer(('', 9100), app)
    #http_server.serve_forever()
