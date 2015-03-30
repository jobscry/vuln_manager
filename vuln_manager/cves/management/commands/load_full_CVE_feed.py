from django.core.management.base import BaseCommand, CommandError
from django.conf import settings
from cpes.models import Item
from cpes.management.commands.utils import fast_iter
from cves.models import VulnerabilityDictionary, Vulnerability
from .utils import Updater, get_xpath, get_xpath_date
from os.path import join, normpath, isfile
from lxml import etree

import time



def parse_cves(element, updater):
    updater.add_items(
        Item.objects.filter(
            cpe22_wfn__in=get_xpath(element, 'a:vulnerable-software-list/a:product/text()')
        ).values_list('pk', flat=True),
        Vulnerability(
            cve_id=element.get('id'),
            published=get_xpath_date(element, 'a:published-datetime/text()'),
            modified=get_xpath_date(element, 'a:last-modified-datetime/text()'),
            cwe=get_xpath(element, 'a:cwe/@id', False),
            summary=get_xpath(element, 'a:summary/text()', False),
            references=[x for x in get_refrences(get_xpath(element, 'a:references/a:reference'))],
            cvss_base_score=get_xpath(element, 'a:cvss/b:base_metrics/b:score/text()', False),
            cvss_access_vector=get_xpath(element, 'a:cvss/b:base_metrics/b:access-vector/text()', False),
            cvss_access_complexity=get_xpath(element, 'a:cvss/b:base_metrics/b:access-complexity/text()', False),
            cvss_authentication=get_xpath(element, 'a:cvss/b:base_metrics/b:authentication/text()', False),
            cvss_confidentiality_impact=get_xpath(element, 'a:cvss/b:base_metrics/b:confidentiality-impact/text()', False),
            cvss_integrity_impact=get_xpath(element, 'a:cvss/b:base_metrics/b:integrity-impact/text()', False),
            cvss_availability_impact=get_xpath(element, 'a:cvss/b:base_metrics/b:availability-impact/text()', False),
            cvss_generated=get_xpath_date(element, 'a:cvss/b:base_metrics/b:generated-on-datetime/text()'),
            dictionary=updater.dictionary
        )
    )


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

        context = etree.iterparse(path, events=('end', ), tag=FEED_SCHEMA + 'entry')
        fast_iter(context, parse_cves, updater)
        updater.save()

        dictionary.num_items = updater.total_count
        end = float(time.time())
        dictionary.duration = end - dictionary.start
        dictionary.save()

