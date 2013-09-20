#!/usr/bin/env python2.7

'''fvgui.py: Acts as a broker between JSON requests coming from the Django webpage and the callback from the FlowVisor. Provides persistent storage for topologies, links and flowtables.'''

import urllib
import json
import ConfigParser
import manage
import threading
from BaseHTTPServer import HTTPServer, BaseHTTPRequestHandler
from SocketServer import ThreadingMixIn

call_id = 1
flowtables = {}
links = {}
topologies = {}

class ThreadedHTTPServer(ThreadingMixIn, HTTPServer):
    allow_reuse_address = True

class JSONHandler(BaseHTTPRequestHandler):
    def log_message( self, format, *args ):
        pass

    def do_GET(self):
        pass

    def do_POST(self):
        header = self.headers.getheader('content-type')
        content_length = int(self.headers.getheader('content-length'))
        body = self.rfile.read(content_length)
        if (header == 'application/x-www-form-urlencoded') or (header == 'application/json'):
            post_json = json.loads(body)
            _id = post_json['id']
            if post_json['method'] == 'list-flowtable':
                result = get_flowtable(post_json['params']['dpid'])
                self.send_reply(_id, result)
            elif post_json['method'] == 'list-topology':
                result = topologies[post_json['params']['slice-name']]
                self.send_reply(_id, result)
            elif post_json['method'] == 'list-slices':
                result = get_slices()
                self.send_reply(_id, result)
            elif post_json['method'] == 'list-dpid':
                result = get_dpid_from_id(post_json['params']['id'], post_json['params']['slice-name'])
                self.send_reply(_id, result)
            elif post_json['method'] == 'flowtable-callback':
                flowtables.update({long(post_json['params'][0]['dpid']) : {str(post_json['params'][0]['cookie']) : post_json['params']}})
            elif post_json['method'] == 'slice-connected' or post_json['method'] == 'slice-disconnected' or post_json['method'] == 'device-connected':
                build_slices()
            else:
                response_data = urllib.urlopen(fv_url, body).read()
                self.send_response(200)
                self.end_headers()
                self.wfile.write(response_data)

    def send_reply(self, _id, result):
        self.send_response(200)
        self.send_header('Content-type','application/json')
        self.end_headers()
        message = json.dumps({'id':_id, 'result':result, 'jsonrpc':'2.0'})
        self.wfile.write(message)

def get_flowtable(dpid):
    try:
        dpid_long = get_long_from_dpid(dpid)
        return flowtables[dpid_long]
    except:
        return {'message' : 'No flowtable currently available. Waiting for callback.'}

def get_long_from_dpid(dpid):
    dpid = dpid.replace(':', '')
    dpid = long(dpid, 16)
    return dpid

def get_slices():
    slices = []
    for _slice in topologies:
        slices.append({'name' : _slice})
    return slices

def build_slices():
    global topologies
    global links 
    links = do_fv_call('list-links')
    slices = do_fv_call('list-slices')
    if slices != None and links != None:
        for _slice in slices['result']:
            dpid_count = 0
            slice_name = {}
            slice_name['slice-name'] = _slice['slice-name']
            slice_health = do_fv_call('list-slice-health', slice_name)
            if slice_health != None:
                d3_nodes = list()
                for dpid in slice_health['result']['connected-dpids']:
                    d3_nodes.append({'name': dpid, 'group': 1, 'id': dpid_count, 'dpid': dpid})
                    dpid_count += 1
                topologies[_slice['slice-name']] = {}
                topologies[_slice['slice-name']].update({'nodes':d3_nodes})
                build_links_for_slice(_slice['slice-name'])
            else:
                print 'Error: No slices found with the name %s' % _slice['slice-name']
                return False 
        return True
    else:
        print 'Error: No slices found.'
        return False 

def build_links_for_slice(_slice):
    global topologies
    global links
    d3_links = list()  
    for link in links['result']:
        src = get_id_from_dpid(link['srcDPID'], _slice)
        dst = get_id_from_dpid(link['dstDPID'], _slice)
        if src != None and dst != None:
            d3_links.append({'source': src, 'target': dst, 'value' : 10})
    topologies[_slice].update({'links':d3_links})

def get_id_from_dpid(dpid, _slice):
    for node in topologies[_slice]['nodes']:
        if str(node['dpid']) == str(dpid):
            return node['id']
    return None

def get_dpid_from_id(_id, _slice):
    for node in topologies[_slice]['nodes']:
        if int(node['id']) == int(_id):
            return node['dpid']
    return None

def do_fv_call(method, _input=None):
    global call_id
    if _input==None:
        post_data = None
        try:
            post_data = json.dumps({'id':call_id, 'method':method, 'jsonrpc':'2.0'})
        except json.JSONEncodeException as e:
            print 'Error: Could not encode JSON: %s' %e 
    else:
        try:
            post_data = json.dumps({'id':call_id, 'method':method, 'params':_input, 'jsonrpc':'2.0'})
        except json.JSONEncodeException as e:
            print 'Error: Could not encode JSON: %s' %e 
    try:
        response_data = urllib.urlopen(fv_url, post_data).read() 
        call_id += 1
        try:
            response_json = json.loads(response_data)
            return response_json
        except json.JSONDecodeException as e:
            print 'Error: Could not decode JSON: %s' %e 
    except IOError as e:
        print 'Error: Could not connect to FlowVisor instance: %s' % e

def do_fv_callbacks(url):
    callback = {'url' : url, 'method' : 'flowtable-callback', 'event-type' : 'FLOWTABLE_CALLBACK', 'name' : 'fvgui'}
    do_fv_call('register-event-callback', callback)
    callback['method'] = 'device-connected'
    callback['event-type'] = 'DEVICE_CONNECTED'
    do_fv_call('register-event-callback', callback)
    callback['method'] = 'slice-connected'
    callback['event-type'] = 'SLICE_CONNECTED'
    do_fv_call('register-event-callback', callback)
    callback['method'] = 'slice-disconnected'
    callback['event-type'] = 'SLICE_DISCONNECTED'
    do_fv_call('register-event-callback', callback)

if __name__ == '__main__':
    global fv_url
    config = ConfigParser.ConfigParser()
    config.read("fvgui.ini")
    fv_ip = str(config.get('flowvisor', 'ip'))
    fv_port = int(config.get('flowvisor', 'port'))
    fv_user = str(config.get('flowvisor', 'user'))
    fv_pass = str(config.get('flowvisor', 'pass'))
    fv_url =  'https://%s:%s@%s:%d' % (fv_user, fv_pass, fv_ip, fv_port)
    fvgui_ip = str(config.get('fvgui', 'ip'))
    fvgui_port = int(config.get('fvgui', 'port'))
    fvgui_url = 'http://%s:%d' % (fvgui_ip, fvgui_port)
    web_ip = str(config.get('web', 'ip'))
    web_port = int(config.get('web', 'port'))
    build_slices()
    do_fv_callbacks(fvgui_url)
    web_host = web_ip + ':' + str(web_port)
    django_args = ['manage.py', 'runserver', web_host, '--noreload']
    django_server = threading.Thread(target=manage.main, args=(django_args,), kwargs={})
    django_server.start()
    print 'fvgui running on %s:%i...' % (fvgui_ip, fvgui_port)
    server = ThreadedHTTPServer((fvgui_ip, fvgui_port), JSONHandler)
    server.serve_forever()