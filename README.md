# [Foodgram](https://foodgram.ddnsking.com/)

## О проекте

«Фудграм» — сайт, на котором пользователи будут публиковать свои рецепты, добавлять чужие рецепты в избранное и подписываться на публикации других авторов. Зарегистрированным пользователям также будет доступен сервис «Список покупок». Он позволит создавать список продуктов, которые нужно купить для приготовления выбранных блюд.

### Основные возможности проекта
- Управление пользователями
    - Регистрация новых пользователей
    - Аутентификация по токенам (JWT)
    - Управление профилем
    - Загрузка аватара
    - Смена пароля

- Рецепты
    - Создание, просмотр, редактирование и удаление рецептов
    - Фильтрация рецептов по:
        - Тегам
        - Авторам
        - Избранному
        - Списку покупок
    - Добавление/удаление рецептов в избранное
    - Добавление/удаление рецептов в список покупок
    - Скачивание списка покупок

- Теги и ингредиенты
    - Просмотр всех тегов
    - Просмотр всех ингредиентов
    - Поиск ингредиентов по названию

- Подписки
    - Подписаться/отписаться от других пользователей
    - Просмотр своих подписок с рецептами авторов

### Особенности реализации
- Полноценное SPA-приложение с REST API
- Оптимизированные запросы к базе данных
- Автоматизированный CI/CD процесс

## Стек технологий

**Backend:**
- Python 3.9
- Django 3.2
- Django REST Framework
- PostgreSQL
- Gunicorn
- Djoser

**Frontend:**
- React 18
- Redux Toolkit
- Tailwind CSS

**Инфраструктура:**
- Docker + Docker Compose
- Nginx
- GitHub Actions (CI/CD)


### 1. Развертывание проекта

```bash
# Клонирование репозитория
git clone https://github.com/Kamilla-ElhDaou/foodgram.git

cd foodgram

# Настройка окружения

Создайте файл .env в корне проекта (на основе .env.example):

# Django
SECRET_KEY=secret_key
DEBUG=False

# PostgreSQL
POSTGRES_USER=foodgram_user
POSTGRES_PASSWORD=foodgram_password
POSTGRES_DB=foodgram
DB_HOST=foodgram
DB_PORT=5432

# Дополнительные настройки
ALLOWED_HOSTS=127.0.0.1,example.com
```

### 2. Запуск в Docker

### Сборка и запуск контейнеров
```
docker compose up -d --build
```

### Применение миграций

```
docker compose exec backend python manage.py migrate
```

### Сбор статических файлов

```
docker compose exec backend python manage.py collectstatic --no-input
```

### Наполнение приложения данными

```
docker compose exec backend python manage.py load_csv_data
docker compose exec backend python manage.py load_json_data
```
После запуска приложение будет доступно по адресу:
http://localhost:8000/

Документация доступна по адресу: http://localhost:8000/api/docs/

## CI/CD Pipeline
Процесс автоматической сборки включает:
- Сборку Docker-образов
- Деплой на production-сервер
- Отправку уведомлений в Telegram

Автор
Камилла Эль Хадж Дау
Telegram @liaklam