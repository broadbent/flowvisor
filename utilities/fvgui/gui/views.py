#!/usr/bin/env python2.7

'''views.py: Describes methods to be called when specific web pages are requested. Makes JSON requests back to fvgui and returns data to web page.'''

import urllib
import json
import ConfigParser
from django.shortcuts import render

fvgui_url = None
init = False
call_id = 1

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
        response_data = urllib.urlopen(fvgui_url, post_data).read() 
        call_id += 1
        try:
            response_json = json.loads(response_data)
            return response_json
        except json.JSONDecodeException as e:
            print 'Error: Could not decode JSON: %s' %e 
    except IOError as e:
        print 'Error: Could not connect to FlowVisor instance: %s' % e

def config():
    global init
    global fvgui_url
    config = ConfigParser.ConfigParser()
    config.read("fvgui.ini")
    fvgui_ip = str(config.get('fvgui', 'ip'))
    fvgui_port = int(config.get('fvgui', 'port'))
    fvgui_url = 'http://%s:%d' % (fvgui_ip, fvgui_port)
    init = True

def index(request):
    if not init:
        config()   
    slices = do_fv_call('list-slices')
    # set default slice as first slice in list-slices
    _slice = slices['result'][0]['name']
    topology = do_fv_call('list-topology', {'slice-name' : _slice})
    slicestats = do_fv_call('list-slice-health', {'slice-name' : _slice})
    fvstats = do_fv_call('list-fv-health')
    fvversion = do_fv_call('list-version')
    context = {'slices' : slices['result'], 'name' : _slice, 'topology' : json.dumps(topology['result']), 'slicestats' : json.dumps(slicestats['result']), 'fvstats' : json.dumps(fvstats['result']), 'fvversion' : json.dumps(fvversion['result'])}
    return render(request, 'gui/index.html', context)

def slice(request, _slice):
    if not init:
        config() 
    topology = do_fv_call('list-topology', {'slice-name' : _slice})
    slices = do_fv_call('list-slices')
    slicestats = do_fv_call('list-slice-health', {'slice-name' : _slice})
    fvstats = do_fv_call('list-fv-health')
    fvversion = do_fv_call('list-version')
    context = {'slices' : slices['result'], 'name' : _slice, 'topology' : json.dumps(topology['result']), 'slicestats' : json.dumps(slicestats['result']), 'fvstats' : json.dumps(fvstats['result']), 'fvversion' : json.dumps(fvversion['result'])}
    return render(request, 'gui/index.html', context)

def dpid(request, _slice, _id):
    if not init:
        config()
    dpid = do_fv_call('list-dpid', {'id' : _id, 'slice-name' : _slice})
    dpid = dpid['result']
    dpidinfo = do_fv_call('list-datapath-info', {'dpid' : dpid})
    dpidstats = do_fv_call('list-datapath-stats', {'dpid' : dpid})
    flowtable = do_fv_call('list-flowtable', {'dpid' : dpid})
    context = {'dpid': dpid, 'id' : _id, 'dpidinfo' : json.dumps(dpidinfo['result']), 'dpidstats' : json.dumps(dpidstats['result']), 'flowtable' : json.dumps(flowtable['result'])}
    return render(request, 'gui/dpid.html', context)