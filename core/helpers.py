from datetime import datetime, timedelta

import numpy as np
from django.conf import settings
from django.http import Http404

def is_int_dtype(series):
    return series.dtype.char in np.typecodes['AllInteger']


def query_request(request, df):
    by = request.GET.get('by')
    query = request.GET.get('query')
    if by and query:
        if is_int_dtype(df[by]):
            queried = df[df[by].astype('str').str.contains(query, case=False, na=False)]
        else:
            queried = df[df[by].str.contains(query, case=False, na=False)]
    else:
        queried = df

    return queried

def filter_ticket_request(request, df, service_id):
    filtered = df[df['SERVICE_ID'] == service_id]
    return query_request(request, filtered)


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

def is_expired_soon(termination_date):
    diff = termination_date - datetime.today()
    return diff < timedelta(days=60) and diff > timedelta(0, 0)


def as_rupiah(num):
    return 'Rp{:,.2f}'.format(num)


def transform_single_user(user):
    try:
        position = settings.HIERARCHY_LEVEL_NAMES[user.level - 1] if user.level else 'N/A'
    except KeyError:
        raise ValueError(f'Corrupted data: user with username {user.username} has invalid level: {user.level}.')


    return [
        user.username,
        user.name,
        position,
        getattr(user.level_2_superior, 'name', 'N/A'),
        getattr(user.level_3_superior, 'name', 'N/A'),
        getattr(user.level_4_superior, 'name', 'N/A'),
        user.last_login,
        'Yes' if user.is_staff else 'No',
    ]

def process_user_data(users):
    return [transform_single_user(user) for user in users]

def filter_results_by_user(request, df):
    user = request.user
    if user.is_staff or df.empty:
        return df
    if user.level == 1:
        return df[df['SALES_NAME'] == user.username]
    else:
        subordinate_usernames = {s.username for s in getattr(user, f'subordinates_{user.level}').all()}
        return df[df['SALES_NAME'].apply(lambda name: name in subordinate_usernames)]
