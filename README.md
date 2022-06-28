# Django_ORM

# 1. Requirements install
python -m pip install -r requirements.txt

# 2. Create Django Project
 - django-admin startproject mysite
 - cd ./mysite
 - python manage.py runserver
 - (서버 구동 까지 확인)

# 3. machbase_orm install
 - machbase_orm.zip 파일을 다운
 - mysite 폴더에 압축을 해제
 - setting.py 에 아래와 같이 추가
```
DATABASES = {
    'default': {
    ...
    },
    'machbase': {
        'ENGINE': 'machbase_orm',  # 다운받은 파일의 압축 해제한 폴더 이름, 또는 해당 폴더를 python에서 import를 위해 접근하기 위한 경로
        'NAME': 'MACHBASE',
        'USER': 'SYS',  # machbase connection을 위한 user ID
        'PASSWORD': 'MANAGER',  # machbase connection을 위한 user PWD
        'HOST': '127.0.0.1',  # Machbase host 주소
        'PORT': '5656',  # Machbase Connection PORT
        'HTTP_PORT': '5657',  # Machbase Rest API 호출을 할 수 있는 PORT
        'CONNTYPE': 1,  # ODBC Connect Type
        'COMPRESS': 512,  # Machbase Compress rate
        'OS': 'windows',
        'LIMIT': 100 # select 시 limit 갯수
        # machbase의 string encoding 방식이 os 마다 상이하여, machbase가 설치된 곳의 운영체제 / win 이라는 키워드가 들어있으면 windows로 인식
    }
  }
```

# 4. Model.py 설정
 - sqlite와 같은 다른 vendor의 DB의 경우 django의 migrate 기능을 활용하여, DDL을 자동으로 생성하고 실행 시켜 줄 수 있으나, Machbase의 경우 DDL이 정상적으로 수행될 수 없기 때문에, 따로 Machbase에 Table을 ORM 객체와 같은 형식으로 만들어져 있어야 한다.
 - mysite와 동일한 위치에서 django-admin startapp quickstart 입력하여 app생성
 - python manage.py migrate
 - python manage.py createsuperuser 를 입력하여, django project를 최신화 해주고, 관리자 계정을 생성
 - Model.py에 활용하고자 하는 ORM 객체 정의
 ```
 class SampleData(models.Model):
    _RID = models.AutoField(primary_key=True)
    _RID.get_placeholder = lambda *args, **kwargs: '?' # Machbase에서 query string에 대해서 나중에 값을 할당하는 string format기능에서 %s 와 같이 % 접두어를 이해하지 못하기 때문에, 모든 placeholder를 ? 로 치환하여야 하기 때문에 반드시 포함되어야 함
    value = models.FloatField()
    value.get_placeholder = lambda *args, **kwargs: '?'
    label = models.CharField(max_length=100)
    label.get_placeholder = lambda *args, **kwargs: '?'
    date_string = models.CharField(max_length=100)
    date_string.get_placeholder = lambda *args, **kwargs: '?'
    class Meta:
        db_table = "Sample" # Machbase 상의 Table 이름
 ```

# 5. serializers.py 설정
 - quickstart 폴더에 serializers.py 라는 파일를 만든다. serialize는 rest_framework에서 제공하는 CRUD를 손쉽게 활용하기 위한 Serializer 객체를 정의하는 곳이다.
 - serializers.py 파일에 아래의 객체를 생성한다.
 ```
from rest_framework import serializers
from .models import SampleData
 
class SampleDataSerializer(serializers.HyperlinkedModelSerializer):
 
    class Meta:
        SampleData.objects._db = 'machbase' # 명시적으로 machbase db 사용을 강제하기 위해서 추가된 코드
        model = SampleData
        fields = ('_RID', 'value', 'label', 'date_string')
 ```
 
# 6. view.py 설정
  - views.py파일에 아래의 코드들을 추가한다. viewset은 rest_framemwork의 기능과 http method를 연결하는 역할을 해주는 객체이다.
  ```
from django.shortcuts import render
from rest_framework import viewsets
from .serializers import SampleDataSerializer
from .models import SampleData
 
... 
 
class SampleDataViewSet(viewsets.ModelViewSet):
    queryset = SampleData.objects.using('machbase').all().order_by('_RID') # 반드시 models.py에서 정의한 ORM model 객체의 objects 필드에 using method에 'macbhase' 할당하여야 한다.
    serializer_class = SampleDataSerializer
  ```
  
# 7. urls.py 설정
 - urls.py파일을 quickstart 폴더 아래에 생성하고, 아래의 코드들을 추가한다.
 ```
from django.urls import include, path
from rest_framework import routers
from . import views
 
router = routers.DefaultRouter()
router.register(r'sample', views.SampleDataViewSet)
 
urlpatterns = [
    path('', include(router.urls))
]
 ```
 - mysite 폴더 아래에 있는 urls.py파일에 아래의 내용을 추가한다.
 ```
from django.contrib import admin
from django.urls import path, include
 
urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('quickstart.urls')),
]
 ```
# 8. 마무리
 - settings.py의 INSTALLED_APPS 필드에 'rest_framework'(추가로 사용하는 라이브러리)와 quickstart.apps.QuickstartConfig(생성한 app을 프로젝트에 등록하기 위함)를 추가한다.
 ```
 INSTALLED_APPS = [
    ...
    'quickstart.apps.QuickstartConfig',
    'rest_framework'
    ...
]
 ```
 - python manage.py makemigrations → python manage.py migarte 를 통해서 project 상태를 업데이트 한다.
 - python manage.py runserver 를 실행시켜 동작을 확인한다.
 - http://127.0.0.1:8000/sample/ 링크로 들어가 value 와 label, date string에 임의의 값을 할당하여 insert 한다.
 - machsql을 통해서 데이터가 정상적으로 입력되었는지 확인한다.

# Appendix / Bulk Insert (Append)
 - Django의 bulk_create를 이용해서 machbase에 임의의 데이터를 넣는 예제를 통해서 append를 수행하는 방식에 대해서 알아본다.
 - 이전의 quickstart app의 진행 결과를 그대로 사용하여 진행한다.
 - views.py 파일에 아래의 코드를 추가한다.
 ```
from django.http import HttpResponse
import datetime
import random
 
def insert_bulk_data(request, label):
    data = []
    start_date = datetime.datetime(2021, 11, 18, 10, 00, 00)
    time_gap = datetime.timedelta(seconds=10)
    for i in range(100):
        date_string = start_date + time_gap * i
        data.append(SampleData(label=label, value=random.random()*10, date_string=date_string.strftime('%Y-%m-%d %H:%M:%S')))
    SampleData.objects.using('machbase').bulk_create(data) # bulk insert 하는 경우 ORM 객체를 인스턴스로 만들어서 해당 리스트를 ORM의 bulk_create 메서드의 입력인자로 전해주면 된다.
    html = f"<html><body><h1>SAVE {label} </body></html>"
    return HttpResponse(html)
 ```
 - views에서 작성한 함수(controller)를 url에 route하기 위해서 quickstart의 urls.py 파일을 아래와 같이 수정한다.
 ```
  urlpatterns = [
    ...
    path('insert/<str:label>', views.insert_bulk_data),
    ...
]
 ```
 - python manage.py runserver 를 실행한 뒤, http://127.0.0.1:8000/insert/bulk_test 을 통해서 data insert를 진행한다.
 - 동일한게 machsql을 통해서 data가 정상적으로 insert 되었는지 확인한다.
 - insert 된 데이터를 ORM으로 select하여, label, time, value를 표로 반환해주는 API를 추가하여, ORM을 통해서 data select 하는 예제를 마무리한다.
 - 데이터를 시각화 하는 controller를 추가하기 위해서 views.py 파일에 아래의 코드를 추가한다.
 ```
 def get_value_table(request, label):
    value_list = SampleData.objects.using('machbase').filter(label=label)
    table_header = """
    <tr>
        <th>Label</th>
        <th>Value</th>
        <th>Date</th>
    </tr>
    """
    table_body = '\n'.join([f'<tr><td>{x.label}</td><td>{x.value}</td><td>{x.date_string}</td></tr>' for x in value_list])
    body_test = f"""
    <h1>{label} Description</h1>
    <table>
        {table_header}
        {table_body}
    </table>
    """
 
    html = f"<html><body>{body_test}</body></html>"
    return HttpResponse(html)
 ```
 - views에서 작성한 함수(controller)를 url에 route하기 위해서 quickstart의 urls.py 파일을 아래와 같이 수정한다.
 ```
 urlpatterns = [
    ...
    path('table/<str:label>', views.get_value_table),
    ...
]
 ```
 - python manage.py runserver 를 실행한 뒤, http://127.0.0.1:8000/table/bulk_test 을 통해서 결과를 확인한다.
