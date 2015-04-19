from django.db import models
from django.contrib.auth.models import User
from django.contrib.postgres.fields import ArrayField
from django.utils.http import urlquote
from model_utils import Choices
from core.models import BaseDictionary


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


class Dictionary(BaseDictionary):
    """
    Dictionary model to track updates to the database.
    """
    title = models.CharField(max_length=255)
    schema_version = models.DecimalField(max_digits=4, decimal_places=2)
    product_version = models.DecimalField(max_digits=4, decimal_places=2)
    generated = models.DateTimeField()
    num_deprecated = models.PositiveIntegerField(default=0)
    num_references = models.PositiveIntegerField(default=0)
    num_existing = models.PositiveIntegerField(default=0)

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


class Watch(models.Model):
    part = models.CharField(
        max_length=1,
        choices=Item.PART_CHOICES,
        default=APPLICATIONS,
        db_index=True
    )
    vendor = models.CharField(max_length=255, db_index=True)
    product = models.CharField(max_length=255, db_index=True)
    users = models.ManyToManyField(User)
    created = models.DateTimeField(auto_now_add=True)

    @staticmethod
    def from_cpe(cpe):
        try:
            return Watch.objects.get(
                part=cpe.part,
                vendor=cpe.vendor,
                product=cpe.product,
            )
        except Watch.DoesNotExist:
            return None

    def __str__(self):
        return '[{0}:{1}:{2}:*:*:*:*:*:*:*]'.format(
            self.part,
            self.vendor,
            self.product,
        )

    class Meta:
        verbose_name_plural = 'watches'
