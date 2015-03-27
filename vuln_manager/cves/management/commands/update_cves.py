from django.core.management.base import BaseCommand, CommandError
from django.conf import settings

from os.path import join, normpath, isfile
from lxml import etree


VULNERABILITY_SCHEMA = '{http://scap.nist.gov/schema/vulnerability/0.4}'
FEED_SCHEMA = '{http://scap.nist.gov/schema/feed/vulnerability/2.0}'

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

        for event, element in etree.iterparse(path, tag=FEED_SCHEMA + 'entry'):
            for child in element:
                print child.tag
            element.clear()