from django.http import Http404


def filter_ticket_request(request, df, service_id):

    filtered = df[df['SERVICE_ID'] == service_id]

    by = request.GET.get('by')
    query = request.GET.get('query')
    if by and query:
        queried = filtered[filtered[by].str.contains(query, case=False, na='')]
    else:
        queried = filtered

    return queried

def get_ticket_meta(df, service_id):
    try:
        link = df[df['SERVICE_ID'] == service_id].iloc[0]
    except IndexError:
        raise Http404(f'Service with service id {service_id} does not exist')

    service_detail = link.PRODUCT_DETAIL
    ba_num = link.BA_NUMBER
    ba_name = link.CA_NAME

    return [
        ['Service/Link/Circuit ID', service_id],
        ['Services', service_detail],
        ['BA Number/Ref', ba_num],
        ['BA Name', ba_name],
    ]