from django.conf.urls import url
from . import views

app_name = 'django_dvbboxes'

urlpatterns = [
    # views.media urls
    url(r'media/search/$', views.media, name='media_search'),
    url(r'media/delete/(?P<filename>\w+)/$',
        views.media,
        name='media_delete'),
    url(r'media/delete/$',
        views.media,
        name='media_delete_batch'),
    url(r'media/rename/(?P<filename>\w+)/$',
        views.media,
        name='media_rename'),
    url(r'media/(?P<filename>\w+)/$',
        views.media,
        name='media_infos'),
    # views.listing urls
    url(r'listing/apply/$',
        views.listing,
        name='applylisting'),
    url(r'listing/$', views.listing, name='listing'),
    # views.program urls
    url(r'program/$', views.program, name='program'),
    url(r'program/xmltv/(?P<filename>\w+)/$', views.program, name='xmltv'),
    url(r'^$', views.index, name='index'),
    ]
