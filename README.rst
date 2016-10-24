django_dvbboxes
===============

django_dvbboxes est une application Django toute simple, interfaçant dvbboxes: le gestionnaire de cluster dvbbox.

La documentation détaillée se trouve dans :file:`docs`, et `ici <http://docs.malagasy.com/django-dvbboxes/>`_.

Installation
------------

Pour installer:

1. il faut ajouter :code:`django_dvbboxes` dans :code:`INSTALLED_APPS`, comme ceci:

.. code-block:: python

   INSTALLED_APPS = [
       ...
       'django_dvbboxes',
   ]

2. inclure les URLS de :code:`django_dvbboxes` dans le fichier :code:`urls.py` de votre projet

.. code-block:: python

   url(r'^dvbboxes/', include('django_dvbboxes.urls'))

3. lancer :code:`python manage.py migrate` pour créer les migrations de modèle de l'application.
