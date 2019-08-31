from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LogoutView
from django.http import Http404
from django.shortcuts import render, redirect

# Create your views here.
from django.urls import reverse
from django.views import View
from django.views.generic import TemplateView
import pandas as pd

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

class OpenTicketView(LoginRequiredMixin, View):

    def get(self, request, *args, service_id=None, **kwargs):

        filtered = open_tickets[open_tickets['SERVICE_ID'] == service_id]

        context = dict(data=filtered.values.tolist(), table_headings=filtered.columns.tolist())
        return render(request, template_name='core/open_ticket.html', context=context)


class ClosedTicketView(LoginRequiredMixin, View):

    def get(self, request, *args, service_id=None, **kwargs):
        filtered = closed_tickets[closed_tickets['SERVICE_ID'] == service_id]

        by = request.GET.get('by')
        query = request.GET.get('query')
        if by and query:
            queried = filtered[filtered[by].str.contains(query, case=False, na='')]
        else:
            queried = filtered

        mttr = queried.HANDLING_TIME_HOURS.mean()
        average_pending_time = queried.PENDING_TIME_HOURS.mean()
        most_problem_resolved = queried['PROBLEM_TIER 1'].mode().iloc[0]
        try:
            link = links_df[links_df['SERVICE_ID'] == service_id].iloc[0]
        except IndexError:
            raise Http404(f'Service with service id {service_id} does not exist')

        service_detail = link.PRODUCT_DETAIL
        ba_num = link.BA_NUMBER
        ba_name = link.CA_NAME

        metadata = [
            ['Service/Link/Circuit ID', service_id],
            ['Services', service_detail],
            ['BA Number/Ref', ba_num],
            ['BA Name', ba_name],
        ]

        context = dict(
            data=queried.values.tolist(),
            table_headings=queried.columns.tolist(),
            mttr=mttr,
            average_pending_time=average_pending_time,
            most_problem_resolved=most_problem_resolved,
            metadata=metadata,
        )



        return render(request, template_name='core/closed_ticket.html', context=context)


