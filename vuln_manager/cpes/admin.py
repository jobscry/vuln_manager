from django.contrib import admin
from .models import CPE, CPETitle, CPEReference, CPEDictionaryUpdate, cpe23_wfn_to_dict


class CPEAdmin(admin.ModelAdmin):
    list_display = ['part', 'cpe23_wfn', 'deprecated' ]
    list_filter = ['deprecated', 'dictionary', 'deprecation_type']

admin.site.register(CPE, CPEAdmin)


class CPEReferenceAdmin(admin.ModelAdmin):
    list_display = ['value', 'url']

admin.site.register(CPEReference, CPEReferenceAdmin)


class CPEDictionaryUpdateAdmin(admin.ModelAdmin):
    list_display = ('schema_version', 'product_version', 'generated', 'created')

admin.site.register(CPEDictionaryUpdate, CPEDictionaryUpdateAdmin)