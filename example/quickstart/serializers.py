from rest_framework import serializers
from .models import SampleData, SampleTagData


class SampleDataSerializer(serializers.HyperlinkedModelSerializer):

    class Meta:
        SampleData.objects._db = 'machbase'
        model = SampleData
        fields = ('_RID', 'value', 'label', 'date_string')


class SampleTagDataSerializer(serializers.HyperlinkedModelSerializer):

    class Meta:
        SampleTagData.objects._db = 'machbase'
        model = SampleTagData
        fields = ('name', 'time', 'value')