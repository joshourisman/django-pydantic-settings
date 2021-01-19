# django-pydantic-settings
## Use pydantic settings management to simplify configuration of Django settings.

Very much a work in progress, but reads the standard DJANGO_SETTINGS_MODULE environment variable (defaultingo to pydantic_settings.Settings) to load a sub-class of pydantic_settings.Settings. All settings (that have been defined in pydantic_settings.Settings) can be overridden with environment variables. A special DatabasSettings class is used to allow multiple databases to be configured simply with DSNs.

## Database configuration
By defining multiple `DjangoDsn` attributes of the `DatabaseSettings` class, you can easily configure one or more database connections with environment variables. DSNs are parsed using dj-database-url.

```python
class DatabaseSettings(BaseSettings):
    default: DjangoDsn = Field(env="DATABASE_URL")
    secondary: DjangoDsn = Field(env="SECONDARY_DATABASE_URL")
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
