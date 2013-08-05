#!/usr/bin/env python2.7

"""fvgui.py: FlowVisor GUI: facilitating the visualisation of network slices in a running FlowVisor instance."""

import urllib
import argparse
from jsonrpc.json import loads, dumps, JSONEncodeException, JSONDecodeException


class main():
    call_id = 1
    dpid_count = 0
    topology = {}
    url = None
    json_file = None
    
    def __init__(self):
        self.form_url()
        self.build_full_topology()
        print "Operation completed! Please open index.html to view topology."

    def build_full_topology(self):
        if self.add_all_datapaths() and self.add_all_links():
            self.write_d3_json()

    def add_all_datapaths(self):
        datapaths = self.do_fv_call("list-datapaths")
        if datapaths != None:
            d3_nodes = list()
            for dpid in datapaths["result"]:
                d3_nodes.append({"name": dpid, "group": 1, "id": self.dpid_count, "dpid": dpid})
                self.dpid_count += 1
            self.topology.update({"nodes":d3_nodes})
            return True
        else:
            print "Error: No DPIDs found in topology."
            return False

    def add_all_links(self):
        links = self.do_fv_call("list-links")
        if links != None:
            d3_links = list()  
            for link in links["result"]:
                src = self.find_id_from_dpid(link["srcDPID"])
                dst = self.find_id_from_dpid(link["dstDPID"])
                if src != None and dst != None:
                    d3_links.append({"source": src, "target": dst, "value" : 3})
                else:
                    print "Note: Unknown DPID found in list of topology links. Ignoring."        
            self.topology.update({"links":d3_links})
            return True
        else:
            print "Error: No links found in topology."
            return False

    def find_id_from_dpid(self, dpid):
        for node in self.topology["nodes"]:
            if node["dpid"] == dpid:
                return node["id"]
        return None

    def do_fv_call(self, method):
        try:
            post_data = dumps({"id":self.call_id, "method":method, "jsonrpc":"2.0"})
        except JSONEncodeException as exception:
            print "Error: Could not encode JSON for FlowVisor request: %s" % exception
        try:
            response_data = urllib.urlopen(self.url, post_data).read() 
            self.call_id += 1
            try:
                response_json = loads(response_data)
                return response_json
            except JSONDecodeException as exception:
                print "Error: Could not decode JSON from FlowVisor response: %s" % exception
        except IOError as exception:
            print "Error: Could not connect to FlowVisor instance: %s" % exception

    def write_d3_json(self):
        try:
            self.json_file = open('topology.json', 'w+')
        except IOError as exception:
            print "Error: Could not open D3.js topology file: %s" % exception
        try:
            self.json_file.write(dumps(self.topology))
        except (IOError, JSONEncodeException) as exception:
            print "Error: Could not write topology to D3.js topology file: %s" % exception
        if self.json_file != None:
            self.json_file.close()

    def form_url(self):
        parser = argparse.ArgumentParser(description='FlowVisor GUI: facilitating the visualisation of network slices in a running FlowVisor instance.')
        parser.add_argument('-i', '--ip', dest="ip", required=True, help='IP address of running FlowVisor instance.')
        parser.add_argument('-p', '--port', dest="port",default="8081", help='JSON-RPC port of running FlowVisor isntance.')
        parser.add_argument('-u', '--username', dest="username", default="fvadmin", help='Username of FlowVisor user.')
        parser.add_argument('-pw', '--password', dest="password", required=True, help='Password of FlowVisor user.')
        arguments = parser.parse_args()
        self.url =  "https://%s:%s@%s:%d" % (arguments.username, arguments.password, arguments.ip, int(arguments.port))


if __name__ == "__main__":
    main()