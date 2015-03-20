from django.db import models


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


class CPEDictionaryUpdate(models.Model):
    title = models.CharField(max_length=255)
    schema_version = models.DecimalField(max_digits=4, decimal_places=2)
    product_version = models.DecimalField(max_digits=4, decimal_places=2)
    generated = models.DateTimeField()
    notes = models.TextField(blank=True, null=True)
    start = models.DateTimeField(blank=True, null=True)
    end = models.DateTimeField(blank=True, null=True)
    created = models.DateTimeField(auto_now_add=True)

    def __unicode__(self):
        return 'Update (%s)' % self.generated 


class CPETitle(models.Model):
    lang = models.CharField(max_length=5)
    title = models.CharField(max_length=255, unique=True)


class CPEReference(models.Model):
    value = models.CharField(max_length=255)
    url = models.URLField(max_length=2000)
    dictionary = models.ForeignKey(CPEDictionaryUpdate)


def cpe23_wfn_to_dict(wfn):
    return dict(zip(WFN_KEYS, wfn.split(':')[2:]))


class CPE(models.Model):
    PART_CHOICES = (
        (APPLICATIONS, 'Applications'),
        (OPERATING_SYSTEMS, 'Operating Systems'),
        (HARDWARE, 'Hardware')
    )
    DEPRECATION_TYPE_CHOICES = (
        (NAME_CORRECTION, 'Correction'),
        (NAME_REMOVAL, 'Removal'),
        (ADDITIONAL_INFORMATION, 'Additional Information')
    )
    cpe22_wfn = models.CharField(max_length=255, unique=True, null=True, blank=True)
    cpe23_wfn = models.CharField(max_length=255, unique=True)
    title = models.CharField(max_length=255)
    references = models.ManyToManyField(CPEReference)
    deprecated = models.BooleanField(default=False)
    deprecation_date = models.DateTimeField(blank=True, null=True)
    deprecation_type = models.CharField(
        max_length=25, choices=DEPRECATION_TYPE_CHOICES, default=NAME_CORRECTION)
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
    dictionary = models.ForeignKey(CPEDictionaryUpdate)
