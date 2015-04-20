from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.shortcuts import render_to_response, get_object_or_404, redirect
from django.template import RequestContext
from cpes.models import Item, Watch
from .models import Alert


PER_PAGE = getattr(settings, 'MAX_PER_PAGE', 100)


def by_cpe(request, cpe_id):
    cpe = get_object_or_404(Item, pk=cpe_id)
    objects = cpe.vulnerability_set.all()

    return render_to_response(
        'cves/index.html',
        RequestContext(
            request,
            {
                'cpe': cpe,
                'objects': objects,
                'q_dict': {
                    'part': cpe.part,
                    'vendor': cpe.vendor,
                    'product': cpe.product,
                    'version': cpe.version
                }
            }
        )
    )


@login_required
def alerts(request):
    watch_pks = list(
        Watch.objects.filter(users=request.user).values_list('pk', flat=True)
    )
    alerts = Alert.objects.select_related(
        'vulnerability', 'watch').filter(watch__pk__in=watch_pks)
    acks = list(alerts.filter(acks=request.user).values_list('pk', flat=True))

    return render_to_response(
        'cves/alerts_index.html',
        RequestContext(
            request,
            {
                'alerts': alerts,
                'acks': acks
            }
        )
    )


@login_required
def acknowledge_alert(request, alert_pk):
    alert = get_object_or_404(Alert, pk=alert_pk)
    alert.acks.add(request.user)
    messages.success(request, 'Alert acknowledged.')
    return redirect(
        reverse('cves:alerts')
    )
