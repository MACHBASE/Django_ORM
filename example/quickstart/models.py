from django.db import models

# Create your models here.


class SampleData(models.Model):
    _RID = models.AutoField(primary_key=True)
    _RID.get_placeholder = lambda *args, **kwargs: '?'
    value = models.FloatField()
    value.get_placeholder = lambda *args, **kwargs: '?'
    label = models.CharField(max_length=100)
    label.get_placeholder = lambda *args, **kwargs: '?'
    date_string = models.CharField(max_length=100)
    date_string.get_placeholder = lambda *args, **kwargs: '?'

    class Meta:
        db_table = "Sample"


class SampleTagData(models.Model):
    # _RID = models.AutoField(primary_key=True)
    # _RID.get_placeholder = lambda *args, **kwargs: '?'
    name = models.CharField(max_length=100, primary_key=True)
    name.get_placeholder = lambda *args, **kwargs: '?'
    time = models.CharField(max_length=100)
    time.get_placeholder = lambda *args, **kwargs: '?'
    value = models.FloatField()
    value.get_placeholder = lambda *args, **kwargs: '?'

    class Meta:
        managed = False
        db_table = "TAG"