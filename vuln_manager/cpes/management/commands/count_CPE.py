from django.core.management.base import BaseCommand, CommandError
from django.conf import settings
from django.utils.timezone import now
from django.utils.dateparse import parse_datetime
from cpes.models import (
    CPE, CPETitle, CPEReference, CPEDictionaryUpdate, cpe23_wfn_to_dict,
)

from os.path import join, normpath, isfile
from lxml import etree


CPE_DICT = '{http://cpe.mitre.org/dictionary/2.0}'
CPE_23 = '{http://scap.nist.gov/schema/cpe-extension/2.3}'
XML = '{http://www.w3.org/XML/1998/namespace}'
LANG = 'en-US'
MAX_ITEMS_PER_SAVE = 25


class Command(BaseCommand):
    args = '<cpe_dict_name>'
    help = 'Updates the CPE Database'

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

        parser = etree.XMLParser(ns_clean=True)
        tree = etree.parse(path, parser)

        root = tree.getroot()
        print len(root.findall(CPE_DICT + 'cpe-item'))