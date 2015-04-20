from django.conf.urls import url
from . import views

urlpatterns = [
    url(
        r'alerts/$',
        views.alerts,
        name='alerts'
    ),
    url(
        r'ack/(?P<alert_pk>[0-9]+)/$',
        views.acknowledge_alert,
        name='ack'
    ),
    url(
        r'(?P<cpe_id>[0-9]+)/$',
        views.by_cpe,
        name='by_cpe'
    )
]
