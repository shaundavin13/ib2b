import os


from split_settings.tools import include

ENVIRONMENT = os.getenv('ENVIRONMENT', 'local')
include(
    'setting_components/base.py',
    'setting_components/{}.py'.format(ENVIRONMENT).lower()
)