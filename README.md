# Проект Foodgram

* **Описание**: Foodgram - сайт, на котором пользователи могут публиковать свои рецепты, добавлять чужие рецепты в избранное и подписываться на публикации других авторов. Зарегистрированным пользователям также доступен сервис «Список покупок». Он позволяет создавать список продуктов, которые нужно купить для приготовления выбранных блюд.
* **Стек**  
  Django, Django REST Framework, Gunicorn, Nginx, PostgreSQL, Docker
* **Запуск проекта на сервере**  
    Перейдите в настройки репозитория — Settings, выберете на панели слева Secrets and Variables → Actions, нажммите New repository secret и добавьте следующие значения:
    ```
    DOCKER_PASSWORD - пароль для Docker Hub
    DOCKER_USERNAME - логин  для Docker Hub
    HOST - IP-адрес вашего сервера
    SSH_KEY - ваш закрытый SSH-ключ
    SSH_PASSPHRASE -  содержимое текстового файла с закрытым SSH-ключом
    USER - ваше имя пользователя
    TELEGRAM_TO - ID своего телеграм-аккаунта
    TELEGRAM_TOKEN - токен вашего бота
    ```
    Создайте на сервере и заполните .env (в той же директории, в которой будет находиться файл docker-compose.production.yml), который должен содержать:
    ```
    POSTGRES_USER=django_user
    POSTGRES_PASSWORD=mysecretpassword
    POSTGRES_DB=django
    DB_HOST=db
    DB_PORT=5432
    SECRET_KEY='указать SECRET_KEY'
    ALLOWED_HOSTS='указать доменное имя или IP хоста'
    ```
    Выполните команды:
    ```
    git add .
    git commit -m 'Текст коммита'
    git push
    ```
    После этого будет произведена проверка кода линтерами, сборка и деплой образа foodgram_backend на DockerHub, деплой проекта на удаленный сервер (будут выполнены миграции, собрана статика и загружены данные об ингредиентах). Вам так же придет смс в телеграм об успешном деплое.
* **Запуск проекта локально в контейнерах**   
   Создайте в рабочей директории и заполните .env , который должен содержать:
    ```
    POSTGRES_USER=django_user
    POSTGRES_PASSWORD=mysecretpassword
    POSTGRES_DB=django
    DB_HOST=db
    DB_PORT=5432
    SECRET_KEY=django-insecure-nu1&1^eo5-odq#gv^f)%mwzgqwi=#57lh9m9jz53l1*_y)x3dn
    DJANGO_DEBUG=False (если хотите включить режим отладки)
    ```
    В папке infra выполните 
    ```
    docker compose up
    ```
* **Спецификация API**  
    доступна по адресу http://localhost/api/docs/ 

* **Примеры запросов к API**  
  *Регистрация пользователя(POST)*  
    http://localhost/api/users/  
    Request
    ```
    {
    "email": "vpupkin@yandex.ru",
    "username": "vasya.pupkin",
    "first_name": "Вася",
    "last_name": "Иванов",
    "password": "Qwerty123"
    }
    ```
    Response
    ```
    {
    "email": "vpupkin@yandex.ru",
    "id": 0,
    "username": "vasya.pupkin",
    "first_name": "Вася",
    "last_name": "Иванов"
    }
    ```
    *Получение рецепта(GET)*  
    http://localhost/api/recipes/{id}/  
    Request
    ```
    {
    "id": 0,
    "tags": [
        {
        "id": 0,
        "name": "Завтрак",
        "slug": "breakfast"
        }
    ],
    "author": {
        "email": "user@example.com",
        "id": 0,
        "username": "string",
        "first_name": "Вася",
        "last_name": "Иванов",
        "is_subscribed": false,
        "avatar": "http://foodgram.example.org/media/users/image.png"
    },
    "ingredients": [
        {
        "id": 0,
        "name": "Картофель отварной",
        "measurement_unit": "г",
        "amount": 1
        }
    ],
    "is_favorited": true,
    "is_in_shopping_cart": true,
    "name": "string",
    "image": "http://foodgram.example.org/media/recipes/images/ image.png",
    "text": "string",
    "cooking_time": 1
    }
    ```
    *Удаление рецепта(DELETE)*  
    http://localhost/api/recipes/{id}/
    Response
    ```
    {
    "detail": "Учетные данные не были предоставлены."
    }
    ```
    *Добавление рецепта в избранное(POST)*  
    http://localhost/api/recipes/{id}/favorite/
    Response
    ```
    {
    "id": 0,
    "name": "string",
    "image": "http://foodgram.example.org/media/recipes/images/image.png",
    "cooking_time": 1
    }
    ```

* **Created by Ekaterina Soloveva**  
https://github.com/KatyaSoloveva

