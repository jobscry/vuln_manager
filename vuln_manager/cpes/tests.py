from django.test import TestCase
from django.utils.dateparse import parse_datetime
from cpes.models import Dictionary, Item, cpe23_wfn_to_dict

FIXTURE_GENERATED_DATE = r'2015-04-04T03:50:00.174Z'
CPE_WFN = r'cpe:2.3:a:\$0.99_kindle_books_project:\$0.99_kindle_books:6:*:*:*:*:android:*:*'
CPE_KEYS = (
    'language',
    'part',
    'update',
    'product',
    'target_sw',
    'vendor',
    'other',
    'edition',
    'version',
    'sw_edition',
    'target_hw'
)
CPE_VALS = (
    '\\$0.99_kindle_books_project',
    '*',
    '\\$0.99_kindle_books',
    'android',
    'a',
    '6'
)


class CPESTestCase(TestCase):
    fixtures = ['test_cpes.json', ]

    def test_cpe23_wfn_to_dict(self):
        d = cpe23_wfn_to_dict(CPE_WFN)
        vals = set(d.keys()) & set(CPE_KEYS)
        for v in vals:
            self.assertTrue(v in CPE_KEYS)
        vals = set(d.values()) & set(CPE_VALS)
        for v in vals:
            self.assertTrue(v in CPE_VALS)
