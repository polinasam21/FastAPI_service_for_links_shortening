# API-сервис сокращения ссылок

## Севис

Развернутый сервис доступен по адресу: `http://:8000/`

## Установка и запуск

Склонируйте репозиторий

Выполните

```bash
docker-compose up --build
```

API будет доступно по адресу: `http://0.0.0.0:8000/`

## Реализованные эндпоинты:

1. `POST /register` - регистрация пользователя
2. `POST /token` - создание и получение токена
3. `POST /links/shorten` - создание короткой ссылки (также можно указать custom_alias и время истечения ссылки expires_at)
4. `GET /links/{short_code}` - перенаправление на оригинальный URL
5. `DELETE /links/{short_code}` - удаление короткой ссылки
6. `PUT /links/{short_code}` - обновление короткой ссылки
7. `GET /links/{short_code}/stats` - получение статистики для короткой ссылки (оригинальный URL, дата создания, количество переходов, дата последнего использования)
8. `GET /links/search/link` - поиск короткой ссылки по оригинальному URL
9. `DELETE /links/remove_unused/links` - удаление неиспользуемых ссылок
10. `GET /links/expired/links`- отображение истории всех истекших ссылок с информацией о них

## Описание базы данных

### Таблица Users
- id - первичный ключ
- username - имя пользователя
- email - адрес электронной почты
- password - пароль (используется хеширование)

### Таблица Links
- id - первичный ключ
- original_url - оригинальный адрес
- short_code - короткая ссылка
- created_at - дата и время создания короткой ссылки
- last_accessed_at - дата и время последнего использования короткой ссылки
- access_count - число обращений к короткой ссылке
- expires_at - дата и время истечения короткой ссылки

## Примеры запросов
`POST /register`

`POST /token`

`POST /links/shorten`

`DELETE /links/{short_code}`

`PUT /links/{short_code}`

`GET /links/{short_code}/stats`

`GET /links/search/link`

`DELETE /links/remove_unused/links`

`GET /links/expired/links`
