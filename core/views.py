from django.contrib.auth.views import LogoutView
from django.shortcuts import render, redirect

# Create your views here.
from django.urls import reverse
from django.views import View
from django.views.generic import TemplateView

class IndexView(TemplateView):
    def get(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect(reverse('core:dashboard'))
        else:
            return redirect(reverse('core:login'))

class DashboardView(TemplateView):
    template_name = 'core/dashboard.html'