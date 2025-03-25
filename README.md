# URL Shortener App

## Описание

FastAPI приложение для создания, управления и использования сокращенных ссылок

## Как запустить проект

- склонировать репозиторий на локальную машину

```
git clone https://github.com/LHLHLHE/hse_applied_python_hw_3_short_links.git
```

- перейти в директорию `infra/`
- создать в `infra/` файл `.env` (пример содержимого в файле `.env.template`)
- выполнить команду (для этого нужно установить `docker` и `docker-compose`):
```
docker-compose up -d
```

Корневой адрес API: [http://127.0.0.1:8000](http://127.0.0.1:8000)

API документация: [http://127.0.0.1:8000/docs/](http://127.0.0.1:8000/docs/)

Для остановки приложения выполнить команду:
```
docker-compose down
```
Для остановки с удалением данных в БД:
```
docker-compose down -v
```

## Описание API

API предоставляет следующий функционал:
- создание короткой ссылки (в том числе кастомной)
- перенаправление на оригинальный URL по короткой ссылке
- замена оригинального URL у короткой ссылки (только для зарегистрированных пользователей)
- удаление короткой ссылки (только для зарегистрированных пользователей)
- просмотр статистики ссылки
- поиск ссылок по оригинальному URL
- просмотр истекших ссылок
- просмотр своих активных ссылок (только для зарегистрированных пользователей)

Создаваемой ссылке любой пользователь может задать время отключения, 
при наступлении которого она становится недоступной для любых действий и отображается только в списке истекших ссылок.

Неиспользуемые ссылки (в том числе истекшие) безвозвратно удаляются через `N` дней с последнего перехода. 
По умолчанию через 30 дней, но этот параметр можно настроить через переменную `UNUSED_LINKS_TTL_DAYS`.

В эндпоинтах истекших ссылок, поиска, ссылок пользователя и статистике используется кеширование, 
которое сбрасывается отдельно для каждого эндпоинта в зависимости от действия над ссылками (создание/изменение/удаление).

## Примеры запросов

**Регистрация**

`POST /users`

Request body:
```
{
    "username": "user",
    "password": "password"
}
```

**Вход:**

`POST /auth/login`

Request body:
```
{
    "username": "user",
    "password": "password"
}
```

В ответ в обоих эндпоинтах придет `Bearer` токен, который нужно передавать в заголовке запросов 
создания/обновления/удаления ссылки и просмотра своих (для создания является необязательным)

**Создание короткой ссылки:**

`POST /links/shorten?expires_at={YYYY-MM-DDTHH:MM}`

Параметр `expires_at` является опциональным.

Request body:
```
{
    "original_url": "https://example.com/1_XpbChwNfdSu0k2cBItKDfAX3YOWxU3S?usp=sharing#scrollTo=hffGnSbyAr7i",
    "custom_alias": "alias"
}
```
Поле `custom_alias` является опциональным.

Response:
```
{
    "id": 1,
    "original_url": "https://example.com/1_XpbChwNfdSu0k2cBItKDfAX3YOWxU3S?usp=sharing#scrollTo=hffGnSbyAr7i",
    "short_code": "alias",
    "short_link": "http://127.0.0.1:8000/links/alias",
    "created_at": "2025-03-25T15:23:42.439290Z",
    "redirect_count": 0,
    "last_used_at": null,
    "expires_at": "2025-03-25T15:50:00Z",
    "is_expired": false,
    "user_id": 1
}
```

**Переход по ссылке:**

`GET /links/{short_code}`

**Изменение оригинального URL короткой ссылки:**

`PUT /links/{short_code}`

Request body:
```
{
    "original_url": "https://second.example.com/1_XpbChwNfdSu0k2cBItKDfAX3YOWxU3S?usp=sharing#scrollTo=hffGnSbyAr7i"
}
```
Response:
```
{
    "id": 1,
    "original_url": "https://second.example.com/1_XpbChwNfdSu0k2cBItKDfAX3YOWxU3S?usp=sharing#scrollTo=hffGnSbyAr7i",
    "short_code": "alias",
    "short_link": "http://127.0.0.1:8000/links/alias",
    "created_at": "2025-03-25T15:23:42.439290Z",
    "redirect_count": 0,
    "last_used_at": null,
    "expires_at": "2025-03-25T15:50:00Z",
    "is_expired": false,
    "user_id": 1
}
```

**Удаление ссылки:**

`DELETE /links/{short_code}`

**Просмотр статистики по ссылке:**

`GET /links/{short_code}/stats`

Response:
```
{
    "original_url": "https://example.com/1_XpbChwNfdSu0k2cBItKDfAX3YOWxU3S?usp=sharing#scrollTo=hffGnSbyAr7i",
    "created_at": "2025-03-25T15:23:42.439290Z",
    "redirect_count": 3,
    "last_used_at": "2025-03-25T15:32:46.299644Z"
}
```

**Поиск по оригинальному URL:**

`GET /links/search?original_url={original_url}`

Response:
```
[
    {
        "id": 1,
        "original_url": "https://example.com/1_XpbChwNfdSu0k2cBItKDfAX3YOWxU3S?usp=sharing#scrollTo=hffGnSbyAr7i",
        "short_code": "alias",
        "short_link": "http://127.0.0.1:8000/links/alias",
        "created_at": "2025-03-25T15:23:42.439290Z",
        "redirect_count": 3,
        "last_used_at": "2025-03-25T15:32:46.299644Z",
        "expires_at": "2025-03-25T15:50:00Z",
        "is_expired": false,
        "user_id": 1
    }
]
```

**Просмотр своих ссылок:**

`GET /links/my`

Response:
```
[
    {
        "id": 1,
        "original_url": "https://example.com/1_XpbChwNfdSu0k2cBItKDfAX3YOWxU3S?usp=sharing#scrollTo=hffGnSbyAr7i",
        "short_code": "alias",
        "short_link": "http://127.0.0.1:8000/links/alias",
        "created_at": "2025-03-25T15:23:42.439290Z",
        "redirect_count": 3,
        "last_used_at": "2025-03-25T15:32:46.299644Z",
        "expires_at": "2025-03-25T15:50:00Z",
        "is_expired": false,
        "user_id": 1
    }
]
```

**Просмотр истекших ссылок:**

`GET /links/expired`

Response:
```
[
    {
        "id": 1,
        "original_url": "https://example.com/1_XpbChwNfdSu0k2cBItKDfAX3YOWxU3S?usp=sharing#scrollTo=hffGnSbyAr7i",
        "short_code": "alias",
        "short_link": "http://127.0.0.1:8000/links/alias",
        "created_at": "2025-03-25T15:23:42.439290Z",
        "redirect_count": 3,
        "last_used_at": "2025-03-25T15:32:46.299644Z",
        "expires_at": "2025-03-25T15:50:00Z",
        "is_expired": true,
        "user_id": 1
    }
]
```

## Описание БД

База данных состоит из двух таблиц: "links" и "users".

Таблица "links":
- id: уникальный идентификатор ссылки (первичный ключ)
- original_url: оригинальный URL
- short_code: уникальный короткий код для ссылки (с индексом для быстрого поиска)
- short_link: полная короткая ссылка
- created_at: дата и время создания ссылки (UTC)
- redirect_count: количество переходов по ссылке
- last_used_at: дата и время последнего использования ссылки (UTC), может быть null
- expires_at: дата и время истечения срока действия ссылки (UTC), может быть null
- is_expired: флаг, указывающий, истек ли срок действия ссылки
- user_id: внешний ключ, связывающий ссылку с пользователем, может быть null

Таблица "users":
- id: уникальный идентификатор пользователя (первичный ключ)
- username: уникальное имя пользователя
- password: хешированный пароль пользователя

Между таблицами существует связь "один ко многим": один пользователь может иметь множество ссылок, 
но каждая ссылка принадлежит только одному пользователю (или никому, если user_id is null).