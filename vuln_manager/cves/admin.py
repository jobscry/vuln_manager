from django.contrib import admin
from .models import (
    VulnerabilityDictionary,
    Vulnerability,
    Alert
)


class VulnerabilityDictionaryAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'num_items',
        'num_updated',
        'num_not_updated',
        'start',
        'duration'
    )

admin.site.register(VulnerabilityDictionary, VulnerabilityDictionaryAdmin)


class VulnerabilityAdmin(admin.ModelAdmin):
    list_display = (
        'cve_id',
        'published',
        'modified',
        'cwe',
        'cvss_base_score',
    )
    list_filter = [
        'cwe',
    ]

admin.site.register(Vulnerability, VulnerabilityAdmin)


class AlertAdmin(admin.ModelAdmin):
    list_display = (
        'watch',
        'created'
    )
    date_hierarchy = 'created'

admin.site.register(Alert, AlertAdmin)
