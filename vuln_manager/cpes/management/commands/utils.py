MAX_ITEMS = 10000


class Updater(object):
    def __init__(self, dictionary, model):
        self.items = list()
        self.total_count = 0
        self.count = 0
        self.count_refs = 0
        self.count_deprecated = 0
        self.count_existing = 0
        self.dictionary = dictionary
        self.model = model

    def add_item(self, item):
        self.items.append(item)

    def increment_count(self):
        self.count += 1
        self.total_count += 1
        if self.count >= MAX_ITEMS:
            self.save()
            self.reset()

    def reset(self):
        self.items = list()
        self.count = 0

    def save(self):
        self.model.objects.bulk_create(self.items)


def fast_iter(context, func, updater):
    # http://www.ibm.com/developerworks/xml/library/x-hiperfparse/
    # Author: Liza Daly
    for event, elem in context:
        func(elem, updater)
        elem.clear()
        while elem.getprevious() is not None:
            del elem.getparent()[0]
    del context
