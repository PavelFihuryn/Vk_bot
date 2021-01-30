"""
Handler - function which get to entered text (text received message)
and context, and return bool: True, if step passed or False, if date is incorrect
"""
import re

from draw_ticket import draw_ticket

re_name = re.compile(r'^[\w\-\s]{3,40}$')
re_email = re.compile(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b')


def handler_name(text, context):
    match = re.match(re_name, text)
    if match:
        context['name'] = text
        return True
    else:
        return False


def handler_email(text, context):
    matches = re.findall(re_email, text)
    if len(matches) > 0:
        context['email'] = matches[0]
        return True
    else:
        return False


def draw_ticket_handler(text, context):
    return draw_ticket(name=context['name'], email=context['email'])
