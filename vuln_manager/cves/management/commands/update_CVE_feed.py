from django.core.management.base import BaseCommand, CommandError
from django.conf import settings
from cpes.models import Item
from cpes.management.commands.utils import fast_iter
from cves.models import VulnerabilityDictionary, Vulnerability
from .utils import (
    Updater,
    get_xpath,
    get_xpath_date,
    get_vuln_item,
    FEED_SCHEMA
)

from os.path import join, normpath, isfile
from lxml import etree

import time


def parse_cves(element, updater):
    published = get_xpath_date(element, 'a:published-datetime/text()')

    if published > updater.latest:

        cve_id = element.get('id')
        modified = get_xpath_date(element, 'a:last-modified-datetime/text()')

        if Vulnerability.objects.filter(cve_id=cve_id).exists():
            cve = Vulnerability.objects.get(cve_id=cve_id)

            if modified > cve.modified:
                cve.__dict__.update(
                    get_vuln_item(
                        element,
                        cve_id,
                        published,
                        modified,
                        updater
                    )
                )
                cve.save()
                cve.cpes.clear()
                cve.cpes.add(Item.objects.filter(
                    cpe22_wfn__in=get_xpath(
                        element,
                        'a:vulnerable-software-list/a:product/text()'
                    )
                ).values_list('pk', flat=True))
                updater.count_updated += 1
            else:
                updater.count_not_updated += 1
        else:
            updater.add_items(
                Item.objects.filter(
                    cpe22_wfn__in=get_xpath(
                        element,
                        'a:vulnerable-software-list/a:product/text()'
                    )
                ).values_list('pk', flat=True),
                Vulnerability(
                    **get_vuln_item(
                        element,
                        cve_id,
                        published,
                        modified,
                        updater
                    )
                )
            )
    else:
        updater.count_not_updated += 1


class Command(BaseCommand):
    args = '<cve_file_name>'
    help = 'Updates the CVE Database'

    def handle(self, *args, **options):
        path = normpath(
            join(
                getattr(settings, 'DJANGO_ROOT'),
                'dicts',
                args[0]
            )
        )
        if not isfile(path):
            raise CommandError(
                'Dictionary does not exist: {0}'.format(
                    args[0]))

        dictionary = VulnerabilityDictionary(start=float(time.time()))
        dictionary.save()
        updater = Updater(dictionary, Vulnerability)

        context = etree.iterparse(
            path, events=('end', ), tag=FEED_SCHEMA + 'entry')
        fast_iter(context, parse_cves, updater)
        updater.save()

        dictionary.num_items = updater.total_count
        dictionary.num_updated = updater.count_updated
        dictionary.num_not_updated = updater.count_not_updated
        dictionary.duration = float(time.time()) - dictionary.start
        dictionary.save()
