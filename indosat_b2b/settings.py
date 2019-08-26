import os

from split_settings.tools import include

from dotenv import load_dotenv
load_dotenv()

ENVIRONMENT = os.getenv('ENVIRONMENT', 'local')
include(
    'setting_components/base.py',
    'setting_components/{}.py'.format(ENVIRONMENT).lower()
)