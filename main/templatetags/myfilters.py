from django import template
from main.models import *
import re
register = template.Library()

@register.filter
def timeframeexists(value, arg):
    if type(arg) != list:
        print('invalidd')
        return None
    return (value in arg)

@register.filter
def check_additional_field(value, arg):

    if not isinstance(value, UserEntry):
        print('this is not the instnace')
        return None
    if not re.fullmatch('\d+\-\d+', arg):
        print('re match got invalid format')
        return None
    (field_id, option_id) = arg.split('-')
    matched = [item for item in value.additional_items.all() if (item.question.id == int(field_id) and item.chosen_option.id == int(option_id))]
    print(matched)
    return len(matched) > 0

@register.filter
def invited_options(invite, field):

    return [op.chosen_option for op in invite.additional_items.all() if op.question.id == field.id]
@register.filter
def concat(value, arg):
    return '{}_{}'.format(value, arg)

@register.filter
def concatwithdash(value, arg):
    return '{}-{}'.format(value, arg)


