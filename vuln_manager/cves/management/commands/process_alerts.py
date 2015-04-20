from django.core.management.base import BaseCommand
from django.db import IntegrityError
from cpes.models import Item, Watch
from cves.models import (
    VulnerabilityDictionary as Dictionary,
    Vulnerability,
    Alert
)

class Command(BaseCommand):
    args = '<force>'
    help = 'Populates/Updates the CVE Database'

    def add_arguments(self, parser):
        parser.add_argument(
            '--force',
            action='store_true',
            dest='force',
            default=False,
            help='Force reprocessing of alerts.')

    def handle(self, *args, **options):

        self.verbosity = options.get('verbosity')
        self.force = options.get('force')

        self.stdout.write('Force is {0}'.format(self.force))

        try:
            if self.force:
                d = Dictionary.objects.latest()
            else:    
                d = Dictionary.objects.filter(processed_alerts=False).latest()

            if self.verbosity >= 3:
                self.stdout.write('Found unprocessed dictionary created on {0}'.format(d.created))
                self.stdout.write('There are {0} vulnerabilities.'.format(d.vulnerability_set.count()))

            created = 0
            for v in d.vulnerability_set.all():
                cpes = []
                for c in v.cpes.all():
                    w = Watch.from_cpe(c)
                    if w is not None:
                        val = '{0}'.format(w)
                        if self.verbosity >= 2:
                            self.stdout.write('Found watch {0}'.format(val))
                        if val not in cpes:
                            if self.verbosity >= 2:
                                self.stdout.write('Watch not found in existing CPE list, trying to create alert.')
                            cpes.append(val)
                            try:
                                Alert.objects.create(
                                    watch=w,
                                    vulnerability=v
                                )
                                created += 1
                            except IntegrityError:
                                if self.verbosity >= 1:
                                    self.stdout.write('Hit existing alert.')

            if self.verbosity >= 2:
                self.stdout.write('Created {0} alerts.'.format(created))

            d.processed_alerts = True
            d.save()

        except Dictionary.DoesNotExist:
            if self.verbosity >= 1:
                self.stdout.write('No unprocessed dictionaries found.')
