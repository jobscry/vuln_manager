from django.conf.urls import url
from . import views

urlpatterns = [
    url(
        r'(?P<level>part|vendor|product)/$',
        views.index,
        name='part_index'
    ),
    url(
        r'versions/$',
        views.version_index,
        name='version_index'
    ),
    url(
        r'^$',
        views.index,
        name='index'
    )
]
