from django import template
from django.utils import simplejson as json

register = template.Library()

@register.filter
def json_list(value):
    """
    Returns the json list formatted for display
    Use it like this :

    {{ myjsonlist|json_list }}
    """
    try:
        dict = json.loads(value)
        print dict
        result = []
        for field in dict:
            result.append(str(field) + ": <span class=values>" + str(json.dumps(dict[field])) + "</span></br>")
        return ''.join(result)
    except Exception as e:
        print e
        return value