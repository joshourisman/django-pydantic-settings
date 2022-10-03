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

There are no settings that must be configured in order to use Django with django-pydantic-settings. All of the possible settings defined by Django ([Settings Reference](https://docs.djangoproject.com/en/3.1/ref/settings/)) are configured in the `pydantic_settings.settings.PydanticSettings` class, using their normal default values provided by Django, or a reasonable calculated value.

If you define and use a settings custom subclass, `BASE_DIR`, `ROOT_URLCONF` and `WSGI_APPLICATION` have calculated defaults relative to its base module. For example, if your `DJANGO_SETTINGS_MODULE` is set to `my_awesome_project.settings.PydanticSettingsSubclass`, then `ROOT_URLCONF` and `WSGI_APPLICATION` will be default to `my_awesome_project.urls` and `my_awesome_project.wsgi.application` respectively, and `BASE_DIR` will default to the directory that contains `my_awesome_project`. This default behavior can be overridden by simply manually specifying `ROOT_URLCONF: str = 'the_actual_urlconf'` and `WSGI_APPLICATION: str = 'the_actual_wsgi_file.application'` in your `PydanticSettings` sub-class.

The other setting worth thinking about is `SECRET_KEY`. By default, `SECRET_KEY` is automatically generated using Django's own `get_random_secret_key()` function. This will work just fine, though as it will be re-calculated every time your `PydanticSettings` sub-class is instantiated, you should set this to something static if you're using Django's authentication and don't want to lose your session every time the server is restarted.

## Database configuration

The default database configuration can be configured by an environment variable named `DATABASE_URL`, containing a DSN (Data Source Name) string.

Google Cloud SQL database connections from within Google Cloud Run are supported; the `DatabaseDsn` type will detect and automatically escape DSN strings of the form `postgres://username:password@/cloudsql/project:region:instance/database` so that they can be properly handled.

Alternatively you can set all your databases at once, by using the `DATABASES` setting (either in a `PydanticSettings` sub-class or via the `DJANGO_DATABASES` environment variable:

```python
def MySettings(PydanticSettings):
    DATABASES = {"default": "sqlite:///db.sqlite3"}  # type: ignore
```

It is also possible to configure additional database connections with environment variables in the same way as the default `DATABASE_URL` configuration by using a `Field` that has a `configure_database` argument that points to the database alias in the `DATABASES` dictionary.

```python
from pydantic_settings import PydanticSettings
from pydantic_settings.database import DatabaseDsn


def MySettings(PydanticSettings):
    secondary_database_dsn: Optional[DatabaseDsn] = Field(
        env="SECONDARY_DATABASE_URL", configure_database="secondary"
    )
```

For example, the `settings_test/database_settings.py` file is has a settings subclass configured like this and outputs the changes to the `DATABASES` setting when run directly:

```
❯ DATABASE_URL=postgres://username:password@/cloudsql/project:region:instance/database SECONDARY_DATABASE_URL=sqlite:///foo python settings_test/database_settings.py
{'default': {'ENGINE': 'django.db.backends.postgresql',
             'HOST': '/cloudsql/project:region:instance',
             'NAME': 'database',
             'PASSWORD': 'password',
             'USER': 'username'},
 'secondary': {'ENGINE': 'django.db.backends.sqlite3', 'NAME': 'foo'}}
```

## Sentry configuration

django-pydantic-settings provides built-in functionality for configuring your Django project to use [Sentry](https://sentry.io/). The simplest way to use this is to inherit from `pydantic_settings.sentry.SentrySettings` rather than `pydantic_settings.settings.PydanticSettings`. This adds the setting `SENTRY_DSN`, which uses the `pydantic_settings.sentry.SentryDsn` type. This will automatically be set according to the `DJANGO_SENTRY_DSN` environment variable, and expects a Sentry DSN (obviously). It validates that the provided DSN is a valid URL, and then automatically initializes the Sentry SDK using the built-in DjangoIntegration. Using this functionality required `sentry-sdk` to be installed, which will be included automatically if you install `django-pydantic-settings[sentry]`.
