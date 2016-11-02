.. _django_dvbboxes_listing:

===================================
Gestion du listing::file:`/listing`
===================================

:code:`django_dvbboxes` propose cette vue pour permettre d'analyser et éventuellement traiter un listing.
Elle interface complètement la classe :code:`dvbboxes.Listing` pour parvenir à celà.

Ainsi, après upload du listing, la vue va créer un résumé de ce à quoi le programme de chaque jour inscrit dans
le listing doit ressembler. Un code couleur est utilisé pour chaque jour:

* vert: tous les fichiers prévus pour ce jour existent sur au moins un noeud du cluster, le programme se termine entre minuit et 07h30 le lendemain

* rouge: au moins un fichier n'existe nulle part dans le cluster, le programme ne se termine pas entre minuit et 07h30 le lendemain

* bleu clair: au moins un fichier n'existe nulle part dans le cluster, le programme se termine entre minuit et 07h30 le lendemain

* orange: tous les fichiers prévus pour ce jour existent sur au moins un noeud du cluster, le programme ne se termine pas entre minuit et 07h30 le lendemain

Un formulaire pour appliquer le résultat est proposé en bas de page. Ce formulaire précise dans quel groupe de cluster et sur quelle chaine on doit appliquer
le listing.

Une fois l'application faite, un résultat par jour est affiché afin de faire un rapport sur l'écriture en base de données des informations.

      
