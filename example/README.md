# Django_ORM
기본적으로 연결 하고자 하는 Machbase에 다음의 Table들을 생성한다
```
create table Sample (value double, label varchar(100), date_string varchar(100));
create tagdata table Tag(name varchar(100) primary key, time datetime basetime, value double summarized);
```

# Requirements install
python -m pip install -r requirements.txt

# Django db create
python manage.py migrate

# Django start
python manage.py runserver

http://127.0.0.1:8000 주소에 들어갔을때 Api Root라는 title의 페이지가 정상적으로 나타나야 한다.
