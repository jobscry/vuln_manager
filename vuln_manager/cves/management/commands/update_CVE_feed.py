from django.core.management.base import BaseCommand, CommandError
from django.conf import settings
from django.utils.dateparse import parse_datetime
from cpes.models import Item
from cpes.management.commands.utils import Updater as Updater, fast_iter
from cves.models import VulnerabilityDictionary, Vulnerability

from os.path import join, normpath, isfile
from lxml import etree

import time


VULNERABILITY_SCHEMA = '{http://scap.nist.gov/schema/vulnerability/0.4}'
FEED_SCHEMA = '{http://scap.nist.gov/schema/feed/vulnerability/2.0}'
NAMESPACE_DICT = {
    'a': 'http://scap.nist.gov/schema/vulnerability/0.4',
    'b': 'http://scap.nist.gov/schema/cvss-v2/0.2'
}


class Updater(Updater):

    def __init__(self, dictionary, model):
        super(Updater, self).__init__(dictionary, model)
        self.items = {}
        self.cpes = {}
        self.count_not_updated = 0
        self.count_updated = 0
        latest = Vulnerability.objects.latest()
        self.latest = latest.published

    def save(self):
        self.model.objects.bulk_create(self.items.values())
        for key, value in self.items.iteritems():
            cve = self.model.objects.get(cve_id=value.cve_id)
            cve.cpes.add(*self.cpes[key])
        self.reset()

    def reset(self):
        self.items = {}
        self.cpes = {}
        self.count = 0

    def add_items(self, cpes, cve):
        self.items[self.count] = cve
        self.cpes[self.count] = cpes
        self.increment_count()


def get_xpath(e, p, all=True):
    if all:
        return e.xpath(p, namespaces=NAMESPACE_DICT)
    else:
        val = e.xpath(p, namespaces=NAMESPACE_DICT)
        try:
            return val[0]
        except IndexError:
            return None


def get_xpath_date(e, p):
    val = e.xpath(p, namespaces=NAMESPACE_DICT)
    try:
        return parse_datetime(val[0])
    except IndexError:
        return None


def get_refrences(references):
    for r in references:
        yield (r.text, r.get('href'))


def get_vuln_item(element, cve_id, published, modified, updater):
    return dict( 
        cve_id=element.get('id'),
        published=published,
        modified=modified,
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


def parse_cves(element, updater):
    published = published=get_xpath_date(element, 'a:published-datetime/text()')

    if published > updater.latest:

        cve_id=element.get('id')
        modified = get_xpath_date(element, 'a:last-modified-datetime/text()')

        if Vulnerability.objects.filter(cve_id=cve_id).exists():
            cve = Vulnerability.objects.get(cve_id=cve_id)
            
            if modified > cve.modified:
                cve.__dict__.update(get_vuln_item(element, cve_id, published, modified, updater))
                cve.save()
                cve.cpes.clear()
                cve.cpes.add(Item.objects.filter(
                    cpe22_wfn__in=get_xpath(element, 'a:vulnerable-software-list/a:product/text()')
                ).values_list('pk', flat=True))
                updater.count_updated += 1
            else:
                updater.count_not_updated += 1
        else:
            updater.add_items(
                Item.objects.filter(
                    cpe22_wfn__in=get_xpath(element, 'a:vulnerable-software-list/a:product/text()')
                ).values_list('pk', flat=True),
                Vulnerability(**get_vuln_item(element, cve_id, published, modified, updater))
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

        context = etree.iterparse(path, events=('end', ), tag=FEED_SCHEMA + 'entry')
        fast_iter(context, parse_cves, updater)
        updater.save()

        dictionary.num_items = updater.total_count
        dictionary.num_updated = updater.count_updated
        dictionary.num_not_updated = updater.count_not_updated
        end = float(time.time())
        dictionary.duration = end - dictionary.start
        dictionary.save()

