from rest_framework import viewsets
from .serializers import SampleDataSerializer, SampleTagDataSerializer
from .models import SampleData, SampleTagData
import json
from django.http import HttpResponse
from django.views.decorators.http import require_http_methods

# Create your views here.


class SampleDataViewSet(viewsets.ModelViewSet):
    queryset = SampleData.objects.using('machbase').all().order_by('_RID')
    serializer_class = SampleDataSerializer


class SampleTagDataViewSet(viewsets.ModelViewSet):
    queryset = SampleTagData.objects.using('machbase').all().order_by('name')
    serializer_class = SampleTagDataSerializer


@require_http_methods(["POST"])
def insert_tag_data(request):
    body = request.body
    values = json.loads(body.decode('utf-8'))
    record = SampleTagData.objects.using('machbase').create(name=values['name'], time=values['time'], value=values['value'])
    return HttpResponse(content=str({'name': record.name, 'time': record.time, 'value': record.value}).encode('utf-8'))

@require_http_methods(["POST"])
def insert_bulk_data(request):
    data = []
    body = request.body
    values = json.loads(body.decode('utf-8'))['values']
    for value in values:
        data.append(SampleData(value=value[0], label=value[1], date_string=value[2]))
    SampleData.objects.using('machbase').bulk_create(data)
    return HttpResponse(content="append success".encode('utf-8'))


@require_http_methods(["POST"])
def insert_bulk_data_tag(request):
    data = []
    body = request.body
    values = json.loads(body.decode('utf-8'))['values']
    for value in values:
        data.append(SampleTagData(name=value[0], time=value[1], value=value[2]))
    SampleTagData.objects.using('machbase').bulk_create(data)
    return HttpResponse(content="append success".encode('utf-8'))


@require_http_methods(["GET"])
def select_data_label(request, label):
    data = []
    value_list = SampleData.objects.using('machbase').filter(label=label)

    return HttpResponse(json.dumps([[x.value, x.label, x.date_string] for x in value_list]).encode('utf-8'))


@require_http_methods(["GET"])
def select_tag_data_timerange(request, start, end):
    data = []
    start = start.replace('_', ' ')
    end = end.replace('_', ' ')
    value_list = SampleTagData.objects.using('machbase').filter(time__range=[start, end])

    return HttpResponse(json.dumps([[x.name, x.value, str(x.time)] for x in value_list]).encode('utf-8'))
