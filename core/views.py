from datetime import datetime, timedelta

import pandas as pd
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import SuspiciousOperation
from django.core.paginator import Paginator
from django.http import Http404
from django.shortcuts import render, redirect
# Create your views here.
from django.urls import reverse
from django.views import View
from django.views.generic import TemplateView

from core.helpers import filter_ticket_request, get_ticket_meta, query_request, is_expired_soon, as_rupiah

fname = 'CHURN DASHBOARD 2019.xlsx'
hierarchy_sheet_name = 'SALES HIERARCHY'
links_sheet_name = 'ASSET MIDI LINKS'
sla_sheet_name = 'TICKET PERFORMANCE SLA'
closed_ticket_sheet_name = 'CLOSED TICKET'
open_ticket_sheet_name = 'IN PROGRESS TICKET'

def read_excel(sheet_name):
    return pd.read_excel(fname, sheet_name)

def load_open_tickets():
    return read_excel(open_ticket_sheet_name)


def load_links():
    df = read_excel(links_sheet_name)
    return df[pd.notnull(df.SALES_NAME)]

def load_closed_tickets():
    return read_excel(closed_ticket_sheet_name)

open_tickets = load_open_tickets()
closed_tickets = load_closed_tickets()
links_df = read_excel(links_sheet_name)

class IndexView(TemplateView):
    def get(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect(reverse('core:dashboard'))
        else:
            return redirect(reverse('core:login'))

class DashboardView(LoginRequiredMixin, View):

    def get(self, request, *args, **kwargs):

        table_headings = links_df.columns.tolist()

        queried = query_request(request, links_df)

        try:
            req_page = request.GET.get('page', 1) or 1
            page_num = int(req_page)
        except (ValueError, TypeError):
            raise SuspiciousOperation('Page number is invalid')

        p = Paginator(queried.values.tolist(), 50)

        data = p.page(page_num)

        total_mrc = as_rupiah(queried.MRC_IDR.sum())
        links_expired_soon = queried[queried['TERMINATION_DATE'].apply(is_expired_soon)]
        mrc_expired_soon = as_rupiah(links_expired_soon['MRC_IDR'].sum())
        num_expired_soon = len(links_expired_soon)

        context = dict(
            table_headings=table_headings,
            data=data,
            page_range=range(1, p.num_pages + 1),
            current_page=page_num,
            paginator=p,
            total_mrc=total_mrc,
            mrc_expired_soon=mrc_expired_soon,
            num_expired_soon=num_expired_soon,
        )

        return render(request, 'core/dashboard.html', context)


class ClosedTicketView(LoginRequiredMixin, View):

    def get(self, request, *args, service_id=None, **kwargs):
        queried = filter_ticket_request(request, closed_tickets, service_id)
        metadata = get_ticket_meta(links_df, service_id)

        mttr = queried.HANDLING_TIME_HOURS.mean() or 'N/A'
        average_pending_time = queried.PENDING_TIME_HOURS.mean() or 'N/A'

        try:
            most_problem_resolved = queried['PROBLEM_TIER 1'].mode().iloc[0]
        except IndexError:
            most_problem_resolved = 'N/A'


        context = dict(
            data=queried.values.tolist(),
            table_headings=queried.columns.tolist(),
            mttr=mttr,
            average_pending_time=average_pending_time,
            most_problem_resolved=most_problem_resolved,
            metadata=metadata,
        )



        return render(request, template_name='core/closed_ticket.html', context=context)


class OpenTicketView(LoginRequiredMixin, View):

    def get(self, request, *args, service_id=None, **kwargs):
        queried = filter_ticket_request(request, open_tickets, service_id)
        metadata = get_ticket_meta(links_df, service_id)

        buffer = timedelta(days=3)

        average_sr_duration = queried.SR_DURATION_HOURS.mean()
        num_late = len(queried[queried.TICKET_DUE_DATE.apply(lambda x: x < datetime.today())])
        num_expired_soon = len(queried[queried.TICKET_DUE_DATE.apply(lambda x: x - datetime.today() < buffer)])  - num_late


        context = dict(
            data=queried.values.tolist(),
            table_headings=queried.columns.tolist(),
            average_sr_duration=average_sr_duration,
            num_late=num_late,
            num_expired_soon=num_expired_soon,
            metadata=metadata,
        )



        return render(request, template_name='core/open_ticket.html', context=context)