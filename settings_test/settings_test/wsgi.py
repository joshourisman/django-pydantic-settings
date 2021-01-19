"""
WSGI config for settings_test project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/3.1/howto/deployment/wsgi/
"""


from django.conf import settings
from django.core.wsgi import get_wsgi_application

from settings_test.settings import Settings

settings.configure(**Settings().dict())
application = get_wsgi_application()
