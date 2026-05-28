#В файле apps.py находится вся конфигурация приложения mainapp

from django.apps import AppConfig


class MainappConfig(AppConfig):
    name = 'mainapp' #Название объекта, который будет отображать собой всё веб-приложение
