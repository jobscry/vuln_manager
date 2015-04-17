from django.core.management.base import BaseCommand
from django.conf import settings
from django.utils.timezone import now
from cpes.models import Item
from cpes.management.commands.utils import get_remote_dict, fast_iter
from cves.models import (
    VulnerabilityDictionary as Dictionary,
    Vulnerability
)
from .utils import (
    Updater,
    get_xpath,
    get_xpath_date,
    get_refrences,
    FEED_SCHEMA
)
from os.path import join
from lxml import etree

import time

FULL_CVSS_URL = getattr(
    settings,
    'FULL_CVSS_URL',
    'https://nvd.nist.gov/feeds/xml/cve/nvdcve-2.0-2015.xml.gz'
)
MODIFIED_CVSS_URL = getattr(
    settings,
    'MODIFIED_CVSS_URL',
    'https://nvd.nist.gov/feeds/xml/cve/nvdcve-2.0-Modified.xml.gz'
)


def parse_cves_full(element, updater):
    updater.add_item(
        Item.objects.filter(
            cpe22_wfn__in=get_xpath(
                element,
                'a:vulnerable-software-list/a:product/text()'
            )
        ).values_list('pk', flat=True),
        Vulnerability(
            cve_id=element.get('id'),
            published=get_xpath_date(
                element, 'a:published-datetime/text()'),
            modified=get_xpath_date(
                element, 'a:last-modified-datetime/text()'),
            cwe=get_xpath(element, 'a:cwe/@id', False),
            summary=get_xpath(element, 'a:summary/text()', False),
            references=[x for x in get_refrences(
                get_xpath(element, 'a:references/a:reference'))],
            cvss_base_score=get_xpath(
                element, 'a:cvss/b:base_metrics/b:score/text()', False),
            cvss_access_vector=get_xpath(
                element,
                'a:cvss/b:base_metrics/b:access-vector/text()',
                False
            ),
            cvss_access_complexity=get_xpath(
                element,
                'a:cvss/b:base_metrics/b:access-complexity/text()',
                False
            ),
            cvss_authentication=get_xpath(
                element,
                'a:cvss/b:base_metrics/b:authentication/text()',
                False
            ),
            cvss_confidentiality_impact=get_xpath(
                element,
                'a:cvss/b:base_metrics/b:confidentiality-impact/text()',
                False
            ),
            cvss_integrity_impact=get_xpath(
                element,
                'a:cvss/b:base_metrics/b:integrity-impact/text()',
                False
            ),
            cvss_availability_impact=get_xpath(
                element,
                'a:cvss/b:base_metrics/b:availability-impact/text()',
                False
            ),
            cvss_generated=get_xpath_date(
                element,
                'a:cvss/b:base_metrics/b:generated-on-datetime/text()'
            ),
            dictionary=updater.update_obj
        )
    )

def parse_cves_update(element, updater):
    published = get_xpath_date(element, 'a:published-datetime/text()')
    modified = get_xpath_date(element, 'a:last-modified-datetime/text()')

    if published > updater.latest or \
        (modified is not None and modified > updater.latest):

        cve_id = element.get('id')

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
                updater.increment('num_updated')
            else:
                updater.increment('num_not_updated')
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
        updater.increment('num_not_updated')


class Command(BaseCommand):
    args = '<cve_file_name>'
    help = 'Populates/Updates the CVE Database'

    def add_arguments(self, parser):
        parser.add_argument('--full',
            action='store_true',
            dest='full',
            default=False,
            help='Full database update?')

    def handle(self, *args, **options):

        self.verbosity = options.get('verbosity')

        current_date = now()
        file_path = join(
            getattr(settings, 'MEDIA_ROOT', ''),
            'data',
            'cvss-dict-%s.xml.gz' % (current_date.strftime('%Y%m%d'))
        )

        if options['full']:
            url = FULL_CVSS_URL
        else:
            url = MODIFIED_CVSS_URL

        try:
            d = Dictionary.objects.latest()
            self.stdout.write('Previous dictionary found with date: %s' % d.last_modified)
            is_created, new_created, new_etag = get_remote_dict(
                url,
                file_path,
                d.last_modified,
                d.etag or None,
                self.verbosity,
                self.stdout
            )
        except Dictionary.DoesNotExist:
            if self.verbosity >= 2:
                self.stdout.write('No previous dictionary found.')
            is_created, new_created, new_etag = get_remote_dict(
                url,
                file_path,
                None,
                None,
                self.verbosity,
                self.stdout
            )

        if is_created:
            file_path = file_path[:-3]
            update = Dictionary.objects.create(
                dictionary_file=file_path,
                start=float(time.time()),
                last_modified=new_created,
                etag=new_etag
            )
            updater = Updater(update, Vulnerability)

            if self.verbosity >= 2:
                self.stdout.write('Count fields are %s' % ', '.join(
                    updater.count_fields.keys()
                ))
                self.stdout.write('Parsing ' + file_path)

            context = etree.iterparse(
                file_path, events=('end', ), tag=FEED_SCHEMA + 'entry')

            if options['full']:
                if self.verbosity >= 2:
                    self.stdout.write('Full database populate.')    
                fast_iter(context, parse_cves_full, updater)
            else:
                if self.verbosity >= 2:
                    self.stdout.write('Database update only.')    
                fast_iter(context, parse_cves_update, cpe_updater) 

            updater.save()

            if self.verbosity >= 2:
                self.stdout.write('Done parsing.')

            update.num_updated = updater.total
            update.num_not_updated = updater.get_count('num_not_updated')
            update.duration = float(time.time()) - update.start
            update.save()
