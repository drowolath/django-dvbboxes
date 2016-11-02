.. _django_dvbboxes:

===============
django-dvbboxes
===============

Application web Django, interfaçant :code:`dvbboxes`.
Elle propose une gestion simplifiée et très sobre du cluster dvbbox.

Pré-requis
==========

Pour fonctionner, django-dvbboxes a besoin de:

* python 2.7
* xmltodict >= 0.9
* dvbboxes >= 0.1
* django >= 1.10

Installation
============

Pour installer, on partira du principe que vous avez installé :code:`pip` sur votre serveur

.. code-block:: bash

   $ git clone http://gitlab.blueline.mg/default/django-dvbboxes.git -b master
   $ cd django-dvbboxes
   $ python setup.py sdist
   $ pip install dist/django-dvbboxes-x.y.tar.gz
   # si vous n'êtes pas dans un virtualenv, autant rajouter "--user" à cette dernière commande

Une fois installé, vous pouvez configurer votre projet Django qui va utiliser cette application:

1. il faut ajouter :code:`django_dvbboxes` dans :code:`INSTALLED_APPS`, comme ceci:

.. code-block:: python

   INSTALLED_APPS = [
       ...
       'django_dvbboxes',
   ]

2. inclure les URLS de :code:`django_dvbboxes` dans le fichier :code:`urls.py` de votre projet

.. code-block:: python

   url(r'', include('django_dvbboxes.urls'))  # mettez ce que vous voulez pour la regex

3. lancer :code:`python manage.py migrate` pour créer les migrations de modèle de l'application.


.. _django_dvbboxes_toc:

Documentation
=============

.. toctree::
   :maxdepth: 4
   :glob:

   *
