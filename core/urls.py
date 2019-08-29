from django.contrib.auth.views import LogoutView, LoginView
from django.urls import path, include, reverse
from core.views import DashboardView, IndexView

app_name = 'core'

urlpatterns = [
    path('dashboard', DashboardView.as_view(), name='dashboard'),
    path('login', LoginView.as_view(redirect_authenticated_user=True), name='login'),
    path('logout', LogoutView.as_view(), name='logout'),
    path('', IndexView.as_view(), name='index'),
]
