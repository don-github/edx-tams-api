# edx-accounts-api

> Accounts REST Api for Open edX

WARNING: This Django application makes no sense on its own as it depends on [edx-platform](https://github.com/edx/edx-platform).

## How to install

### Register the application

Add the application to `INSTALLED_APPS` setting :

```python
INSTALLED_APPS = (
    ...
    'accounts_api',
    ...
)
```

### URLs entries

Add URLs entries:

```python
urlpatterns = patterns('',
    ...
    url('^api/accounts_api/', include('accounts_api.urls', namespace='accounts_api'))
    ...
)
```


## How to use

