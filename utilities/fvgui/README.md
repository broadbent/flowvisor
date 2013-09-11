# FlowVisor GUI #

The FlowVisor GUI (FVGUI) is designed as a tool to virtualise slices on a running FlowVisor instance.

## Requirements ##

FVGUI uses [Python](http://www.python.org/), [Django](https://www.djangoproject.com/) and [D3.js](http://d3js.org/).

### Python ###

FVGUI requires version 2.7 of Python: http://www.python.org/download/releases/2.7.5/

### Django ###

FVGUI is built using Django 1.5.3: https://www.djangoproject.com/download/1.5.3/tarball/

### D3.js ###

The latest version of D3.js is included with FVGUI.

## Running FlowVisor GUI ##

FVGUI uses Django's built in server. This can be started using the following command, run inside the fvgui folder:

``` python manage.py runserver ```

The server will then start at: http://127.0.0.1:8000/

In addition, to change the port of the webserver, use:

``` python manage.py runserver 8080 ```

Also, to change the IP address of the webserver, use:

``` python manage.py runserver 0.0.0.0:8000 ```

__Please note__: the Django webserver is not intended for production use. See [runserver](https://docs.djangoproject.com/en/dev/ref/django-admin/#django-admin-runserver) for more details.

## Author ##

FVGUI is developed and maintained by Matthew Broadbent (matt@matthewbroadbent.net). Initial development was undertaken as part of the [Google Summer of Code 2013](http://www.google-melange.com/gsoc/homepage/google/gsoc2013). FVGUIUI It is part of the main FlowVisor release, which can be found at: https://github.com/OPENNETWORKINGLAB/flowvisor.
