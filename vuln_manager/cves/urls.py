from django.conf.urls import url
from . import views

urlpatterns = [
    url(
        r'(?P<cpe_id>[0-9]+)/$',
        views.by_cpe,
        name='by_cpe'
    ),

]
