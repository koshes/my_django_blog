# Реализация блога на Django
### Функционал проекта:
* Публикация постов с возможностью коментирования
* Возможность пользователям делиться понравившимися постами с помощью email рассылки 
* Добавление тэгов к постам
* Рекомендация похожих постов по тэгу 
### В разработке применяется:
* [Python 3.7](https://www.python.org/downloads/release/python-379/)
* [Django 3](https://www.djangoproject.com/)
* [Docker](https://www.docker.com/)

### Установка
```bash
убедиться, что активировано виртуально окружение с python 3.7
git clone https://github.com/koshes/my_django_blog.git # копировать проект локально
pip install -r requirements.txt # установка зависимостей python
python manage.py migrate # миграция базы данных
```

### Запуск 
```
python manage.py runserver
```