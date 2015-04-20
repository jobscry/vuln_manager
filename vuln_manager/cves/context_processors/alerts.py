from cpes.models import Watch
from cves.models import Alert

def new_alert_count(request):
    if request.user.is_authenticated:
        return {
            'new_alert_count': Alert.objects.filter(
                watch__pk__in=list(Watch.objects.filter(users=request.user).values_list('pk', flat=True))
            ).exclude(acks=request.user).count()
        }
    return {
        'new_alert_count': 0
    }