from django.conf import settings
from django.utils.dateparse import parse_datetime
from django.utils.timezone import now
from cpes.management.commands.utils import Updater
from cves.models import Vulnerability

MAX_ITEMS = getattr(settings, 'PARSER_MAX_ITEMS', 1000)

VULNERABILITY_SCHEMA = '{http://scap.nist.gov/schema/vulnerability/0.4}'
FEED_SCHEMA = '{http://scap.nist.gov/schema/feed/vulnerability/2.0}'
NAMESPACE_DICT = {
    'a': 'http://scap.nist.gov/schema/vulnerability/0.4',
    'b': 'http://scap.nist.gov/schema/cvss-v2/0.2'
}


class Updater(Updater):

    def __init__(self, update_obj, model, max_buffer_items=MAX_ITEMS):
        super(Updater, self).__init__(update_obj, model, max_buffer_items)
        self.items = dict()
        self.cpes = dict()
        try:
            latest = Vulnerability.objects.latest()
            self.latest = latest.modified
        except Vulnerability.DoesNotExist:
            self.latest = now()

    def save(self):
        self.item_model.objects.bulk_create(self.items.values())
        for key, value in self.items.items():
            cve = self.item_model.objects.get(cve_id=value.cve_id)
            cve.cpes.add(*self.cpes[key])
        self.reset()

    def reset(self):
        self.items = dict()
        self.cpes = dict()
        self.buffer = 0

    def add_item(self, cpes, cve):
        self.items[self.buffer] = cve
        self.cpes[self.buffer] = cpes
        self.buffer += 1
        self.total += 1
        if self.buffer >= self.max_buffer_items:
            self.save()
            self.reset()


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
        references=[x for x in get_refrences(
            get_xpath(element, 'a:references/a:reference'))],
        cvss_base_score=get_xpath(
            element, 'a:cvss/b:base_metrics/b:score/text()', False),
        cvss_access_vector=get_xpath(
            element, 'a:cvss/b:base_metrics/b:access-vector/text()', False),
        cvss_access_complexity=get_xpath(
            element,
            'a:cvss/b:base_metrics/b:access-complexity/text()',
            False
        ),
        cvss_authentication=get_xpath(
            element, 'a:cvss/b:base_metrics/b:authentication/text()', False),
        cvss_confidentiality_impact=get_xpath(
            element,
            'a:cvss/b:base_metrics/b:confidentiality-impact/text()',
            False
        ),
        cvss_integrity_impact=get_xpath(
            element, 'a:cvss/b:base_metrics/b:integrity-impact/text()', False),
        cvss_availability_impact=get_xpath(
            element,
            'a:cvss/b:base_metrics/b:availability-impact/text()',
            False
        ),
        cvss_generated=get_xpath_date(
            element, 'a:cvss/b:base_metrics/b:generated-on-datetime/text()'),
        dictionary=updater.update_obj
    )
