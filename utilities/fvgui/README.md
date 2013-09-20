# FlowVisor GUI #

The FlowVisor GUI (FVGUI) is designed as a tool to virtualise slices on a running FlowVisor instance.

## Requirements ##

FVGUI uses [Python](http://www.python.org/), [Django](https://www.djangoproject.com/) and [D3.js](http://d3js.org/).

### Python ###

FVGUI requires version 2.7 of Python: <http://www.python.org/download/releases/2.7.5/>

### Django ###

FVGUI is built using Django 1.5.3: <https://www.djangoproject.com/download/1.5.3/tarball/>. See the [installation guide](https://docs.djangoproject.com/en/1.5/intro/install/) for more details.

### D3.js ###

The latest version of D3.js is included with FVGUI.

## Configuration ##

FVGUI is configured via the ```fvgui.ini``` file. The distribution includes a sample configuration file; you will need to change this to atleast point to your running FlowVisor instance. This configuration file also facilitates starting the serving on an alternate IP and port.

## Run ##

FVGUI uses Django's built in server. This is automatically started when you run FVGUI with:

```bash
$ python fvgui.py 
```

By default, the server will then start at: <http://127.0.0.1:8000/gui/>. This can be configured in the ```fvgui.ini``` file.

__Please note__: the Django webserver that FVGUI currently uses is not intended for production use. See [runserver](https://docs.djangoproject.com/en/dev/ref/django-admin/#django-admin-runserver) for more details.

## Author ##

FVGUI is developed and maintained by Matthew Broadbent (<matt@matthewbroadbent.net>). Initial development was undertaken as part of the [Google Summer of Code 2013](http://www.google-melange.com/gsoc/homepage/google/gsoc2013). FVGUI It is part of the main FlowVisor release, which can be found at: <https://github.com/OPENNETWORKINGLAB/flowvisor>.
