from django.core.management.base import BaseCommand, CommandError
from django.conf import settings
from django.utils.timezone import now
from django.utils.dateparse import parse_datetime
from cpes.models import (
    CPE, CPETitle, CPEReference, CPEDictionaryUpdate, cpe23_wfn_to_dict,
)

from os.path import join, normpath, isfile
from lxml import etree


def fixtag(tag):
    vals = tag.split('}')
    return vals[0][1:], vals[1]

CPE_DICT = '{http://cpe.mitre.org/dictionary/2.0}'
CPE_23 = '{http://scap.nist.gov/schema/cpe-extension/2.3}'
XML = '{http://www.w3.org/XML/1998/namespace}'
LANG = 'en-US'

def get_references(item, ref_count, update):
    references = item.find(CPE_DICT + 'references')
    if references is not None:
        old_ref_count = ref_count
        refs = []
        ref_list = references.findall(CPE_DICT + 'reference')
        for ref in references:
            refs.append(
                CPEReference(
                    value=ref.text,
                    url=ref.get('href'),
                    dictionary=update
                )
            )
            ref_count += 1
        if ref_count > old_ref_count:
            return refs, ref_count
    return None, None


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

        generator = root.find(CPE_DICT + 'generator')
        update = CPEDictionaryUpdate(start=now())
        update.title = generator.find(CPE_DICT + 'product_name').text
        update.product_version = generator.find(CPE_DICT + 'product_version').text
        update.schema_version = generator.find(CPE_DICT + 'schema_version').text
        update.generated = parse_datetime(generator.find(CPE_DICT + 'timestamp').text)
        update.started = now()
        update.save()
        notes = []

        count, deprecated_count, references_count, existing_count = 0, 0, 0, 0
        all_items = {}
        all_references = {}
        for item in root.iterchildren(CPE_DICT + 'cpe-item'):
            new_title = 'No Title'
            for title in item.findall(CPE_DICT + 'title'):
                if title.get(XML + 'lang') == LANG:
                    new_title = title.text

            cpe23 = item.find(CPE_23 + 'cpe23-item')

            cpe23_wfn = cpe23.get('name')

            if item.get('deprecated'):
                defaults = cpe23_wfn_to_dict(cpe23.get('name'))
                defaults['dictionary'] = update
                defaults['title'] = new_title
                existing_item, created = CPE.objects.get_or_create(
                    cpe23_wfn=cpe23_wfn,
                    defaults=defaults
                )
                if created:
                    deprecation = cpe23.find(CPE_23 + 'deprecation')
                    deprecated_by = deprecation.find(CPE_23 + 'deprecated-by')
                    existing_item.deprecated = True
                    existing_item.deprecated_by = deprecated_by.get('name')
                    existing_item.deprecation_type = deprecated_by.get('type')
                    existing_item.deprecation_date = parse_datetime(deprecation.get('date'))
                    existing_item.save()

                deprecated_count += 1
            else:
                if not CPE.objects.filter(cpe23_wfn=cpe23_wfn).exists():
                    new_item = CPE(**cpe23_wfn_to_dict(cpe23.get('name')))
                    new_item.title = new_title
                    new_item.dictionary = update
                    new_item.cpe23_wfn = cpe23_wfn

                    references, new_count = get_references(item, references_count, update)
                    if references is not None:
                        all_references[count] = references
                        references_count = new_count

                    all_items[count] = new_item
                    count += 1
                else:
                    existing_count += 1

        CPE.objects.bulk_create(all_items.values())
        for x in all_references.keys():
            pks = []
            for ref in all_references[x]:
                ref.save()
                pks.append(ref.pk)
            item = CPE.objects.get(cpe23_wfn=all_items[x].cpe23_wfn)
            item.references.add(*pks)

        notes.append('found {0} items'.format(count))
        notes.append('found {0} deprecated items'.format(deprecated_count))
        notes.append('found {0} references'.format(references_count))
        notes.append('found {0} existing'.format(existing_count))
        update.notes = '\n'.join(notes)
        update.end = now()
        update.save()