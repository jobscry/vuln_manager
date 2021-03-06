from django.conf.urls import include, url
from django.contrib import admin

urlpatterns = [
    url(r'^admin/', include(admin.site.urls)),
    url(r'^cpes/', include('cpes.urls', namespace='cpes')),
    url(r'^cves/', include('cves.urls', namespace='cves')),
    url(r'^accounts/', include('registration.backends.default.urls')),
]
