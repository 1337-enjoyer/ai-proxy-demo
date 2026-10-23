# AI Provider Demo

Учебный проект — мини-провайдер доступа к нейросетевым моделям через API.
Демонстрирует полный стек: FastAPI + SQLAlchemy (async) + PostgreSQL + Alembic + fastapi-users + Docker + SSE-стриминг.

## 🚀 Стек

* **Python 3.12**
* **FastAPI** — веб-фреймворк
* **SQLAlchemy 2.0 (async)** + **asyncpg** — работа с БД
* **PostgreSQL 16** — база данных (Docker)
* **Alembic** — миграции (синхронный `psycopg` для миграций, async `asyncpg` для приложения)
* **fastapi-users 15** — готовая аутентификация (JWT)
* **Pydantic v2** + **pydantic-settings** — валидация и конфиг
* **OpenAI SDK** — вызовы нейросетей (в учебных целях используется mock-сервер)
* **Docker / Docker Compose** — инфраструктура
* **Aiogram** — Telegram-боты (в планах)

## 📁 Структура проекта

```
ai-provider/
├── app/
│   ├── main.py              # Точка входа FastAPI
│   ├── core/
│   │   ├── config.py        # Pydantic Settings (.env)
│   │   └── users.py         # UserManager, JWT, current_active_user
│   ├── db/
│   │   ├── base.py          # DeclarativeBase
│   │   └── session.py       # Async engine + session factory
│   ├── models/
│   │   └── user.py          # SQLAlchemy-модель (SQLAlchemyBaseUserTableUUID)
│   ├── schemas/
│   │   └── user.py          # Pydantic-схемы (UserRead, UserCreate, UserUpdate)
│   └── api/
│       └── routes/
│           └── chat.py      # /chat/stream — SSE-стриминг от нейросети
├── alembic/                 # Миграции
├── docker-compose.yml
├── requirements.txt
├── .env.example
└── README.md
```

## ⚙️ Запуск

### 1. Клонировать и установить зависимости

```bash
git clone <repo-url>
cd ai-proxy-demo-1
python -m venv venv
source venv/Scripts/activate    # Windows (Git Bash)
pip install -r requirements.txt
```

### 2. Настроить `.env`

Скопируй `.env.example` в `.env` и заполни:

```env
DATABASE_URL=postgresql+asyncpg://provider:provider_pass@localhost:5433/ai_provider
OPENAI_API_KEY=test
OPENAI_BASE_URL=http://127.0.0.1:8011/v1
SECRET_KEY=change-me-in-prod
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

⚠️ Порт **5433** — внешний порт PostgreSQL из `docker-compose.yml` (внутри контейнера 5432).

### 3. Поднять базу

```bash
docker compose up -d db
```

### 4. Применить миграции

```bash
alembic upgrade head
```

### 5. Запустить mock-сервер нейросети (для тестов без реального API)

```bash
pip install mock-ai-api
mock-ai-api
```

Слушает `http://127.0.0.1:8011`.

### 6. Запустить приложение

```bash
uvicorn app.main:app --reload
```

Swagger: <http://127.0.0.1:8000/docs>

## 🔐 Аутентификация (fastapi-users)

| Метод | Путь                    | Описание                                        |
| :---- | :---------------------- | :---------------------------------------------- |
| POST  | `/auth/register`        | Регистрация (`email`, `password`)               |
| POST  | `/auth/jwt/login`       | Логин (form-data: `username`=email, `password`) |
| GET   | `/users/me`             | Текущий пользователь (Bearer token)             |
| POST  | `/auth/forgot-password` | Запрос сброса пароля                            |
| POST  | `/auth/reset-password`  | Сброс пароля по токену                          |
| POST  | `/auth/verify`          | Подтверждение email                             |

## 💬 Чат (провайдер нейросетей)

`POST /chat/stream` — SSE-стриминг ответа от модели.

Заголовок: `Authorization: Bearer <access_token>`

Тело:

```json
{
  "message": "Напиши короткое стихотворение про кота",
  "model": "gpt-4.1:mock-text"
}
```

Ответ — поток SSE:

```
data: кусочек
data: текста
...
data: [DONE]
```

## 🧪 Проверка через Postman

1. **Регистрация** — `POST /auth/register`, JSON `{"email": "...", "password": "..."}`
2. **Логин** — `POST /auth/jwt/login`, **x-www-form-urlencoded**: `username`=email, `password`
3. Скопировать `access_token` из ответа
4. **`GET /users/me`** — Header `Authorization: Bearer <token>`
5. **`POST /chat/stream`** — тот же заголовок, JSON с `message`

## 🐳 Docker

`docker-compose.yml` содержит два сервиса:

* `db` — PostgreSQL 16 (порт `5433:5432`)
* `api` — FastAPI (порт `8000`, монтирует `./app` для hot-reload)

## ⚠️ Известные нюансы

* **SQLAlchemy зафиксирован на 2.0.55.** Версия 2.1.x ломает `fastapi-users` с `MappedAnnotationError`. Не обновляй без проверки.
* **Alembic работает через синхронный `psycopg`**, а приложение — через асинхронный `asyncpg`. Это нормально: миграции — одноразовая операция.
* **В миграциях `fastapi-users`** может понадобиться вручную добавить `import fastapi_users_db_sqlalchemy` в шапку файла миграции (Alembic не всегда добавляет его сам).
* **Windows + asyncpg**: если ловишь `WinError 64` / `ConnectionDoesNotExistError`, проверь, что не запущен локальный PostgreSQL на 5432 (отсюда маппинг на 5433).

## 📝 TODO

* [ ] Aiogram-бот как интерфейс к `/chat/stream`
* [ ] Учёт токенов и биллинг пользователей
* [ ] Rate limiting (Redis)
* [ ] Интеграция реальных провайдеров (OpenAI, Google)
* [ ] Nginx + Dockerfile для прода
* [ ] Тесты (pytest + httpx)

## 📄 Лицензия

Учебный проект. Используй как хочешь.
