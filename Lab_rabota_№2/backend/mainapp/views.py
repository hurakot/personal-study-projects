

from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse, JsonResponse

# В файле views.py описана логика обработки HTTP-запросов.
# views.py содержит функции и классы, которые принимают HTTP-запрос и возвращают ответ (как HTML или JSON).

# Предположительно это главный рабочий файл, в котором ты будешь создавать основную логику приложения.

# Create your views here.

from rest_framework import viewsets
from rest_framework.viewsets import ModelViewSet
from .models import Nerf
from .serializers import ProductSerializer

#REST запросы
class BookViewSet(viewsets.ModelViewSet): # Используется класс ModelViewSet
    queryset = Nerf.objects.all()
    serializer_class = ProductSerializer

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





def nerf_json(request):
    nerfs = Nerf.objects.all()
    serializer = ProductSerializer(nerfs, many=True)
    return JsonResponse(serializer.data, safe=False)


# Создание записи
def create(request):
    if request.method == 'POST':
        Nerf.objects.create(
            title=request.POST.get('title'),
            series=request.POST.get('series'),
            bullet=request.POST.get('bullet'),
            price=request.POST.get('price'),
            time_create=request.POST.get('time_create'),
            available=bool(request.POST.get('available'))
        )
        return redirect('watch_all')
    return render(request, 'create.html')

# Просмотр всех записей
def watch_all(request):
    data = Nerf.objects.all()
    return render(request, 'list.html', {'nerfs': data})

# Просмотр определённой записи
def watch_one(request, id):
    data = get_object_or_404(Nerf, id=id)
    return render(request, 'detail.html', {'nerf': data})

# Обновление записи
def change(request, id):
    nerf = get_object_or_404(Nerf, id=id)

    if request.method == 'POST':
        nerf.title = request.POST.get('title')
        nerf.series = request.POST.get('series')
        nerf.bullet = request.POST.get('bullet')
        nerf.price = request.POST.get('price')
        nerf.time_create = request.POST.get('time_create')
        nerf.available = bool(request.POST.get('available'))
        nerf.save()

        return redirect('watch_one', id=nerf.id)

    return render(request, 'update.html', {'nerf': nerf})

# Удаление записи
def delete(request, id):
    data = get_object_or_404(Nerf, id=id)
    if request.method == 'POST':
        data.delete()
        return redirect('watch_all')
    return render(request, 'delete.html', {'nerf': data})