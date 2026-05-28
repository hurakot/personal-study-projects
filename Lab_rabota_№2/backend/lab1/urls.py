

#urls.py - это главный файл маршрутов в проекте. 
#В нём прописано, какой URL вызывает какой код.

from django.contrib import admin
from django.urls import path, include
from mainapp.views import BookViewSet

from rest_framework import routers
from rest_framework.routers import DefaultRouter

from mainapp.views import *

#urlpatterns - это список маршрутов (URL-путей)
#'admin/' - URL-путь, admin.site.urls - вызываемый обработчик маршрута

#Настройка REST-запросов в urls.py
router = DefaultRouter()
router.register(r'nerf', BookViewSet)

# Как работать с REST-запросами:
# Для работы с REST-запросами прописываешь строку http://127.0.0.1:8000/api/nerf/1/, где на месте цифры находится id записи. 
# Интерфейс для работы CRUD там уже реализован, так что тебе просто нужно будет запустить систему, сервер в PostgreSQL и выполнять в открытой проге все команды.
# Вся работа была выполнена с помощью фреймворка rest_framework и класса rest_framework.viewsets.ModelViewSet. Они автоматически сами и создали нужный функционал.

# При работе rest_framework:
# Метод                 ViewSet	HTTP

# list()	            GET /nerf/
# retrieve()	        GET /nerf/1/
# create()	            POST /nerf/
# update()	            PUT /nerf/1/
# partial_update()	    PATCH /nerf/1/
# destroy()	            DELETE /nerf/1/

urlpatterns = [
    path('admin/', admin.site.urls),  #Админская панель
    path('create/', create, name="create"), #Путь к созданию страницы 
    path('', watch_all, name="watch_all"), #Путь к просмотру всех страниц
    path('watch_one/<int:id>/', watch_one, name="watch_one"), #Путь к просмотру одной страницы
    path('change/<int:id>/', change, name="change"), #Путь к изменению страницы
    path('delete/<int:id>/', delete, name="delete"), #Путь к удалению страницы
    path('json/', nerf_json), #Использование сериализатора JSON

    # DRF API
    path('api/', include(router.urls)),
   
]
