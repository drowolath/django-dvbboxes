from __future__ import unicode_literals

from django.db import models


class Media(models.Model):
    name = models.CharField(max_length=100, unique=True)
    filename = models.CharField(max_length=1000, unique=True)
    desc = models.TextField(max_length=100000, blank=True)

    class Meta:
        ordering = ['name']
        unique_together = (
            ('name', 'filename'),
            )
        verbose_name = 'Media'
        verbose_name_plural = 'Medias'

    def __unicode__(self):
        return self.name
