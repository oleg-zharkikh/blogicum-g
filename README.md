# Blogicum
Blogicum - сервис ведения личных блогов.
Учебный проект с примером реализации API-функций на основе DRF 
для просмотра и создания постов.

## Используемые технологии
[Django](https://www.djangoproject.com/),
[Django REST framework](https://www.django-rest-framework.org/)

## Руководство по локальному запуску проекта
Клонировать репозиторий и перейти в него в командной строке:

```
git clone https://github.com/oleg-zharkikh/blogicum-drf
```

```
cd blogicum-drf
```
Создать и активировать виртуальное окружение;
Windows
```
python -m venv venv
source venv/Scripts/activate
```
Linux/macOS
```
python3 -m venv venv
source venv/bin/activate
```

Обновить PIP:

Windows
```
python -m pip install --upgrade pip
```
Linux/macOS
```
python3 -m pip install --upgrade pip
```

Установить зависимости из файла requirements.txt:

```
pip install -r requirements.txt
```

Запустить проект:

Windows
```
python blogicum/manage.py runserver
```

Linux/macOS
```
python3 blogicum/manage.py runserver
```