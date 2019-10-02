from django.contrib.auth.views import LogoutView, LoginView, PasswordChangeView
from django.urls import path, include, reverse, reverse_lazy
from core.views import DashboardView, IndexView, OpenTicketView, ClosedTicketView, UsersView, ImportView, SettingsView, \
    CustomPasswordChangeView

app_name = 'core'

urlpatterns = [
    path('', IndexView.as_view(), name='index'),
    path('dashboard', DashboardView.as_view(), name='dashboard'),
    path('dashboard/open-ticket/<str:service_id>', OpenTicketView.as_view(), name='open-ticket'),
    path('dashboard/closed-ticket/<str:service_id>', ClosedTicketView.as_view(), name='closed-ticket'),
    path('dashboard/users', UsersView.as_view(), name='admin-users'),
    path('dashboard/import', ImportView.as_view(), name='admin-import'),
    path('dashboard/change-password', CustomPasswordChangeView.as_view(), name='change-password'),
    path('login', LoginView.as_view(redirect_authenticated_user=True), name='login'),
    path('logout', LogoutView.as_view(), name='logout'),
]
