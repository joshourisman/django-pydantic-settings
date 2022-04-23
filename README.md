# django-pydantic-settings

## Use pydantic settings management to simplify configuration of Django settings.

Very much a work in progress, but reads the standard DJANGO_SETTINGS_MODULE environment variable (defaulting to pydantic_settings.settings.PydanticSettings) to load a sub-class of pydantic_settings.Settings. All settings (that have been defined in pydantic_settings.Settings) can be overridden with environment variables. A special DatabaseSettings class is used to allow multiple databases to be configured simply with DSNs.

As of django-pydantic-settings 0.6.0, Django 4.0 is now supported, but, as a result, support for Python 3.6 and 3.7 has been dropped. Python <3.8 can still be used with versions 0.5.0 and lower, and Django 3.2.x and lower; Python 3.6.0 requires django-pydantic-settings <0.4.0. Currently, django-pydantic-settings is tested on Python 3.8, 3.9, and 3.10, and Django 2.2, 3.0, 3.1, 3.2, and 4.0.

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

If your project uses a package to specify multiple different settings classes, simply set `DJANGO_SETTINGS_MODULE` to be the full path to the desired settings class. For example, given the following directory structure:

```
my_project/
├─ settings/
│  ├─ __init__.py
│  ├─ base.py
│  ├─ local.py
│  ├─ production.py
├─ my_app/

```

To use a settings class called `MyLocal` in `local.py` you would set your `DJANGO_SETTINGS_MODULE` to `my_project.settings.local.MyLocal`.

## Required settings

There are no settings that must be configured in order to use Django with django-pydantic-settings. All of the possible settings defined by Django ([Settings Reference](https://docs.djangoproject.com/en/3.1/ref/settings/)) are configured in the `pydantic_settings.settings.PydanticSettings` class, using their normal default values provided by Django, or a reasonable calculated value. Settings worth thinking about are `ROOT_URLCONF` and `WSGI_APPLICATION`, which, unless otherwise specified, are calculated based on your `DJANGO_SETTINGS_MODULE` assuming that you're using the default Django project layout a provided by `django-admin.py startproject`. So, for example, if your `DJANGO_SETINGS_MODULE` is set to `my_awesome_project.settings.PydanticSettingsSubclass`, then `ROOT_URLCONF` and `WSGI_APPLICATION` will be set to `my_awesome_project.urls` and `my_awesome_project.wsgi` respectively. This default behavior can be overridden by simply specifying `ROOT_URLCONF:str = 'the_actual_urlconf'` and `WSGI_APPLICATION:str = 'the_actual_wsgi_file.application'` in your `PydanticSettings` sub-class. Alternatively, rather than individually settings the `ROOT_URLCONF` and `WSGI_APPLICATION` settings, you can set `BASE_DIR`, and that will be used instead of `DJANGO_SETTINGS_MODULE`.

The other setting worth thinking about is `SECRET_KEY`. By default, `SECRET_KEY` is automatically generated using Django's own `get_random_secret_key()` function. This will work just fine, though as it will be re-calculated every time your `PydanticSettings` sub-class is instantiated, you should set this to somethign static if you're using Django's authentication and don't want to lose your session every time the server is restarted.

## Database configuration

By defining multiple `DatabaseDsn` attributes of the `DatabaseSettings` sub-class, you can easily configure one or more database connections with environment variables. Google Cloud SQL database connections from within Google Cloud Run are supported; the DatabaseDsn type will detect and automatically escape DSN strings of the form `postgres://username:password@/cloudsql/project:region:instance/database` so that they can be properly handled. The below example is taken from the test project in this repository, and shows a working multi-database configuration file. In this example, the value for `DJANGO_SETTINGS_MODULE` should be set, as below, to `settings_test.database_settings.TestSettings`.

```python
class Databases(DatabaseSettings):
    DEFAULT: DatabaseDsn = Field(env="DATABASE_URL")
    SECONDARY: DatabaseDsn = Field(env="SECONDARY_DATABASE_URL")


class TestSettings(PydanticSettings):
    DATABASES: Databases = Field({})
```

```python
❯ DJANGO_SETTINGS_MODULE=settings_test.database_settings.TestSettings DATABASE_URL=postgres://username:password@/cloudsql/project:region:instance/database SECONDARY_DATABASE_URL=sqlite:///foo poetry run python manage.py shell
Python 3.10.2 (main, Feb  2 2022, 06:19:27) [Clang 13.0.0 (clang-1300.0.29.3)] on darwin
Type "help", "copyright", "credits" or "license" for more information.
(InteractiveConsole)
>>> from rich import print
>>> from django.conf import settings
>>> print(settings.DATABASES)
{
    'default': {
        'NAME': 'database',
        'USER': 'username',
        'PASSWORD': 'password',
        'HOST': '/cloudsql/project:region:instance',
        'PORT': '',
        'CONN_MAX_AGE': 0,
        'ENGINE': 'django.db.backends.postgresql'
    },
    'secondary': {'NAME': 'foo', 'USER': '', 'PASSWORD': '', 'HOST': '', 'PORT': '', 'CONN_MAX_AGE': 0, 'ENGINE': 'django.db.backends.sqlite3'}
}
>>>
```

## Sentry configuration

django-pydantic-settings provides built-in functionality for configuring your Django project to use [Sentry](https://sentry.io/). The simplest way to use this is to inherit from `pydantic_settings.sentry.SentrySettings` rather than `pydantic_settings.settings.PydanticSettings`. This adds the setting `SENTRY_DSN`, which uses the `pydantic_settings.sentry.SentryDsn` type. This will automatically be set according to the `DJANGO_SENTRY_DSN` environment variable, and expects a Sentry DSN (obviously). It validates that the provided DSN is a valid URL, and then automatically initializes the Sentry SDK using the built-in DjangoIntegration. Using this functionality required `sentry-sdk` to be installed, which will be included automatically if you install `django-pydantic-settings[sentry]`.
