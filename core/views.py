from datetime import datetime, timedelta

import pandas as pd
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import Http404
from django.shortcuts import render, redirect
# Create your views here.
from django.urls import reverse
from django.views import View
from django.views.generic import TemplateView

from core.helpers import filter_ticket_request, get_ticket_meta

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

class DashboardView(LoginRequiredMixin, TemplateView):
    template_name = 'core/dashboard.html'


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