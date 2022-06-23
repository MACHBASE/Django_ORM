from django.urls import include, path
from rest_framework import routers
from . import views

router = routers.DefaultRouter()
router.register(r'sample', views.SampleDataViewSet)
router.register(r'tag_sample', views.SampleTagDataViewSet)

urlpatterns = [
    path('insert', views.insert_bulk_data),
    path('insert_tag', views.insert_bulk_data_tag),
    path('tag_insert_data', views.insert_tag_data),
    path('select/<str:label>', views.select_data_label),
    path('select_tag/<str:start>/<str:end>', views.select_tag_data_timerange),
    path('', include(router.urls)),
]