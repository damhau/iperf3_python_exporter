# Iperf3 Server and Prometheus exporter

Iperf server for mutli user in pyhton.

Iperf 3 was not built to allow conccurent test, there is a PR https://github.com/esnet/iperf/pull/1074 but this script was built before.

The server part will provide an api to request a iperf3 instance on a random or specific port and the client (a prometheus exporter) will use the instance port recieved from the api and start an iperf3 test.

## Installation

### Centos/Rhel

pip3 install -r requierments.txt

yum install iperf3

### Debian/Ubuntu

pip3 install -r requierments.txt

apt install iperf3

## Getting Started

To test the server you can, start the server and call the rest endpoind /start_iperf_server?port=4000
Run an iperf client to this port.

## Promethus configuration

RUn the server, this exemple will pick the port for the iperf instance from 50100 to 50199. Replace $iperf_server with the hostname if the server.

```
/usr/bin/python3 /opt/iperf3_python_exporter/iperf3_server.py --start_port=50100 --end_port=50199 -p 50001 -n $iperf_server
```

Use the following prometheus config. Replace $iperf_server with the hostname if the server.

```
global:
  scrape_interval: 300s

rule_files:
  - 'alert.rules'

alerting:
  alertmanagers:
  - scheme: http
    static_configs:
    - targets:
      - "alertmanager:9093"

scrape_configs:
  # Prometheus self monitoring
  - job_name: 'prometheus'
    scrape_interval: 300s
    static_configs:
      - targets: ['localhost:9090']

  # IPERF
  - job_name: 'iperf-job1'
    scrape_interval: 600s
    scrape_timeout: 30s
    params:
      server: ['$iperf_server']
      proto: ['tcp']
      apiport: ['50001']
      omit: ['2']
```

### Prerequisites

```
pip install --requirement requirements.txt
```
