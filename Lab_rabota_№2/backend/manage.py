#!/usr/bin/env python

#Файл manage.py - это главный файл для управления всем проектом в Django.
#Через manage.py происходит управление всем проектом (файл manage.py не нужно менять, только использовать)

#Пример используемых с manage.py команд (данные команды прописываются в терминале)

# python manage.py <команда>

# python manage.py runserver
# python manage.py migrate
# python manage.py createsuperuser

# execute_from_command_line - функция, которая выполняет команды, прописанные в терминале.

"""Django's command-line utility for administrative tasks."""
import os
import sys

#Данная функция приниает команду из терминала и выполняет её
def main():
    """Run administrative tasks."""
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'lab1.settings') # Установка настроек, прописанных в файле lab1.settings
    try:
        from django.core.management import execute_from_command_line #Попытка выполнить команду (например, runserver, migrate), записанную в терминале.
    except ImportError as exc:
        raise ImportError( #В случае ошибки в ответе в терминале выведется данное оранжевое сообщение.
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc
    execute_from_command_line(sys.argv) #Если всё хорошо, тут происходит выполнение команды с аргументами, прописанными в терминале


if __name__ == '__main__':
    main()
