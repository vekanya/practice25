# Кулинарное приложение (Django + DRF + JWT)

Веб‑приложение для публикации кулинарных рецептов с изображениями, лайками/дизлайками и комментариями.  
Пользователи могут регистрироваться, авторизовываться, просматривать ленту постов, ставить реакции и комментировать записи.  
Есть возможность скачать свои данные (профиль, посты, комментарии) в формате CSV.

---

## Системные требования

- Python 3.10+
- Django 6.0
- djangorestframework 3.14.0
- djangorestframework-simplejwt 5.3.0
- База данных: SQLite (по умолчанию, файл `db.sqlite3`)

---

## Установка и запуск

### 1. Клонирование проекта

git clone <url-репозитория>
cd app



(папка `app` — корень Django‑проекта, здесь лежит `manage.py`).

### 2. Виртуальное окружение

python -m venv venv
source venv/bin/activate # Linux / macOS
venv\Scripts\activate # Windows



### 3. Установка зависимостей

pip install -r requirements.txt



### 4. Миграции

python manage.py migrate



### 5. Создание суперпользователя (опционально)

python manage.py createsuperuser



### 6. Запуск сервера разработки

python manage.py runserver



Приложение будет доступно по адресу:  
`http://127.0.0.1:8000/`

---

## Архитектура проекта

### Приложения

- `users` — кастомная модель пользователя, регистрация, логин/логаут, профиль, выгрузка данных.
- `posts` — посты (рецепты), изображения, реакции (лайк/дизлайк), комментарии.

### Основные модели

#### `users.models.User`

Наследует `AbstractUser` и добавляет:

- `phone` — номер телефона (только цифры).
- `avatar` — аватар пользователя.
- `is_online` — флаг «онлайн».
- `last_seen` — время последней активности.
- метод `update_last_seen()` — обновляет `last_seen` и `is_online`.

#### `posts.models.Post`

- `author` — внешний ключ на `User`, `related_name="posts"`.
- `text` — текст рецепта.
- `created_at` — дата создания.
- методы:
  - `preview(length=250)` — сокращённый текст.
  - `likes_count()` — количество лайков.
  - `dislikes_count()` — количество дизлайков.
  - `user_reaction(user)` — реакция конкретного пользователя: `1`, `-1` или `0`.

#### `posts.models.PostImage`

- `post` — пост, к которому относится изображение.
- `image` — файл изображения (`upload_to="posts/%Y/%m/%d/"`).

#### `posts.models.Reaction`

- `post` — пост.
- `user` — пользователь.
- `value` — `1` (лайк) или `-1` (дизлайк).  
- `unique_together = ("post", "user")` — одна реакция пользователя на пост.

#### `posts.models.Comment`

- `post` — пост.
- `author` — пользователь.
- `text` — текст комментария.
- `created_at` — дата создания.

---

## Маршрутизация

### Корневой `urls.py` (`app/urls.py`)

urlpatterns = [
path('', include('posts.urls')), # главная / лента
path('fjj38nhis135asdf/', admin.site.urls), # админка
path('users/', include('users.urls')), # auth / профиль / выгрузка
path('api/auth/', include('users.urls')), # JWT-эндпоинты из users.urls
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)



---

## URL‑маршруты и функциональность

### Приложение `posts` (`posts/urls.py`)

app_name = 'posts'

urlpatterns = [
path('', views.home_view, name='home'),
path('create/', views.create_post_view, name='create'),
path('int:pk/', views.post_detail_view, name='detail'),
path('int:pk/comment/', views.add_comment_view, name='comment'),
path('int:pk/react/', views.react_view, name='react'),
]



#### `GET /` (`posts:home`)

- Отображение ленты постов.
- Поддерживает поиск по тексту рецепта и имени автора через `?q=...`:

query = request.GET.get('q', '').strip()
if query:
posts = Post.objects.filter(
Q(text__icontains=query) |
Q(author__username__icontains=query)
)...



- В шаблон `posts/home.html` передаются:
- `posts` — список постов с автором, изображениями, комментариями, реакциями.
- `query` — текущая строка поиска.

#### `GET /create/` и `POST /create/` (`posts:create`)

- Страница создания поста.
- Обрабатывает:
- текст из `request.POST['text']`;
- изображения из `request.FILES.getlist('images')`.
- Создаёт `Post` и связанные `PostImage`, затем редирект на `posts:home`.

#### `GET /<pk>/` (`posts:detail`)

- Детальная страница поста.
- Загружает пост с автором, изображениями и комментариями.
- Шаблон `posts/post.html`.

#### `POST /<pk>/comment/` (`posts:comment`)

- Добавление комментария к посту.
- Используется `CommentForm`.
- После успешного добавления редирект на `posts:home`.

#### `POST /<pk>/react/` (`posts:react`)

- Обработка лайка/дизлайка через AJAX.
- Принимает `value=like` или `value=dislike`.
- Логика:
- если реакции ещё нет — создаёт;
- если реакция совпадает — удаляет (снять лайк/дизлайк);
- если реакция другая — обновляет.
- Возвращает JSON:

{
"likes": <кол-во лайков>,
"dislikes": <кол-во дизлайков>,
"user_reaction": 1 | -1 | 0
}



На фронте (в JS) эти данные используются для обновления иконок и счётчиков.

---

### Приложение `users` (`users/urls.py`)

app_name = "users"

urlpatterns = [
path("register/", views.register_view, name="register"),
path("login/", views.login_view, name="login"),
path("logout/", views.logout_view, name="logout"),
path("profile/", views.profile_view, name="profile"),
path("token/", TokenObtainPairView.as_view(), name="token_obtain_pair"),
path("token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
path("download-data/", views.download_user_data, name="download_data"),
]



#### `GET /users/register/` и `POST /users/register/` (`users:register`)

- Регистрация нового пользователя через `RegisterForm`.
- После успешной регистрации выполняется вход (`login`) и редирект на `posts:home`.

#### `GET /users/login/` и `POST /users/login/` (`users:login`)

- Вход через `LoginForm`.
- При успешном логине:
  - пользователь помечается как `is_online = True`;
  - редирект на `users:profile`.

#### `GET /users/logout/` (`users:logout`)

- Выход пользователя:
  - `is_online = False`;
  - `logout(request)`;
  - редирект на страницу логина.

#### `GET /users/profile/` (`users:profile`)

- Профиль пользователя.
- Если есть `?user=<id>`, открывается профиль другого пользователя, иначе — текущего.
- Если `POST` и профиль свой — обновление аватара через `AvatarUpdateForm`.
- Обновляет `last_seen` и `is_online` через `update_last_seen()`.

#### `GET /users/download-data/` (`users:download_data`)

- Только для авторизованных.
- Отдаёт CSV с личными данными пользователя:
  - username, email, phone;
  - количество постов и комментариев;
  - список постов (id, текст, дата создания);
  - список комментариев (id поста, текст, дата создания).

#### JWT‑эндпоинты

- `POST /api/auth/token/` (`users:token_obtain_pair`)  
  Возвращает `access` и `refresh` токены.
- `POST /api/auth/token/refresh/` (`users:token_refresh`)  
  Принимает `refresh` и возвращает новый `access`.

---

## Статические файлы и шаблоны

- Каталог шаблонов: `BASE_DIR / 'templates'` + `APP_DIRS=True`.
- Основные шаблоны:
  - `posts/home.html` — главная лента.
  - `posts/create_post.html` — создание поста.
  - `posts/post.html` — отдельный пост.
  - `users/auth.html` — логин.
  - `users/reg.html` — регистрация.
  - `users/profile.html` — профиль.

- Статика:

STATIC_URL = 'static/'
STATICFILES_DIRS = [BASE_DIR / 'static']
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'



- Основные директории:
  - `static/css/style.css` — стили.
  - `static/js/script.js` — JS логика (лайки, комментарии, поиск, слайдер, раскрытие текста).
  - `media/avatars/` — аватары.
  - `media/posts/...` — изображения постов.

---

## Как описывать изменения

Если будешь добавлять новые эндпоинты или страницы (например, API для списка пользователей), просто добавь раздел в README:

- название URL;
- HTTP‑метод;
- параметры запроса;
- формат ответа.

---