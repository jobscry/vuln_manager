from django.conf import settings
from django.utils.dateparse import parse_datetime
from django.utils.timezone import now, make_aware
from contextlib import closing
from email.utils import formatdate, parsedate
import datetime
import requests

MAX_ITEMS = getattr(settings, 'PARSER_MAX_ITEMS', 1000)


class Updater(object):
    def __init__(self, update_obj, model, max_buffer_items=MAX_ITEMS):
        self.items = list()
        self.buffer = 0
        self.total = 0
        self.item_model = model
        self.update_obj = update_obj
        self.max_buffer_items = max_buffer_items
        self.count_fields = dict()

        for f in type(self.update_obj)._meta.get_fields(include_parents=False):
            if 'num_' in f.name:
                self.count_fields[f.name] = 0

    def add_item(self, item):
        self.items.append(item)
        self.buffer += 1
        self.total += 1
        if self.buffer >= self.max_buffer_items:
            self.save()
            self.reset()

    def increment(self, field, num=1):
        self.count_fields[field] = self.count_fields[field] + num

    def get_count(self, field):
        return self.count_fields[field]

    def reset(self):
        self.items = list()
        self.buffer = 0

    def save(self):
        self.item_model.objects.bulk_create(self.items)


def get_remote_dict(url, path, last_modified=None, etag=None, verbosity=0, stdout=None):
    if etag is not None or last_modified is not None:
        if etag is None:
            if verbosity >= 2:
                stdout.write('No etag, using date.')
            if last_modified is None:
                if verbosity >= 2:
                    stdout.write('No date, using now.')
                headers = {
                    'If-Modified-Since': formatdate(now().timestamp())
                }
            else:
                headers = {
                    'If-Modified-Since': formatdate(last_modified.timestamp())
                }
        else:
            if verbosity >= 2:
                stdout.write('Using etag.')
            headers = {'If-None-Match': etag}
    else:
        if verbosity >= 1:
            stdout.write('No etag or date, this will force file write.')
        headers = None

    with closing(requests.get(url, stream=True, headers=headers)) as res:

        if res.status_code == 200:
            if verbosity >= 2:
                stdout.write('HTTP Request status:  200')

            new_last_modified = res.headers.get('last-modified', None)
            if new_last_modified is None:
                new_last_modified = now()
            else:
                new_last_modified = datetime.datetime(
                    *parsedate(new_last_modified)[:6]
                )
                new_last_modified = make_aware(new_last_modified)

            new_etag = res.headers.get('etag', None)

            if verbosity >= 2:
                stdout.write('Writing to new file.')
                stdout.write('Path is ' + path)

            if '.gz' in path:
                if verbosity >= 2:
                    stdout.write('Writing to compressed file.')

                import zlib
                d = zlib.decompressobj(16+zlib.MAX_WBITS)
                with open(path[:-3], 'wb') as f:
                    for data in res.raw:
                        f.write(d.decompress(data))
            else:
                with open(path, 'wb') as f:
                    for data in res.iter_content(512):
                        f.write(data)

            if verbosity >= 2:
                stdout.write('Done writing.')

            return (True, new_last_modified, new_etag)

        if verbosity >= 1:
            stdout.write('HTTP Request status:  %s' % res.status_code)

        return (False, None, None)


def fast_iter(context, func, updater):
    # http://www.ibm.com/developerworks/xml/library/x-hiperfparse/
    # Author: Liza Daly
    for event, elem in context:
        func(elem, updater)
        elem.clear()
        while elem.getprevious() is not None:
            del elem.getparent()[0]
    del context
