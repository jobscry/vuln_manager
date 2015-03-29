from django.db import models
from django.contrib.postgres.fields import ArrayField
from cpes.models import Item

LOCAL = 'LOCAL'
ADJACENT_NETWORK = 'ADJACENT_NETWORK'
NETWORK = 'NETWORK'
LOW = 'LOW'
MEDIUM = 'MEDIUM'
HIGH = 'HIGH'
MULTIPLE = 'MULTIPLE'
SINGLE = 'SINGLE'
NONE = 'NONE'
PARTIAL = 'PARTIAL'
COMPLETE = 'COMPLETE'

class VulnerabilityDictionary(models.Model):
    num_items = models.PositiveIntegerField(default=0)
    num_updated = models.PositiveIntegerField(default=0)
    num_not_updated = models.PositiveIntegerField(default=0)
    start = models.FloatField()
    duration = models.FloatField(blank=True, null=True)
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = 'Vulnerability Dictionaries'


class Vulnerability(models.Model):
    ACCESS_VECTOR_CHOICES = (
        (LOCAL, 'Local'),
        (ADJACENT_NETWORK, 'Adjacent Network'),
        (NETWORK, 'Network')
    )
    ACCESS_COMPLEXITY_CHOICES = (
        (LOW, 'Low'),
        (MEDIUM, 'Medium'),
        (HIGH, 'High')
    )
    AUTHENTICATION_CHOICES = (
        (SINGLE, 'Single'),
        (MULTIPLE, 'Multiple'),
        (NONE, 'None')
    )
    IMPACT_CHOICES = (
        (NONE, 'None'),
        (PARTIAL, 'Partial'),
        (COMPLETE, 'Complete')
    )
    dictionary = models.ForeignKey(VulnerabilityDictionary)
    cpes = models.ManyToManyField(Item)
    cve_id = models.CharField(max_length=25, unique=True)
    published = models.DateTimeField()
    modified = models.DateTimeField()
    cwe = models.CharField(max_length=25, db_index=True, null=True, blank=True)
    summary = models.TextField()
    references = ArrayField(
        models.URLField(max_length=2000), blank=True, null=True
    )
    cvss_base_score = models.DecimalField(max_digits=3, decimal_places=1, null=True, blank=True)
    cvss_access_vector = models.CharField(max_length=20, choices=ACCESS_VECTOR_CHOICES, default=LOCAL, null=True, blank=True)
    cvss_access_complexity = models.CharField(max_length=20, choices=ACCESS_COMPLEXITY_CHOICES, default=LOW, null=True, blank=True)
    cvss_authentication = models.CharField(max_length=20, choices=AUTHENTICATION_CHOICES, default=NONE, null=True, blank=True)
    cvss_confidentiality_impact = models.CharField(max_length=20, choices=IMPACT_CHOICES, default=NONE, null=True, blank=True)
    cvss_integrity_impact = models.CharField(max_length=20, choices=IMPACT_CHOICES, default=NONE, null=True, blank=True)
    cvss_availability_impact = models.CharField(max_length=20, choices=IMPACT_CHOICES, default=NONE, null=True, blank=True)
    cvss_generated = models.DateTimeField(null=True, blank=True)

    def __unicode__(self):
        return self.cve_id

    class Meta:
        get_latest_by = 'published'
        verbose_name_plural = 'vulnerabilities'
