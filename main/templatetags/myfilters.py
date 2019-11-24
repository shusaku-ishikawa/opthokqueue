from django import template
register = template.Library()

@register.filter
def timeframeexists(value, arg):
    if not type(arg) != list:
        return None
    return (value in arg)
@register.filter
def concat(value, arg):
    return '{}_{}'.format(value, arg)
