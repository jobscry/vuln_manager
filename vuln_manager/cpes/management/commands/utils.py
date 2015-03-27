from cpes.models import Item, Dictionary

MAX_ITEMS = 10000


class CPEUpdater(object):
    def __init__(self, update):
        self.items = list()
        self.total_count = 0
        self.count = 0
        self.count_refs = 0
        self.count_deprecated = 0
        self.count_existing = 0
        self.update = update

    def add_item(self, item):
        self.items.append(item)

    def add_references(self, ref):
        self.references[self.count] = ref

    def increment_count(self):
        self.count += 1
        self.total_count += 1
        if self.count >= MAX_ITEMS:
            self.save_cpes()
            self.items = list()
            self.count = 0

    def save_cpes(self):
        Item.objects.bulk_create(self.items)


def fast_iter(context, func, cpe_updater):
    # http://www.ibm.com/developerworks/xml/library/x-hiperfparse/
    # Author: Liza Daly
    for event, elem in context:
        func(elem, cpe_updater)
        elem.clear()
        while elem.getprevious() is not None:
            del elem.getparent()[0]
    del context
