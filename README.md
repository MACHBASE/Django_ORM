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
 - mysite와 동일한 위치에서 django-admin startapp quickstart 입력하여 app생성
 - python manage.py migrate
 - python manage.py createsuperuser 를 입력하여, django project를 최신화 해주고, 관리자 계정을 생성
