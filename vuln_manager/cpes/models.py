from django.db import models
from django.contrib.postgres.fields import ArrayField
from django.utils.http import urlquote
from model_utils import Choices


APPLICATIONS = 'a'
OPERATING_SYSTEMS = 'o'
HARDWARE = 'h'
NAME_CORRECTION = 'NAME_CORRECTION'
NAME_REMOVAL = 'NAME_REMOVAL'
ADDITIONAL_INFORMATION = 'ADDITIONAL_INFORMATION'
WFN_KEYS = [
    'part',
    'vendor',
    'product',
    'version',
    'update',
    'edition',
    'language',
    'sw_edition',
    'target_sw',
    'target_hw',
    'other'
]


class Dictionary(models.Model):
    """
    Dictionary model to track updates to the database.
    """
    title = models.CharField(max_length=255)
    dictionary_file = models.FileField(upload_to='data/cpe_dicts')
    schema_version = models.DecimalField(max_digits=4, decimal_places=2)
    product_version = models.DecimalField(max_digits=4, decimal_places=2)
    generated = models.DateTimeField()
    last_modified = models.DateTimeField(blank=True, null=True)
    etag = models.CharField(max_length=100, blank=True, null=True)
    notes = models.TextField(blank=True, null=True)
    num_items = models.PositiveIntegerField(default=0)
    num_deprecated = models.PositiveIntegerField(default=0)
    num_references = models.PositiveIntegerField(default=0)
    num_existing = models.PositiveIntegerField(default=0)
    start = models.FloatField(blank=True, null=True)
    duration = models.FloatField(blank=True, null=True)
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return 'CPE Dictionary (%s)' % self.generated

    class Meta:
        get_latest_by = 'created'
        verbose_name_plural = 'dictionaries'


def cpe23_wfn_to_dict(wfn):
    return dict(zip(WFN_KEYS, wfn.split(':')[2:]))


class Item(models.Model):
    """
    CPE Item model.
    """
    PART_CHOICES = Choices(
        (APPLICATIONS, 'Applications'),
        (OPERATING_SYSTEMS, 'Operating Systems'),
        (HARDWARE, 'Hardware')
    )
    DEPRECATION_TYPE_CHOICES = Choices(
        (NAME_CORRECTION, 'Correction'),
        (NAME_REMOVAL, 'Removal'),
        (ADDITIONAL_INFORMATION, 'Additional Information')
    )
    cpe22_wfn = models.CharField(
        max_length=255, unique=True, null=True, blank=True)
    cpe23_wfn = models.CharField(max_length=255, unique=True)
    title = models.CharField(max_length=255)
    references = ArrayField(
        models.URLField(max_length=2000), blank=True, null=True
    )
    deprecated = models.BooleanField(default=False)
    deprecation_date = models.DateTimeField(blank=True, null=True)
    deprecation_type = models.CharField(
        max_length=25,
        choices=DEPRECATION_TYPE_CHOICES,
        default=NAME_CORRECTION
    )
    deprecated_by = models.CharField(max_length=255, blank=True, null=True)
    part = models.CharField(
        max_length=1,
        choices=PART_CHOICES,
        default=APPLICATIONS,
        db_index=True
    )
    vendor = models.CharField(max_length=255, db_index=True)
    product = models.CharField(max_length=255, blank=True, null=True)
    version = models.CharField(max_length=255, blank=True, null=True)
    update = models.CharField(max_length=255, blank=True, null=True)
    edition = models.CharField(max_length=255, blank=True, null=True)
    language = models.CharField(max_length=255, blank=True, null=True)
    sw_edition = models.CharField(max_length=255, blank=True, null=True)
    target_sw = models.CharField(max_length=255, blank=True, null=True)
    target_hw = models.CharField(max_length=255, blank=True, null=True)
    other = models.CharField(max_length=255, blank=True, null=True)
    dictionary = models.ForeignKey(Dictionary)

    def url_vendor(self):
        return urlquote(self.vendor)

    def __str__(self):
        return self.cpe23_wfn
