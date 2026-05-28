"""
WSGI config for lab1 project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/6.0/howto/deployment/wsgi/
"""

#Точка входа для WSGI-сервера (например gunicorn)
#Файл используется при деплое проекта и для обработки HTTP-запросов сервером.

import os

from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'lab1.settings')

application = get_wsgi_application()
