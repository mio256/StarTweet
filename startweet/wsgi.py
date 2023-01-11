import os
import sys
from dotenv import load_dotenv
from django.core.wsgi import get_wsgi_application

settings_path = '/home/mi0256/mi0256.pythonanywhere.com'
sys.path.insert(0, settings_path)

os.environ['DJANGO_SETTINGS_MODULE'] = 'startweet.settings'

application = get_wsgi_application()

project_folder = os.path.expanduser('~/mi0256.pythonanywhere.com')  # adjust as appropriate
load_dotenv(os.path.join(project_folder, '.env'))
