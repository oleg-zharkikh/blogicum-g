Вариант 2 — Git через сетевую шару (SMB)
Если SSH — это слишком сложно, можно просто шарить папку с bare-репозиториями через обычную сетевую шару Windows.
Шаги на сервере
Создать папку C:\git_repos.
Настроить сетевую шару (Properties → Sharing).
Дать права на чтение/запись нужным пользователям.
Инициализировать bare-репозиторий как выше:
Копировать код
Powershell
cd C:\git_repos
git init --bare myproject.git
На рабочих станциях
Смонтировать шару или использовать UNC-путь:
Копировать код
Bash
git clone //SERVER_NAME/git_repos/myproject.git
или монтировать как диск:
Копировать код
Bash
net use G: \\SERVER_NAME\git_repos
git clone G:/myproject.git
⚠️ Минус: нет автоматической аутентификации Git, но для локальной сети это часто приемлемо.

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
