.. _django_dvbboxes_media:

==================================
Gestion des media: :file:`/media/`
==================================

L'application propose une vue qui s'occupe de tout ce qui est gestion des fichiers media
via les ressources suivantes

* :ref:`django_dvbboxes_media_search`

* :ref:`django_dvbboxes_media_infos`

* :ref:`django_dvbboxes_media_rename`

* :ref:`django_dvbboxes_media_delete`


.. _django_dvbboxes_media_search:

Rechercher un fichier media: :file:`/media/search`
==================================================

:code:`django-dvbboxes` propose un formulaire de recherche de fichiers à travers le cluster.
L'application utilise la propriété de recherche fournie par le module :code:`dvbboxes`.

Pour résultat, elle fait la liste de tous les fichiers correspondant à la recherche, donnant aussi
la possibilité à l'utilisateur de rechercher par filtrage l'élément désiré parmi les noms de fichiers retournés.

.. _django_dvbboxes_media_infos:

Afficher les informations d'un fichier media: :file:`/media/<filename>`
=======================================================================

Cette ressource propose une page HTML sur laquelle on trouvera les informations relatives au fichier media.

Elle affiche la durée du fichier au format hh:mm:ss, ainsi que les groupes de cluster dans lesquels il est présent (réseau, ville, etc.).

.. note::

   La notion de groupe de cluster est définie dans la documentation de :code:`dvbboxes`.
   
Elle propose aussi d'avoir un oeil sur les jours et heures de diffusion ainsi que les numéros des chaines sur lesquelles
le fichier est censé être diffusé.

La même page donne accès aux fonctions de suppression et renommage du fichier,
et ce à travers tout le cluster (aucune distinction de noeud, instance, etc.) n'est possible.

Elle donne accès à un formulaire qui permet de donner un titre et un descriptif au fichier.

.. note::

   Les titres de fichiers sont uniques du point de vue de l'application.

   Les noms de fichiers sont uniques du point de vue de l'application.

   Les paires (titre, nom de fichier) sont uniques du point de vue de l'application.


.. _django_dvbboxes_media_rename:

Renommer un fichier media: :file:`/media/rename/<filename>`
===========================================================

Cette ressource permet comme son nom l'indique de renommer un fichier.

.. note::

   Le nouveau nom précisé dans le formulaire doit contenir l'extension.

Le fichier est renommé partout où il existe dans le cluster.

.. _django_dvbboxes_media_delete:

Renommer un fichier media: :file:`/media/delete/<filename>`
===========================================================

Cette ressource permet comme son nom l'indique de supprimer un fichier.

Le fichier est supprimé partout où il existe dans le cluster.


  
    
