from django.contrib import admin
from .models import Media


class MediaAdmin(admin.ModelAdmin):
    search_fields = ('name', 'filename')

admin.site.register(Media, MediaAdmin)
