from django import template

register = template.Library()

@register.filter
def getitem(l, i):
    try:
        return l[i]
    except:
        return None


@register.simple_tag
def paginate(request, page):
    updated = request.GET.copy()
    updated['page'] = page
    return updated.urlencode()