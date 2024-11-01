# **Проект Foodgram**
Foodgram
![712D8DDE-C128-47FB-BAF0-4259F688C783](https://github.com/user-attachments/assets/3007539b-6ada-49f3-8951-4c957b64b0b3)


## Описание проекта:

Foodgram — это веб-приложение для любителей кулинарии, которое позволяет пользователям делиться своими рецептами, находить вдохновение и сохранять любимые блюда в одном месте. Созданное для всех, кто хочет улучшить свои кулинарные навыки и расширить гастрономические горизонты, Foodgram предлагает интуитивно понятный интерфейс и широкий функционал.

Основные функции:

-	Регистрация и авторизация: Пользователи могут легко зарегистрироваться и создать свой профиль, чтобы сохранять рецепты и взаимодействовать с другими кулинарами.
-	Добавление рецептов: Удобный редактор позволяет пользователям создавать и публиковать свои рецепты с фотографиями, описаниями и списками ингредиентов.
-	Поиск и фильтрация: Удобные фильтры помогут пользователям находить рецепты по ингредиентам, времени приготовления и другим критериям.
-	Избранные рецепты: Возможность сохранять любимые рецепты в отдельный раздел, чтобы иметь к ним быстрый доступ.
-	Общение и взаимодействие: Пользователи могут комментировать рецепты, ставить лайки и делиться своими впечатлениями, создавая сообщество кулинаров.

Технологии:

-	Backend: Python с использованием Django REST Framework для обработки запросов и управления данными.
-	Frontend: JavaScript с использованием React для создания отзывчивого и интерактивного интерфейса.
-	База данных: PostgreSQL для хранения рецептов, пользователей и других данных.
-	Развертывание: Docker и облачные технологии для удобного развертывания и масштабирования приложения.
## Как запустить проект:

Клонировать репозиторий и перейти в него в командной строке:
```
git clone git@github.com:ovaynise/foodgram.git
```
```
cd foodgram
```
Создать .env файл зависимостей:
```
POSTGRES_USER=юзернейм_в_базе_данных
POSTGRES_PASSWORD=пароль_базы_данных
POSTGRES_DB=название_базы_данных
POSTGRES_PORT='5432'_порт
POSTGRES_HOST=хост_базы_данных
POSTGRES_HOST_ON_DOCKER=foodgramdb_хост_в_докер_контейнере(Не_менять)
DEBUG=False_отключение_и_включение_дебага
DJANGO_SECRET_KEY=секретный_ключ_джанго
MEDIA_ROOT=путь_к_сохранению_медиа_локально
MEDIA_ROOT_SERVER=путь_к_сохранению_медиа_на_сервере
SERVER_IP=ip_адресс_сервера
SERVER_DOMEN=домен_сервера
SALT=соль_для_шифрования
DOCKER_USERNAME=юзернейм_на_докер_хабе
```
Github secrets:
```
DOCKER_PASSWORD=пароль_докер_хаба
DOCKER_USERNAME=логин_докер_хаба
HOST=ip_сервера
SSH_KEY=приватный_ключ
SSH_PASSPHRASE=пароль_от_приватного_ключа
TELEGRAM_TO=ид_телеграмма_для_отправки_сообщения_деплоя
TELEGRAM_TOKENS=телеграм_токен
USER=имя_пользователя_на_сервере
```

Должен быть установлен Docker и DockerCompose.

Запустить docker-compose.yml:

```
docker compose up --build
```
Выполнить миграции:
```
docker compose -f docker-compose.yml exec backend python manage.py makemigrations
```
Создать суперпользователя:
```
docker compose -f docker-compose.yml exec backend python manage.py createsuperuser
```

Импортировать ингредиент из  csv-файлов из директории данных по команде:

```
docker compose -f docker-compose.yml exec backend python manage.py import_csv
```
Для остановки контейнеров Docker:
```
docker compose down -v      # с их удалением
docker compose stop         # без удаления

```
Автор backend'а:
Лях Евгений (c) 2024
