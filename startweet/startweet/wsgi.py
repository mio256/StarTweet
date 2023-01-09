"""
WSGI config for startweet project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/4.0/howto/deployment/wsgi/
"""

import os
from dotenv import load_dotenv
from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'startweet.settings')

application = get_wsgi_application()

load_dotenv(os.path.join('/home/mi0256/mi0256.pythonanywhere.com', '.env'))