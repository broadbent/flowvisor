#!/usr/bin/env python2.7

'''views.py: Describes methods to be called when specific web pages are requested. Makes JSON requests back to fvgui and returns data to web page.'''

import urllib
import json
import ConfigParser
from django.shortcuts import render

fvgui_url = None
init = False
call_id = 1

def do_fvgui_call(method, _input=None):
    '''Make call to FVGUI JSON server  with given method and input.'''
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
        response_data = urllib.urlopen(fvgui_url, post_data).read() 
        call_id += 1
        try:
            response_json = json.loads(response_data)
            return response_json
        except json.JSONDecodeException as e:
            print 'Error: Could not decode JSON: %s' %e 
    except IOError as e:
        print 'Error: Could not connect to FVGUI JSON Server: %s' % e

def config():
    '''Read configuration file for IP and port of FVGUI JSON server.
    Note: Only done once for the first request - persistent afterwards.
    '''
    global init
    global fvgui_url
    config = ConfigParser.ConfigParser()
    config.read("fvgui.ini")
    fvgui_ip = str(config.get('fvgui', 'ip'))
    fvgui_port = int(config.get('fvgui', 'port'))
    fvgui_url = 'http://%s:%d' % (fvgui_ip, fvgui_port)
    init = True

def index(request):
    '''Handle request for visualisation of a slice's topology without a given slice.
    Note: Will use first slice returned from list-slices.
    '''
    if not init:
        config()   
    slices = do_fvgui_call('list-slices')
    _slice = slices['result'][0]['name']
    topology = do_fvgui_call('list-topology', {'slice-name' : _slice})
    slicestats = do_fvgui_call('list-slice-health', {'slice-name' : _slice})
    fvstats = do_fvgui_call('list-fv-health')
    fvversion = do_fvgui_call('list-version')
    context = {'slices' : slices['result'], 'name' : _slice, 'topology' : json.dumps(topology['result']), 'slicestats' : json.dumps(slicestats['result']), 'fvstats' : json.dumps(fvstats['result']), 'fvversion' : json.dumps(fvversion['result'])}
    return render(request, 'gui/index.html', context)

def slice(request, _slice):
    '''Handle request for the visualisation of a specific slice's topology.'''
    if not init:
        config() 
    topology = do_fvgui_call('list-topology', {'slice-name' : _slice})
    slices = do_fvgui_call('list-slices')
    slicestats = do_fvgui_call('list-slice-health', {'slice-name' : _slice})
    fvstats = do_fvgui_call('list-fv-health')
    fvversion = do_fvgui_call('list-version')
    context = {'slices' : slices['result'], 'name' : _slice, 'topology' : json.dumps(topology['result']), 'slicestats' : json.dumps(slicestats['result']), 'fvstats' : json.dumps(fvstats['result']), 'fvversion' : json.dumps(fvversion['result'])}
    return render(request, 'gui/index.html', context)

def dpid(request, _slice, _id):
    '''Handle request for the visualisation of a specific DPID's flowtable.'''
    if not init:
        config()
    dpid = do_fvgui_call('list-dpid', {'id' : _id, 'slice-name' : _slice})
    dpid = dpid['result']
    dpidinfo = do_fvgui_call('list-datapath-info', {'dpid' : dpid})
    dpidstats = do_fvgui_call('list-datapath-stats', {'dpid' : dpid})
    flowtable = do_fvgui_call('list-flowtable', {'dpid' : dpid})
    context = {'dpid': dpid, 'slice' : _slice, 'id' : _id, 'dpidinfo' : json.dumps(dpidinfo['result']), 'dpidstats' : json.dumps(dpidstats['result']), 'flowtable' : json.dumps(flowtable['result'])}
    return render(request, 'gui/dpid.html', context)