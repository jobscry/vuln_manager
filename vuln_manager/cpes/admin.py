from django.contrib import admin
from .models import Item, Dictionary, Watch


class ItemAdmin(admin.ModelAdmin):
    list_display = [
        'part',
        'cpe23_wfn',
        'deprecated'
    ]
    list_filter = ['deprecated', 'dictionary', 'deprecation_type']

admin.site.register(Item, ItemAdmin)


class DictionaryAdmin(admin.ModelAdmin):
    list_display = (
        'schema_version',
        'product_version',
        'generated',
        'num_items',
        'num_deprecated',
        'num_references',
        'num_existing',
        'duration',
        'created'
    )

admin.site.register(Dictionary, DictionaryAdmin)


class WatchAdmin(admin.ModelAdmin):
    list_display = (
        'part',
        'vendor',
        'product',
    )
    list_filter = [
        'part',
        'vendor',
        'product',
    ]

admin.site.register(Watch, WatchAdmin)
