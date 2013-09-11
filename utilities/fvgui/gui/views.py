#!/usr/bin/env python2.7

"""views.py: FlowVisor GUI: facilitating the visualisation of network slices in a running FlowVisor instance."""

import urllib
import argparse
import json
import jsonrpc
from BaseHTTPServer import HTTPServer, BaseHTTPRequestHandler
from SocketServer import ThreadingMixIn
from django.shortcuts import render

call_id = 1
links = {}
topologies = {}
url = None

def start_server():
    server = ThreadedHTTPServer(('localhost', 45000), JSONHandler)
    server.serve_forever()

def build_full_topology(_slice="fvadmin"):
    if build_slices():
        return write_d3_json(_slice)
        #print "Topology successfully generated! Please open index.html to view topology."
    else:
        print "Error: Could not generate initial topology"

def build_slices():
    slices = do_fv_call("list-slices")
    if slices != None:
        for _slice in slices["result"]:
            dpid_count = 0
            slice_name = {}
            slice_name["slice-name"] = _slice["slice-name"]
            slice_health = do_fv_call("list-slice-health", slice_name)
            if slice_health != None:
                d3_nodes = list()
                for dpid in slice_health["result"]["connected-dpids"]:
                    d3_nodes.append({'name': dpid, 'group': 1, 'id': dpid_count, 'dpid': dpid})
                    dpid_count += 1
                topologies[_slice["slice-name"]] = {}
                topologies[_slice["slice-name"]].update({"nodes":d3_nodes})
                build_links_for_slice(_slice["slice-name"])
            else:
                print "Error: No slices found with the name '%s'" % _slice["slice-name"]
                return False 
        return True
    else:
        print "Error: No slices found."
        return False 

# def build_datapaths(self):
#     datapaths = do_fv_call("list-datapaths")
#     if datapaths != None:
#         d3_nodes = list()
#         for dpid in datapaths["result"]:
#             d3_nodes.append({"name": dpid, "group": 1, "id": dpid_count, "dpid": dpid})
#             dpid_count += 1
#         topology.update({"nodes":d3_nodes})
#         return True
#     else:
#         print "Error: No DPIDs found in topology."
#         return False

def get_links():
    global links 
    links = do_fv_call("list-links")
    if links != None:
        return True
    else:
        print "Error: No links found in FlowVisor."
        return False

def build_links_for_slice(_slice="fvadmin"):
    global topologies
    global links
    d3_links = list()  
    for link in links["result"]:
        src = find_id_from_dpid(link["srcDPID"], _slice)
        dst = find_id_from_dpid(link["dstDPID"], _slice)
        if src != None and dst != None:
            d3_links.append({'source': src, 'target': dst, 'value' : 3})
    topologies[_slice].update({"links":d3_links})

def find_id_from_dpid(dpid, _slice="fvadmin"):
    for node in topologies[_slice]["nodes"]:
        if node["dpid"] == dpid:
            return node["id"]
    return None

def do_fv_call(method, _input=None):
    global call_id
    if _input==None:
        post_data = None
        try:
            post_data = json.dumps({"id":call_id, "method":method, "jsonrpc":"2.0"})
        #except JSONEncodeException as exception:
        except Exception as e:
            print "Error: %s" %e 
    else:
        try:
            post_data = json.dumps({"id":call_id, "method":method, "params":_input, "jsonrpc":"2.0"})
        except Exception as e:
            print "Error: %s" %e 
    try:
        response_data = urllib.urlopen(url, post_data).read() 
        call_id += 1
        try:
            response_json = json.loads(response_data)
            return response_json
        except Exception as e:
            print "Error: %s" %e 
    except IOError as exception:
        print "Error: Could not connect to FlowVisor instance: %s" % exception

def write_d3_json(_slice="fvadmin"):
    topology = json.dumps(topologies[_slice])
    return topology

# def parse_arguments():
#     global url
#     parser = argparse.ArgumentParser(description='FlowVisor GUI: facilitating the visualisation of network slices in a running FlowVisor instance.')
#     parser.add_argument('-i', '--ip', dest="ip", required=True, help='IP address of running FlowVisor instance.')
#     parser.add_argument('-p', '--port', dest="port",default="8081", help='JSON-RPC port of running FlowVisor isntance.')
#     parser.add_argument('-u', '--username', dest="username", default="fvadmin", help='Username of FlowVisor user.')
#     parser.add_argument('-pw', '--password', dest="password", required=True, help='Password of FlowVisor user.')
#     parser.add_argument('-s', '--slice', dest="slice", default="fvadmin", help='FlowVisor slice you wish to visualise.')
#     arguments = parser.parse_args()
#     url =  "https://%s:%s@%s:%d" % (arguments.username, arguments.password, arguments.ip, int(arguments.port))
#     return arguments.slice

class ThreadedHTTPServer(ThreadingMixIn, HTTPServer):
    allow_reuse_address = True

class JSONHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        pass

    def do_POST(self):
        header = self.headers.getheader('content-type')
        if header == 'application/x-www-form-urlencoded':
            content_length = int(self.headers.getheader('content-length'))
            post_body = self.rfile.read(content_length)
            post_json = loads(post_body)
            _id = post_json["id"]
            if post_json["method"] == "get-slices":
                result = []
                for slice_name in topologies:
                    self.result.append({'slice-name' : slice_name})
                self.send_result(_id, result)
            elif post_json["method"] == "set-topology":
                write_d3_json(post_json["params"]["slice-name"])
                self.send_result(_id, True)
            elif post_json["method"] == "get-flowtable":
                #return most recent version of flowtable for a switch\
                #need to use callbacks - can also use list-datapath-stats and info
                pass
            elif post_json["method"] == "get-slice-stats":
                #for each slice, we want to use stats, health and info
                pass
            elif post_json["method"] == "get-fv-health":
                #get fv stats
                pass

    def send_result(self, _id, result):
        self.send_response(200)
        self.end_headers()
        message = dumps({"id":_id, "result":result, "jsonrpc":"2.0"})
        self.wfile.write(message)

def get_slices():
    result = []
    for slice_name in topologies:
        result.append({'name' : slice_name})
    return result

def index(request):
    global url
    url =  "https://%s:%s@%s:%d" % ("fvadmin", "ofwork", "192.168.56.101", int("8081"))
    get_links()
    topology = build_full_topology()
    context = {'slices' : get_slices(), 'name' : 'fvadmin', 'topology' : topology}
    return render(request, 'gui/index.html', context)

def slice(request, slice_name):
    global url
    url =  "https://%s:%s@%s:%d" % ("fvadmin", "ofwork", "192.168.56.101", int("8081"))
    _slice = "fvadmin"
    get_links()
    topology = build_full_topology(slice_name)
    context = {'slices' : get_slices(), 'name' : slice_name, 'topology' : topology}
    return render(request, 'gui/index.html', context)