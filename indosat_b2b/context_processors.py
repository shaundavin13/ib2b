from django.conf import settings


def global_template_vars(request):

    return dict(
        app_name='Indosat Links Dashboard',
        sales_dashboard_url=settings.SALES_DASHBOARD_URL
    )