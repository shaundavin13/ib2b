from datetime import datetime, timedelta

import pandas as pd
from django.conf import settings
from django.contrib import messages
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import PasswordChangeView
from django.core.exceptions import SuspiciousOperation
from django.core.paginator import Paginator
from django.shortcuts import render, redirect
# Create your views here.
from django.urls import reverse, reverse_lazy
from django.utils.decorators import method_decorator
from django.views import View
from django.views.generic import TemplateView

from core.DataManager import DataManager
from core.UserManager import UserManager
from core.helpers import filter_ticket_request, get_ticket_meta, query_request, is_expired_soon, as_rupiah, \
    process_user_data, filter_results_by_user
from core.history_manager import HistoryManager
from core.models import User

data_manager = DataManager()
user_manager = UserManager()

class IndexView(TemplateView):
    def get(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect(reverse('core:dashboard'))
        else:
            return redirect(reverse('core:login'))

class DashboardView(LoginRequiredMixin, View):

    def get(self, request, *args, **kwargs):

        if not data_manager._initialized:
            return render(request, template_name='core/dashboard.html')

        table_headings = data_manager.links_df.columns.tolist()

        queried = query_request(request, data_manager.links_df)

        try:
            req_page = request.GET.get('page', 1) or 1
            page_num = int(req_page)
        except (ValueError, TypeError):
            raise SuspiciousOperation('Page number is invalid')

        queried = filter_results_by_user(request, queried)

        p = Paginator(queried.fillna('-').values.tolist(), 50)

        data = p.page(page_num)

        total_mrc = as_rupiah(queried.MRC_IDR.sum())

        links_expired_soon = queried if queried.empty else queried[queried['TERMINATION_DATE'].apply(is_expired_soon)]
        mrc_expired_soon = as_rupiah(links_expired_soon['MRC_IDR'].sum())
        num_expired_soon = len(links_expired_soon)

        service_id_index = table_headings.index('SERVICE_ID')
        open_ticket_index = table_headings.index('OPEN_TICKET')
        closed_ticket_index = table_headings.index('CLOSED_TICKET')

        dtypes = [(col, data_manager.links_df[col].dtype.name) for col in data_manager.links_df.columns]
        searchable_columns = [i[0] for i in dtypes if i[1] == 'object']

        context = dict(
            table_headings=table_headings,
            searchable_columns=searchable_columns,
            data=data,
            page_range=range(1, p.num_pages + 1),
            current_page=page_num,
            paginator=p,
            total_mrc=total_mrc,
            mrc_expired_soon=mrc_expired_soon,
            num_expired_soon=num_expired_soon,
            service_id_index=service_id_index,
            open_ticket_index=open_ticket_index,
            closed_ticket_index=closed_ticket_index,
            query=request.GET.get('query'),
            filter_by=request.GET.get('by'),
        )

        return render(request, 'core/dashboard.html', context)


class ClosedTicketView(LoginRequiredMixin, View):

    def get(self, request, *args, service_id=None, **kwargs):
        if not data_manager._initialized:
            return render(request, template_name='core/closed_ticket.html')  # todo: conditional in template for empty state
        queried = filter_ticket_request(request, data_manager.closed_tickets_df, service_id)
        metadata = get_ticket_meta(data_manager.links_df, service_id)

        mttr = queried.HANDLING_TIME_HOURS.mean() or 'N/A'
        average_pending_time = queried.PENDING_TIME_HOURS.mean() or 'N/A'

        try:
            most_problem_resolved = queried['PROBLEM_TIER 1'].mode().iloc[0]
        except IndexError:
            most_problem_resolved = 'N/A'

        dtypes = [(col, data_manager.closed_tickets_df[col].dtype.name) for col in data_manager.closed_tickets_df.columns]
        searchable_columns = [i[0] for i in dtypes if i[1] == 'object']

        context = dict(
            data=queried.fillna('-').values.tolist(),
            table_headings=queried.columns.tolist(),
            searchable_columns=searchable_columns,
            mttr=mttr,
            average_pending_time=average_pending_time,
            most_problem_resolved=most_problem_resolved,
            metadata=metadata,
        )



        return render(request, template_name='core/closed_ticket.html', context=context)


class OpenTicketView(LoginRequiredMixin, View):

    def get(self, request, *args, service_id=None, **kwargs):
        if not data_manager._initialized:
            return render(request, template_name='core/open_ticket.html') #todo: conditional in template for empty state

        queried = filter_ticket_request(request, data_manager.open_tickets_df, service_id)
        metadata = get_ticket_meta(data_manager.links_df, service_id)

        buffer = timedelta(days=3)

        average_sr_duration = queried.SR_DURATION_HOURS.mean()
        num_late = len(queried[queried.TICKET_DUE_DATE.apply(lambda x: x < datetime.today())])
        num_expired_soon = len(queried[queried.TICKET_DUE_DATE.apply(lambda x: x - datetime.today() < buffer)])  - num_late

        dtypes = [(col, data_manager.open_tickets_df[col].dtype.name) for col in data_manager.open_tickets_df.columns]
        searchable_columns = [i[0] for i in dtypes if i[1] == 'object']



        context = dict(
            data=queried.fillna('-').values.tolist(),
            searchable_columns=searchable_columns,
            table_headings=queried.columns.tolist(),
            average_sr_duration=average_sr_duration,
            num_late=num_late,
            num_expired_soon=num_expired_soon,
            metadata=metadata,
        )



        return render(request, template_name='core/open_ticket.html', context=context)

class UsersView(View):

    @method_decorator(staff_member_required(login_url=settings.LOGIN_URL))
    def get(self, request, *args, **kwargs):
        context = dict(
            data=process_user_data(User.objects.all()),
            table_headings=['Username', 'Position', 'AVP', 'VP', 'SVP', 'Last Login', 'Is Staff'],
            searchable_columns=['Username', 'Position', 'AVP', 'VP', 'SVP', 'Is Staff'],
        )

        return render(request, template_name='core/users.html', context=context)


class ImportDataView(View):

    def get(self, request, *args, **kwargs):
        return render(request, template_name='core/import_data.html')

    def post(self, request, *args, **kwargs):
        try:
            f = request.FILES['file']
        except KeyError:
            raise SuspiciousOperation(f'Unexpected payload: {request.FILES}')

        dfs = pd.read_excel(f, sheet_name=None)

        data_manager.load_data(dfs)

        messages.success(self.request, 'Data has been successfully uploaded. Click the site icon on the top left to view the newly uploaded data.')
        return render(request, template_name='core/import_data.html')


class ImportDataHistoryView(View):

    def get(self, request, *args, **kwargs):

        data = HistoryManager.get_data_upload_history()

        return render(request, template_name='core/import_data_history.html', context=dict(
            searchable_columns=['Uploader NIK', 'Upload time', 'Data Type'],
            table_headings=['Uploader NIK', 'Upload time', 'Data Type'],
            data=data,
        ))


class ImportUsersView(View):

    def get(self, request, *args, **kwargs):
        return render(request, template_name='core/import_users.html')

    def post(self, request, *args, **kwargs):
        try:
            f = request.FILES['file']
        except KeyError:
            raise SuspiciousOperation(f'Unexpected payload: {request.FILES}')

        dfs = pd.read_excel(f, sheet_name=None)

        user_manager.load_users(dfs)

        messages.success(self.request,
                         'Users have been successfully imported. Go to Admin > Users to view updated users.')
        return render(request, template_name='core/import_users.html')


class ImportUsersHistoryView(View):

    def get(self, request, *args, **kwargs):
        data = HistoryManager.get_user_upload_history()

        return render(request, template_name='core/import_user_history.html', context=dict(
            searchable_columns=['Uploader NIK', 'Upload time', 'Data Type'],
            table_headings=['Uploader NIK', 'Upload time', 'Data Type'],
            data=data,
        ))


class SettingsView(View):

    def get(self, request, *args):
        pass

    def post(self, request, *args):
        pass

class CustomPasswordChangeView(PasswordChangeView):
    success_url = reverse_lazy('core:change-password')

    def form_valid(self, form):
        messages.success(self.request, 'Your password has been changed.')
        return super().form_valid(form)
