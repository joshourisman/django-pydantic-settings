"""
ASGI config for settings_test project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/3.1/howto/deployment/asgi/
"""

from django.conf import settings
from django.core.asgi import get_asgi_application

from settings_test.settings import Settings

settings.configure(**Settings().dict())

application = get_asgi_application()
