from django.db import models


class BaseDictionary(models.Model):
    dictionary_file = models.FileField(upload_to='data')
    last_modified = models.DateTimeField(blank=True, null=True)
    etag = models.CharField(max_length=100, blank=True, null=True)
    notes = models.TextField(blank=True, null=True)
    num_items = models.PositiveIntegerField(default=0)
    start = models.FloatField(blank=True, null=True)
    duration = models.FloatField(blank=True, null=True)
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        abstract = True
