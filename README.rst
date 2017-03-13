django_dvbboxes
===============

django_dvbboxes is a simple django app, that interfaces `dvbboxes <https://github.com/drowolath/dvbboxes>`_


Installation
------------

To install

1. add :code:`django_dvbboxes` to your Django's project :code:`INSTALLED_APPS`, in settings.py:

.. code-block:: python

   INSTALLED_APPS = [
       ...
       'django_dvbboxes',
   ]

2. include :code:`django_dvbboxes` urls in :code:`urls.py`:

.. code-block:: python

   url(r'^dvbboxes/', include('django_dvbboxes.urls'))

3. execute :code:`python manage.py migrate` to create the app's models
