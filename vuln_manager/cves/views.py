from django.conf import settings
from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext
from cpes.models import Item


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
