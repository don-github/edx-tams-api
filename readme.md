# edx-tams-api

> TAMS REST Api for Open edX

WARNING: This Django application makes no sense on its own as it depends on [edx-platform](https://github.com/edx/edx-platform).

## How to install

### Register the application

Add the application to `INSTALLED_APPS` setting :

```python
INSTALLED_APPS = (
    ...
    'tams_api',
    ...
)
```

### URLs entries

Add URLs entries:

```python
urlpatterns = patterns('',
    ...
    url('^api/tams_api/', include('tams_api.urls', namespace='tams_api'))
    ...
)
```


## How to use

