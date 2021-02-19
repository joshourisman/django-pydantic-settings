# django-pydantic-settings

## Use pydantic settings management to simplify configuration of Django settings.

Very much a work in progress, but reads the standard DJANGO_SETTINGS_MODULE environment variable (defaulting to pydantic_settings.Settings) to load a sub-class of pydantic_settings.Settings. All settings (that have been defined in pydantic_settings.Settings) can be overridden with environment variables. A special DatabaseSettings class is used to allow multiple databases to be configured simply with DSNs. In theory, django-pydantic-settings should be compatible with any version of Django that runs on Python 3.6+ (which means Django 1.11 and on), but has so far only been tested against Django 3.1.

## Installation & Setup

Install django-pydantic-settings:

```
pip install django-pydantic-settings
```

Modify your Django project's `manage.py` file to use django-pydantic-settings, it should look something like this:

```python
#!/usr/bin/env python
"""Django's command-line utility for administrative tasks."""
import sys

from pydantic_settings import SetUp


def main():
    """Run administrative tasks."""
    SetUp().configure()

    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc
    execute_from_command_line(sys.argv)


if __name__ == "__main__":
    main()
```

Your `wsgi.py` and/or `asgi.py` files will need to be modified similarly, and look something like this:

```python
from django.core.wsgi import get_wsgi_application

from pydantic_settings import SetUp

SetUp().configure()
application = get_wsgi_application()
```

The `SetUp` class will automatically look for the standard `DJANGO_SETTINGS_MODULE` environment variable, read it, confirm that it points to an existing Python module, and load that module. Your `DJANGO_SETTINGS_MODULE` variable should point to a `pydantic_settings.settings.PydanticSettings` sub-class (though technically any Python class that defines a `dict()` method which returns a Python dictionary of key/value pairs matching the required Django settings will work). Calling the `configure()` method will then use the specified module to configure your project's Django settings.

## Database configuration

By defining multiple `DatabaseDsn` attributes of the `DatabaseSettings` class, you can easily configure one or more database connections with environment variables. DSNs are parsed using dj-database-url.

```python
class DatabaseSettings(BaseSettings):
    default: DatabaseDsn = Field(env="DATABASE_URL")
    secondary: DatabaseDsn = Field(env="SECONDARY_DATABASE_URL")
```

```python
❯ DATABASE_URL=sqlite:///foo SECONDARY_DATABASE_URL=sqlite:///bar ./settings_test/manage.py shell
Python 3.9.1 (default, Jan  8 2021, 17:17:43)
[Clang 12.0.0 (clang-1200.0.32.28)] on darwin
Type "help", "copyright", "credits" or "license" for more information.
(InteractiveConsole)
>>> from django.conf import settings
...
>>> pp.pprint(settings.DATABASES)
{   'default': {   'ATOMIC_REQUESTS': False,
                   'AUTOCOMMIT': True,
                   'CONN_MAX_AGE': 0,
                   'ENGINE': 'django.db.backends.sqlite3',
                   'HOST': '',
                   'NAME': 'foo',
                   'OPTIONS': {},
                   'PASSWORD': '',
                   'PORT': '',
                   'TEST': {   'CHARSET': None,
                               'COLLATION': None,
                               'MIGRATE': True,
                               'MIRROR': None,
                               'NAME': None},
                   'TIME_ZONE': None,
                   'USER': ''},
    'secondary': {   'CONN_MAX_AGE': 0,
                     'ENGINE': 'django.db.backends.sqlite3',
                     'HOST': '',
                     'NAME': 'bar',
                     'PASSWORD': '',
                     'PORT': '',
                     'USER': ''}}
>>>
```
