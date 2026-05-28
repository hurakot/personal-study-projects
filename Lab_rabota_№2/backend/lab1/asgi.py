"""
ASGI config for lab1 project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/6.0/howto/deployment/asgi/
"""

#Файл asgi.py - это точка входа для ASGI-сервера.
#Файл используется при деплое проекта и для обработки HTTP-запросов сервером.

#ASGI - это более современный стандарт, чем WSGI.

import os

from django.core.asgi import get_asgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'lab1.settings')

application = get_asgi_application()
