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
