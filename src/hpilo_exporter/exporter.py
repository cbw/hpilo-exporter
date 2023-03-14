"""
Pulls data from specified iLO and presents as Prometheus metrics
"""
from __future__ import print_function
from _socket import gaierror
import os
import sys
import hpilo

import time
from . import prometheus_metrics
from http.server import BaseHTTPRequestHandler
from http.server import HTTPServer
from socketserver import ForkingMixIn
from prometheus_client import generate_latest, Summary
from urllib.parse import parse_qs
from urllib.parse import urlparse


def print_err(*args, **kwargs):
    print(*args, file=sys.stderr, **kwargs)


# Create a metric to track time spent and requests made.
REQUEST_TIME = Summary(
    'request_processing_seconds', 'Time spent processing request')


class ForkingHTTPServer(ForkingMixIn, HTTPServer):
    max_children = 30
    timeout = 30


class RequestHandler(BaseHTTPRequestHandler):
    """
    Endpoint handler
    """
    def return_error(self):
        self.send_response(500)
        self.end_headers()

    def do_GET(self):
        """
        Process GET request

        :return: Response with Prometheus metrics
        """
        # this will be used to return the total amount of time the request took
        start_time = time.time()
        # get parameters from the URL
        url = urlparse(self.path)
        # following boolean will be passed to True if an error is detected during the argument parsing
        error_detected = False
        query_components = parse_qs(urlparse(self.path).query)

        ilo_host = None
        ilo_port = None
        ilo_user = os.getenv('ILO_USERNAME')
        ilo_password = os.getenv('ILO_PASSWORD')
        try:
            ilo_host = query_components['ilo_host'][0]
            ilo_port = int(query_components['ilo_port'][0])
        except KeyError as e:
            print_err("missing parameter %s" % e)
            self.return_error()
            error_detected = True

        if ilo_user is None:
            try:
                ilo_user = query_components['ilo_user'][0]
            except KeyError as e:
                print_err("missing parameter %s" % e)
                self.return_error()
                error_detected = True

        if ilo_password is None:
            try:
                ilo_password = query_components['ilo_password'][0]
            except KeyError as e:
                print_err("missing parameter %s" % e)
                self.return_error()
                error_detected = True

        if url.path == self.server.endpoint and ilo_host and ilo_user and ilo_password and ilo_port:

            ilo = None
            try:
                ilo = hpilo.Ilo(hostname=ilo_host,
                                login=ilo_user,
                                password=ilo_password,
                                port=ilo_port, timeout=10)
            except hpilo.IloLoginFailed:
                print("ILO login failed")
                self.return_error()
            except gaierror:
                print("ILO invalid address or port")
                self.return_error()
            except hpilo.IloCommunicationError as e:
                print(e)

            # get product and server name
            try:
                product_name = ilo.get_product_name()
            except:
                product_name = "Unknown HP Server"

            try:
                server_name = ilo.get_server_name()
                if server_name == "":
                    server_name = ilo_host
            except:
                server_name = ilo_host

            # get health
            embedded_health = ilo.get_embedded_health()
            health_at_glance = embedded_health['health_at_a_glance']
            
            if health_at_glance is not None:
                for key, value in health_at_glance.items():
                    for status in value.items():
                        if status[0] == 'status':
                            gauge = 'hpilo_{}_gauge'.format(key)
                            if status[1].upper() == 'OK':
                                prometheus_metrics.gauges[gauge].labels(product_name=product_name,
                                                                        server_name=server_name).set(0)
                            elif status[1].upper() == 'DEGRADED':
                                prometheus_metrics.gauges[gauge].labels(product_name=product_name,
                                                                        server_name=server_name).set(1)
                            else:
                                prometheus_metrics.gauges[gauge].labels(product_name=product_name,
                                                                        server_name=server_name).set(2)
            #for iLO3 patch network
            if ilo.get_fw_version()["management_processor"] == 'iLO3':
                print_err('Unknown iLO nic status')
            else:
                # get nic information
                for nic_name,nic in embedded_health['nic_information'].items():
                   try:
                       value = ['OK','Disabled','Unknown','Link Down'].index(nic['status'])
                   except ValueError:
                       value = 4
                       print_err('unrecognised nic status: {}'.format(nic['status']))

                   prometheus_metrics.hpilo_nic_status_gauge.labels(product_name=product_name,
                                                                    server_name=server_name,
                                                                    nic_name=nic_name,
                                                                    ip_address=nic['ip_address']).set(value)

            # Fan speeds
            for _,fan in embedded_health['fans'].items():
                fan_name = fan['label']
                try:
                    fan_status = ['OK','Disabled','Not Installed','Failed'].index(fan['status'])
                except ValueError:
                    fan_status = 4
                    print_err('unrecognised fan status: {}'.format(fan['status']))

                prometheus_metrics.hpilo_fan_status_gauge.labels(product_name=product_name,
                                                                    server_name=server_name,
                                                                    fan_name=fan_name).set(fan_status)
                
                if fan['speed'] is not None:
                    (fan_speed, _) = fan['speed']
                    prometheus_metrics.hpilo_fan_speed_gauge.labels(product_name=product_name,
                                                                    server_name=server_name,
                                                                    fan_name=fan_name).set(fan_speed)
                    
            # Temperatures
            for _,temperature in embedded_health['temperature'].items():
                thermometer_name = temperature['label']
                try:
                    temp_status = ['OK','Disabled','Not Installed','Failed'].index(temperature['status'])
                except ValueError:
                    temp_status = 4
                    print_err('unrecognised temperature status: {}'.format(temperature['status']))

                prometheus_metrics.hpilo_temp_status_gauge.labels(product_name=product_name,
                                                                    server_name=server_name,
                                                                    thermometer_name=thermometer_name).set(temp_status)
                                    
                if type(temperature['currentreading']) is tuple:
                    (cur_temp, _) = temperature['currentreading']
                    prometheus_metrics.hpilo_temp_gauge.labels(product_name=product_name,
                                                               server_name=server_name,
                                                               thermometer_name=thermometer_name).set(cur_temp)

                if type(temperature['caution']) is tuple:
                    (caution_temp, _) = temperature['caution']
                    prometheus_metrics.hpilo_temp_caution_gauge.labels(product_name=product_name,
                                                                       server_name=server_name,
                                                                       thermometer_name=thermometer_name).set(caution_temp)

                if type(temperature['critical']) is tuple:
                    (critical_temp, _) = temperature['critical']
                    prometheus_metrics.hpilo_temp_critical_gauge.labels(product_name=product_name,
                                                                        server_name=server_name,
                                                                        thermometer_name=thermometer_name).set(critical_temp)

            # get firmware version
            fw_version = ilo.get_fw_version()["firmware_version"]
            # prometheus_metrics.hpilo_firmware_version.set(fw_version)
            prometheus_metrics.hpilo_firmware_version.labels(product_name=product_name,
                                                             server_name=server_name).info({'firmware_version': fw_version})

            # Temperatures
            host_power_state = ilo.get_host_power_status()
            try:
                power_status = ['OFF','ON'].index(host_power_state)
            except ValueError:
                power_status = 2
                print_err('unrecognised power state: {}'.format(host_power_state))

                prometheus_metrics.hpilo_host_power_gauge.labels(product_name=product_name,
                                                                 server_name=server_name).set(power_status)
                
            # Server uptime
            try:
                uptime = ilo.get_server_power_on_time()
                prometheus_metrics.hpilo_host_uptime_gauge.labels(product_name=product_name,
                                                                  server_name=server_name).set(uptime)
            except Exception as e:
                print_err('exception when calling get_server_power_on_time(): {}'.format(e))


            # Network info
            network = ilo.get_network_settings()
            prometheus_metrics.hpilo_ip_address.labels(product_name=product_name,
                                                       server_name=server_name).info({'ip_address': network['ip_address']})
            
            # get the amount of time the request took
            REQUEST_TIME.observe(time.time() - start_time)

            # generate and publish metrics
            metrics = generate_latest(prometheus_metrics.registry)
            self.send_response(200)
            self.send_header('Content-Type', 'text/plain')
            self.end_headers()
            self.wfile.write(metrics)

        elif url.path == '/':
            self.send_response(200)
            self.send_header('Content-Type', 'text/html')
            self.end_headers()
            self.wfile.write("""<html>
            <head><title>HP iLO Exporter</title></head>
            <body>
            <h1>HP iLO Exporter</h1>
            <p>Visit <a href="/metrics">Metrics</a> to use.</p>
            </body>
            </html>""")

        else:
            if not error_detected:
                self.send_response(404)
                self.end_headers()


class ILOExporterServer(object):
    """
    Basic server implementation that exposes metrics to Prometheus
    """

    def __init__(self, address='0.0.0.0', port=8080, endpoint="/metrics"):
        self._address = address
        self._port = port
        self.endpoint = endpoint

    def print_info(self):
        print_err("Starting exporter on: http://{}:{}{}".format(self._address, self._port, self.endpoint))
        print_err("Press Ctrl+C to quit")

    def run(self):
        self.print_info()

        server = ForkingHTTPServer((self._address, self._port), RequestHandler)
        server.endpoint = self.endpoint

        try:
            while True:
                server.handle_request()
        except KeyboardInterrupt:
            print_err("Killing exporter")
            server.server_close()
