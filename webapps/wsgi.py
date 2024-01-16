"""
WSGI config for webapps project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/3.1/howto/deployment/wsgi/
"""

import os
import sys
import warnings
warnings.warn(f"We currently has sys.path: {sys.path}")
sys.path.insert(0, '/home/ubuntu/.local/lib/python3.10/site-packages')
sys.path = ['/home/ubuntu/.local/lib/python3.10/site-packages'] + sys.path

from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'webapps.settings')

application = get_wsgi_application()
