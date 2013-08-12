#!/usr/bin/env python2.7

"""fvgui.py: FlowVisor GUI: facilitating the visualisation of network slices in a running FlowVisor instance."""

import urllib
import argparse
from jsonrpc.json import loads, dumps, JSONEncodeException, JSONDecodeException


class main():
    call_id = 1
    links = {}
    topologies = {}
    url = None
    
    def __init__(self):
        _slice = self.parse_arguments()
        self.get_links()
        self.build_full_topology(_slice)

    def build_full_topology(self, _slice="fvadmin"):
        if self.build_slices():
            self.write_d3_json(_slice)
            print "Topology successfully generated! Please open index.html to view topology."
        else:
            print "Error: Could not generate initial topology"

    def build_slices(self):
        slices = self.do_fv_call("list-slices")
        if slices != None:
            for _slice in slices["result"]:
                dpid_count = 0
                slice_name = {}
                slice_name["slice-name"] = _slice["slice-name"]
                slice_health = self.do_fv_call("list-slice-health", slice_name)
                if slice_health != None:
                    d3_nodes = list()
                    for dpid in slice_health["result"]["connected-dpids"]:
                        d3_nodes.append({"name": dpid, "group": 1, "id": dpid_count, "dpid": dpid})
                        dpid_count += 1
                    self.topologies[_slice["slice-name"]] = {}
                    self.topologies[_slice["slice-name"]].update({"nodes":d3_nodes})
                    self.build_links_for_slice(_slice["slice-name"])
                else:
                    print "Error: No slices found with the name '%s'" % _slice["slice-name"]
                    return False 
            return True
        else:
            print "Error: No slices found."
            return False 

    # def build_datapaths(self):
    #     datapaths = self.do_fv_call("list-datapaths")
    #     if datapaths != None:
    #         d3_nodes = list()
    #         for dpid in datapaths["result"]:
    #             d3_nodes.append({"name": dpid, "group": 1, "id": self.dpid_count, "dpid": dpid})
    #             self.dpid_count += 1
    #         self.topology.update({"nodes":d3_nodes})
    #         return True
    #     else:
    #         print "Error: No DPIDs found in topology."
    #         return False

    def get_links(self):
        self.links = self.do_fv_call("list-links")
        if self.links != None:
            return True
        else:
            print "Error: No links found in FlowVisor."
            return False

    def build_links_for_slice(self, _slice="fvadmin"):
        d3_links = list()  
        for link in self.links["result"]:
            src = self.find_id_from_dpid(link["srcDPID"], _slice)
            dst = self.find_id_from_dpid(link["dstDPID"], _slice)
            if src != None and dst != None:
                d3_links.append({"source": src, "target": dst, "value" : 3})
        self.topologies[_slice].update({"links":d3_links})

    def find_id_from_dpid(self, dpid, _slice="fvadmin"):
        for node in self.topologies[_slice]["nodes"]:
            if node["dpid"] == dpid:
                return node["id"]
        return None

    def do_fv_call(self, method, _input=None):
        if _input==None:
            try:
                post_data = dumps({"id":self.call_id, "method":method, "jsonrpc":"2.0"})
            except JSONEncodeException as exception:
                print "Error: Could not encode JSON for FlowVisor request: %s" % exception
        else:
            try:
                post_data = dumps({"id":self.call_id, "method":method, "params":_input, "jsonrpc":"2.0"})
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

    def write_d3_json(self, _slice="fvadmin"):
        json_file = None
        try:
            json_file = open('topology.json', 'w+')
        except IOError as exception:
            print "Error: Could not open D3.js topology file: %s" % exception
        try:
            try:
                json_file.write(dumps(self.topologies[_slice]))
            except KeyError as exception:
                print "Error: Slice with name '%s' not found." % _slice
        except (IOError, JSONEncodeException) as exception:
            print "Error: Could not write topology to D3.js topology file: %s" % exception
        if json_file != None:
            json_file.close()

    def parse_arguments(self):
        parser = argparse.ArgumentParser(description='FlowVisor GUI: facilitating the visualisation of network slices in a running FlowVisor instance.')
        parser.add_argument('-i', '--ip', dest="ip", required=True, help='IP address of running FlowVisor instance.')
        parser.add_argument('-p', '--port', dest="port",default="8081", help='JSON-RPC port of running FlowVisor isntance.')
        parser.add_argument('-u', '--username', dest="username", default="fvadmin", help='Username of FlowVisor user.')
        parser.add_argument('-pw', '--password', dest="password", required=True, help='Password of FlowVisor user.')
        parser.add_argument('-s', '--slice', dest="slice", default="fvadmin", help='FlowVisor slice you wish to visualise.')
        arguments = parser.parse_args()
        self.url =  "https://%s:%s@%s:%d" % (arguments.username, arguments.password, arguments.ip, int(arguments.port))
        return arguments.slice


if __name__ == "__main__":
    main()