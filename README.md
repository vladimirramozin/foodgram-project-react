# foodgram - социальная сеть для обмена рецептами.

## Описание проекта:
Учебный проект по написанию BACKEND-части на основе DRF. Функционал расскрыт через эндпоинты.
Проект развернут в трех докер-контейнерах (nginx, backend(DRF), postgresql) взаимосвязь через frontend.
Адрес проекта http://62.84.123.23 login:1@1.ru, password:QWEasd1234
## Основные эндпоинты:
Получить список всех публикаций рецептов.
```
http://localhost/api/recipes
```
Добавление новой публикации в коллекцию публикаций. Анонимные запросы запрещены.
```
http://localhost/api/recipes
```
Получение публикации по id.
```
http://localhost/api/recipes/{id}/
```

Обновление публикации по id. Обновить публикацию может только автор публикации. Анонимные запросы запрещены.
```
http://localhost/api/recipes/{id}/
```
Частичное обновление публикации по id. Обновить публикацию может только автор публикации. Анонимные запросы запрещены.
```
http://localhost/api/recipes/{id}/
```
Удаление публикации по id. Удалить публикацию может только автор публикации. Анонимные запросы запрещены.
```
http://localhost/api/recipes/{id}/
Показать пользователей. Создать пользователя.
```
http://localhost/api/users/
```
Показать профиль пользователя.
```
http://localhost/api/users/{id}/
```
Показать текущего пользователя.
```
http://localhost/api/users/me/
```
Смена пароля пользователя.
```
http://localhost/api/users/set_password/
```
Полечение токена.
```
http://localhost/api/auth/token/login/
```
Удаление токена
```
http://localhost/api/auth/token/logout/
```
Показать теги
```
http://localhost/api/tags/
```
Показать конкретный тег
```
http://localhost/api/tags/{id}/
```
Добавить рецепты в список покупок и удалить из него
```
http://localhost/api/recipes/{id}/shopping_cart/
```
Скачать список покупок
```
http://localhost/api/recipes/download_shopping_cart/
```
Добавить/удалить рецепт в избранное
```
http://localhost/api/recipes/{id}/favorite/
```
Подписаться, отписать от автора
```
http://localhost/api/users/{id}/subscribe/
```
Получить список ингредиенто
http://localhost/api/ingredients/

Получить данные о конретном ингредиенте
http://localhost/api/ingredients/{id}/

Мои подписки
http://localhost/api/users/subscriptions/
## Как запустить проект:

Клонировать репозиторий и перейти в него в командной строке:
```
git clone https://github.com/vladimirramozin/foodgram-project.git
```
Cоздать и активировать виртуальное окружение:
```
python3 -m venv env
source .venv/bin/activate
```
Установить зависимости из файла requirements.txt:
```
python3 -m pip install --upgrade pip
pip install -r requirements.txt
```

Перейти в папку infra собрать и запустить докер образ:
```
sudo docker-compose up -d --build
```

Выполнить миграции и собрать статику:
```
python3 manage.py migrate
```


## Системные требования:
Python 3.7,
Django==2.2.16,
pytest==6.2.4,
pytest-pythonpath==0.7.3,
pytest-django==4.4.0,
djangorestframework==3.12.4,
djangorestframework-simplejwt==4.7.2,
Pillow==8.3.1,
PyJWT==2.1.0,
requests==2.26.0
