from django.db import models

#В этом файле описана структура используемых БД.

class Nerf(models.Model): # Модель записи о nerf-пушке
    title = models.CharField(max_length=255) # Название пушки
    series = models.TextField(blank=False) #Серия, к которой принадлежит nerf-пушка
    bullet = models.TextField(blank=False) #Тип используемых патронов
    price = models.FloatField() # Цена nerf-пушки
    time_create = models.DateField() #Дата создания и выпуска nerf-пушки
    created_at = models.DateTimeField(auto_now=True) #Дата и время создания записи
    available = models.BooleanField(default=True) #Пушка доступна для покупки или нет?






