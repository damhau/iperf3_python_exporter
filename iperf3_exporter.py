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
logging.basicConfig(filename='/var/log/iperf_exporter.log',level=logging.DEBUG)
logging.debug('Starting iperf_exporter')
 
# Misc vars
CONTENT_TYPE_LATEST = str('text/plain; version=0.0.4; charset=utf-8')
 
# Prometheus metrics definition for TCP
iperf3_tcp_tcp_mss_default = Gauge('iperf3_tcp_tcp_mss_default', 'The default tcp maximum segment size', ['server', 'protocol'],)
iperf3_tcp_retransmits = Gauge('iperf3_tcp_retransmits', 'The amount of retransmits (Only returned from client)', ['server', 'protocol'],)
iperf3_tcp_sent_bytes = Gauge('iperf3_tcp_sent_bytes', 'Sent bytes', ['server', 'protocol'],)
iperf3_tcp_sent_bps = Gauge('iperf3_tcp_sent_bps', 'Sent bits per second', ['server', 'protocol'],)
iperf3_tcp_received_bytes = Gauge('iperf3_tcp_received_bytes', 'Received bytes', ['server', 'protocol'],)
iperf3_tcp_received_bps = Gauge('iperf3_tcp_received_bps', 'Received bits per second', ['server', 'protocol'],)

# Prometheus metrics definition for UDP
iperf3_udp_bytes = Gauge('iperf3_udp_bytes', 'Bytes', ['server', 'protocol'],)
iperf3_udp_bps = Gauge('iperf3_udp_bps', 'Bits per second', ['server', 'protocol'],)
iperf3_udp_jitter_ms = Gauge('iperf3_udp_jitter_ms', 'Jitter in millieseconds', ['server', 'protocol'],)
iperf3_udp_packets = Gauge('iperf3_udp_packets', 'Number of packet', ['server', 'protocol'],)
iperf3_udp_lost_packets = Gauge('iperf3_udp_lost_packets', 'Number of lost packet', ['server', 'protocol'],)
iperf3_udp_lost_percent = Gauge('iperf3_udp_lost_percent', 'Percent of lost packet', ['server', 'protocol'],)
iperf3_udp_seconds = Gauge('iperf3_udp_seconds', 'DUration of test in seconds', ['server', 'protocol'],)


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
    logging.debug('Received http request to /metric')
    logging.debug('iperf3_server:' + str(iperf3_server))
    logging.debug('iperf3_proto:' + str(iperf3_proto))
    logging.debug('iperf3_omit:' + str(iperf3_omit))
    logging.debug('iperf3_duration:' + str(iperf3_duration))
    logging.debug('iperf3_bandwidth:' + str(iperf3_bandwidth))
    logging.debug('iperf3_num_streams:' + str(iperf3_num_streams))
    logging.debug('iperf3_reverse:' + str(iperf3_reverse))
    logging.debug('iperf3_api_port:' + str(iperf3_api_port))

    logging.debug("http://" + iperf3_server + ":" + iperf3_api_port + "/iperf3_increment")
    url = "http://" + iperf3_server + ":" + iperf3_api_port + "/iperf3_increment"
    response = requests.get(url)
    json_data = response.json()
    logging.debug("Json data:")
    logging.debug(json_data)
    iperf3_server_port = json_data['port']

    if iperf3_proto == 'tcp':
        client = iperf3.Client()
        if iperf3_duration:
            client.duration = int(iperf3_duration)
        client.protocol = 'tcp'
        if iperf3_omit:
            client.omit = int(iperf3_omit)
        client.server_hostname = iperf3_server
        client.port = iperf3_server_port
        result = client.run()
        iperf3_tcp_tcp_mss_default.labels(server=iperf3_server, protocol=iperf3_proto).set(result.tcp_mss_default)
        iperf3_tcp_retransmits.labels(server=iperf3_server, protocol=iperf3_proto).set(result.retransmits)
        iperf3_tcp_sent_bytes.labels(server=iperf3_server, protocol=iperf3_proto).set(result.sent_bytes)
        iperf3_tcp_sent_bps.labels(server=iperf3_server, protocol=iperf3_proto).set(result.sent_bps)
        iperf3_tcp_received_bytes.labels(server=iperf3_server, protocol=iperf3_proto).set(result.received_bytes)
        iperf3_tcp_received_bps.labels(server=iperf3_server, protocol=iperf3_proto).set(result.received_bps)
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
        result = client.run()
        iperf3_udp_bytes.labels(server=iperf3_server, protocol=iperf3_proto).set(result.bytes)
        iperf3_udp_bps.labels(server=iperf3_server, protocol=iperf3_proto).set(result.bps)
        iperf3_udp_jitter_ms.labels(server=iperf3_server, protocol=iperf3_proto).set(result.jitter_ms)
        iperf3_udp_packets.labels(server=iperf3_server, protocol=iperf3_proto).set(result.packets)
        iperf3_udp_lost_packets.labels(server=iperf3_server, protocol=iperf3_proto).set(result.lost_packets)
        iperf3_udp_lost_percent.labels(server=iperf3_server, protocol=iperf3_proto).set(result.lost_percent)
        iperf3_udp_seconds.labels(server=iperf3_server, protocol=iperf3_proto).set(result.seconds)

    return Response(generate_latest(), mimetype=CONTENT_TYPE_LATEST)
 

if __name__ == '__main__':
    # app.run(host='0.0.0.0', port='9100')
    http_server = WSGIServer(('', 9100), app)
    http_server.serve_forever()