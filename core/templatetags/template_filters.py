from django import template

register = template.Library()

@register.filter
def getitem(l, i):
    try:
        return l[i]
    except:
        return None