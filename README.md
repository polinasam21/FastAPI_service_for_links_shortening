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
![Снимок экрана от 2025-03-21 00-26-00](https://github.com/user-attachments/assets/01a347d1-66b9-460f-9b9d-faa61a7d8b5a)
![Снимок экрана от 2025-03-21 00-26-54](https://github.com/user-attachments/assets/56c96b93-e2a4-46d2-bc3d-673bee5fba2b)

`POST /token`
![Снимок экрана от 2025-03-21 00-27-33](https://github.com/user-attachments/assets/8949b5fe-875b-4827-ab7f-2fbd2e4d6423)
![Снимок экрана от 2025-03-21 00-28-00](https://github.com/user-attachments/assets/f994f4e9-acb9-435c-8bb7-9f2182cec1a0)

`POST /links/shorten`
![Снимок экрана от 2025-03-21 00-28-51](https://github.com/user-attachments/assets/bb61e70f-ab5d-4235-a828-ba85881184d0)
![Снимок экрана от 2025-03-21 00-29-13](https://github.com/user-attachments/assets/c7193d1e-656a-4bf2-8720-052b1f8706f6)

`GET /links/{short_code}/stats`
![Снимок экрана от 2025-03-21 00-31-00](https://github.com/user-attachments/assets/ef1c2d85-3662-4a4e-8fb7-d95d6f5a34b2)
![Снимок экрана от 2025-03-21 00-31-46](https://github.com/user-attachments/assets/9c7dc186-823a-4022-8869-aebc78e99842)

`GET /links/search/link`
![Снимок экрана от 2025-03-21 00-32-39](https://github.com/user-attachments/assets/ed07b775-3f1b-4637-bbf9-30b7b9a1af1b)

`PUT /links/{short_code}`
![Снимок экрана от 2025-03-21 00-33-42](https://github.com/user-attachments/assets/52322cb6-7853-492d-bcaf-26ac480ba313)
![Снимок экрана от 2025-03-21 00-34-05](https://github.com/user-attachments/assets/2ca98ae3-d967-446e-b931-9e8e03cf6d1c)

`DELETE /links/{short_code}`
![Снимок экрана от 2025-03-21 00-34-54](https://github.com/user-attachments/assets/671ad290-09ce-484d-99a4-b0a60e21dcb8)

`DELETE /links/remove_unused/links`
![Снимок экрана от 2025-03-21 00-36-43](https://github.com/user-attachments/assets/648771c7-955d-436d-9320-15d51096070e)

`GET /links/expired/links`
![Снимок экрана от 2025-03-21 00-49-18](https://github.com/user-attachments/assets/b7cbf44e-8541-469a-b73a-240851256d03)

