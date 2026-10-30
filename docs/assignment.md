# Лабораторная работа № 3  
## Backend с REST API и базой данных

В предыдущих лабораторных работах вы создали клиентскую часть веб-приложения: страницы, оформление, интерактивность и работу с данными в браузере. Теперь приложение нужно разделить на две части: **frontend** будет получать данные через HTTP-запросы, а **backend** будет хранить данные в базе данных и предоставлять к ним доступ через REST API.

Эта лабораторная работа — переход от статического сайта к полноценному клиент-серверному приложению. Сейчас важно не добавить как можно больше функций, а правильно выделить сущности предметной области, спроектировать понятный API и связать frontend, backend и базу данных.

## Цель работы

Научиться:

- выделять сущности и отношения между ними на основе существующего сайта;
- проектировать REST API для CRUD-операций;
- создавать backend на Python;
- хранить данные в реляционной базе данных;
- обращаться к базе данных из backend-приложения;
- автоматически генерировать и использовать OpenAPI-спецификацию;
- получать данные на frontend через REST API.

## Что нужно сделать

Выделите в своем проекте основные сущности и реализуйте для них backend с REST API.

Например:

| Тема проекта | Основная сущность | Примеры связанных данных |
|---|---|---|
| Сайт с видеоиграми | Игра | Жанр, платформа, разработчик |
| Трекер чтения новелл | Новелла | Глава, автор, статус чтения |
| Кулинарная книга | Рецепт | Ингредиент, категория, шаг приготовления |
| Каталог компьютерных компонентов | Компонент | Категория, производитель, характеристики |
| Складской учёт | Товар | Категория, поставщик, операция поступления |
| Игра «Сломанный телефон» | Сообщение | Игрок, раунд, вариант ответа |
| Персонализированные заметки | Заметка | Категория, тег, пользователь |
| Афиша мероприятий | Мероприятие | Категория, место проведения, участник |
| Сайт с попутчиками | Поездка | Водитель, пассажир, маршрут |
| Квесты в браузере | Квест | Комната, предмет, действие игрока |
| Каталог вакансий | Вакансия | Компания, категория, отклик |
| Справочник грибов, собак или котов | Запись справочника | Категория, характеристика, изображение |
| Аналог Дрома | Объявление | Марка, модель, пользователь |
| Каталог настолок | Настольная игра | Жанр, количество игроков, издатель |
| Каталог автозапчастей | Запчасть | Марка автомобиля, категория, производитель |
| Магазин чая | Товар | Категория, производитель, заказ |
| Brawl Stars | Персонаж | Режим, редкость, характеристика |
| Панель статистики компьютера | Метрика | Устройство, тип метрики, значение |
| Сервис фото + ИИ | Фото | Пользователь, результат обработки |
| Личный дневник или заметки | Запись | Категория, тег, дата |
| Дневник репетитора | Ученик | Занятие, предмет, расписание |

Не обязательно реализовывать все возможные сущности проекта. Для этой работы достаточно выбрать **одну основную сущность** и при необходимости **одну связанную сущность**.

Например, для кулинарной книги основной сущностью может быть `Recipe`, а связанной — `Category`. Для каталога вакансий основной сущностью может быть `Vacancy`, а связанной — `Company`.

## Минимальный состав API

Для основной сущности необходимо реализовать полный набор CRUD-операций:

| Метод | Путь | Назначение |
|---|---|---|
| `GET` | `/api/<entities>` | Получить список записей |
| `POST` | `/api/<entities>` | Создать новую запись |
| `GET` | `/api/<entities>/{id}` | Получить одну запись по идентификатору |
| `PUT` или `PATCH` | `/api/<entities>/{id}` | Обновить запись |
| `DELETE` | `/api/<entities>/{id}` | Удалить запись |

Здесь `<entities>` — имя коллекции во множественном числе, например:

```text
GET    /api/games
POST   /api/games
GET    /api/games/1
PATCH  /api/games/1
DELETE /api/games/1
```

Для кулинарной книги:

```text
GET    /api/recipes
POST   /api/recipes
GET    /api/recipes/12
PATCH  /api/recipes/12
DELETE /api/recipes/12
```

Для каталога вакансий:

```text
GET    /api/vacancies
POST   /api/vacancies
GET    /api/vacancies/7
PUT    /api/vacancies/7
DELETE /api/vacancies/7
```

## Пример: сайт с видеоиграми

Допустим, разрабатывается сайт с видеоиграми. Основная сущность — игра.

### Поля сущности

| Поле | Тип | Описание |
|---|---|---|
| `id` | integer | Уникальный идентификатор |
| `title` | string | Название игры |
| `description` | string | Краткое описание |
| `genre` | string | Жанр |
| `platform` | string | Платформа |
| `release_year` | integer | Год выпуска |
| `rating` | number | Рейтинг |
| `image_url` | string | Ссылка на изображение |
| `created_at` | datetime | Дата добавления |

### Пример объекта

```json
{
  "id": 1,
  "title": "Hollow Knight",
  "description": "Атмосферный метроидвания про путешествие по подземному королевству.",
  "genre": "Metroidvania",
  "platform": "PC",
  "release_year": 2017,
  "rating": 9.2,
  "image_url": "/images/hollow-knight.jpg",
  "created_at": "2026-10-24T10:00:00Z"
}
```

### Примеры запросов

Создание игры:

```http
POST /api/games HTTP/1.1
Content-Type: application/json

{
  "title": "Hollow Knight",
  "description": "Атмосферный метроидвания про путешествие по подземному королевству.",
  "genre": "Metroidvania",
  "platform": "PC",
  "release_year": 2017,
  "rating": 9.2,
  "image_url": "/images/hollow-knight.jpg"
}
```

Ответ сервера:

```http
HTTP/1.1 201 Created
Content-Type: application/json

{
  "id": 1,
  "title": "Hollow Knight",
  "description": "Атмосферный метроидвания про путешествие по подземному королевству.",
  "genre": "Metroidvania",
  "platform": "PC",
  "release_year": 2017,
  "rating": 9.2,
  "image_url": "/images/hollow-knight.jpg",
  "created_at": "2026-10-24T10:00:00Z"
}
```

Получение списка игр:

```http
GET /api/games HTTP/1.1
```

Получение одной игры:

```http
GET /api/games/1 HTTP/1.1
```

Частичное обновление игры:

```http
PATCH /api/games/1 HTTP/1.1
Content-Type: application/json

{
  "rating": 9.5
}
```

Удаление игры:

```http
DELETE /api/games/1 HTTP/1.1
```

## Требования к REST API

API должен быть предсказуемым и использовать корректные HTTP-методы.

### Правила проектирования

- Пути должны обозначать ресурсы, а не действия: `/api/games`, а не `/api/getGames`.
- Имена коллекций должны быть во множественном числе: `/api/recipes`, `/api/vacancies`, `/api/games`.
- Идентификатор конкретной записи передаётся в пути: `/api/games/1`.
- Для чтения используется `GET`.
- Для создания используется `POST`.
- Для полного обновления можно использовать `PUT`.
- Для частичного обновления рекомендуется использовать `PATCH`.
- Для удаления используется `DELETE`.
- Backend не должен доверять данным клиента без проверки: обязательные поля, типы, длину строк и допустимые значения нужно валидировать.

### Коды ответов

Минимально необходимо использовать следующие HTTP-статусы:

| Статус | Когда используется |
|---|---|
| `200 OK` | Успешное чтение или обновление |
| `201 Created` | Успешное создание записи |
| `204 No Content` | Успешное удаление записи |
| `400 Bad Request` | Некорректный запрос или данные |
| `404 Not Found` | Запись не найдена |
| `422 Unprocessable Content` | Данные не прошли валидацию |
| `500 Internal Server Error` | Внутренняя ошибка сервера |

Например, если пользователь запрашивает несуществующую игру:

```http
GET /api/games/999 HTTP/1.1
```

Сервер должен вернуть:

```http
HTTP/1.1 404 Not Found
```

Если при создании рецепта не передано обязательное название:

```http
POST /api/recipes HTTP/1.1
Content-Type: application/json

{
  "description": "Суп без названия"
}
```

Сервер должен вернуть ошибку валидации, например:

```http
HTTP/1.1 422 Unprocessable Content
Content-Type: application/json

{
  "detail": [
    {
      "loc": ["body", "title"],
      "msg": "Field required",
      "type": "missing"
    }
  ]
}
```

## Требования к базе данных

Данные должны храниться в базе данных, а не в массиве JavaScript, JSON-файле или переменной backend-приложения.

Рекомендуется использовать реляционную базу данных:

- PostgreSQL — предпочтительный вариант;
- MySQL — допустимый вариант;
- SQLite — допустимо для простой локальной разработки

### Минимальные требования

Необходимо:

- создать таблицу для основной сущности;
- определить первичный ключ `id`;
- задать подходящие типы данных для полей;
- использовать ограничения `NOT NULL` там, где поле обязательно;
- использовать `UNIQUE`, если значение должно быть уникальным;
- использовать `CHECK`, если значение должно соответствовать правилу;
- при наличии связанной сущности использовать внешний ключ `FOREIGN KEY`.

### Пример таблицы для игр

```sql
CREATE TABLE games (
    id SERIAL PRIMARY KEY,
    title VARCHAR(200) NOT NULL,
    description TEXT,
    genre VARCHAR(100) NOT NULL,
    platform VARCHAR(100) NOT NULL,
    release_year INTEGER CHECK (release_year BETWEEN 1950 AND 2100),
    rating NUMERIC(3, 1) CHECK (rating >= 0 AND rating <= 10),
    image_url VARCHAR(500),
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
```

### Пример таблицы для рецептов

```sql
CREATE TABLE categories (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL UNIQUE
);

CREATE TABLE recipes (
    id SERIAL PRIMARY KEY,
    title VARCHAR(200) NOT NULL,
    description TEXT,
    cooking_time_minutes INTEGER CHECK (cooking_time_minutes > 0),
    servings INTEGER CHECK (servings > 0),
    category_id INTEGER NOT NULL REFERENCES categories(id),
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
```

В этом примере связь между рецептами и категориями реализована через внешний ключ `category_id`.

## Требования к OpenAPI

Backend должен автоматически генерировать OpenAPI-спецификацию.

Если используется FastAPI, спецификация обычно доступна по адресам:

```text
/docs
/redoc
/openapi.json
```

В спецификации должны быть описаны:

- все REST-методы;
- пути запросов;
- параметры пути;
- тела запросов;
- возможные ответы;
- коды ответов;
- схемы данных;
- примеры запросов и ответов.

### Что должно быть в `/docs`

Нужно уметь объяснить по Swagger UI:

- какие методы доступны для каждой сущности;
- какие поля нужно передать при создании записи;
- какие поля возвращает сервер;
- какие ошибки возможны;
- как выполнить запрос напрямую из интерфейса документации;
- как выглядит сгенерированная OpenAPI-спецификация в формате JSON.

### Пример описания операции

Для метода создания игры в OpenAPI должны быть указаны:

- метод `POST`;
- путь `/api/games`;
- тело запроса;
- схема ответа `201 Created`;
- возможный ответ `422 Unprocessable Content`.

Пример фрагмента спецификации:

```yaml
paths:
  /api/games:
    post:
      summary: Создать игру
      operationId: create_game
      requestBody:
        required: true
        content:
          application/json:
            schema:
              $ref: '#/components/schemas/GameCreate'
      responses:
        '201':
          description: Игра создана
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/Game'
        '422':
          description: Ошибка валидации
```

## Требования к frontend

Существующий сайт должен получать данные с backend через REST API.

Минимально необходимо реализовать:

- загрузку списка записей с сервера;
- отображение полученных данных в карточках;
- создание новой записи через форму;
- обновление хотя бы одного поля записи;
- удаление записи.

Например, для каталога игр:

- при открытии страницы frontend отправляет `GET /api/games`;
- полученные игры отображаются в карточках;
- форма «Добавить игру» отправляет `POST /api/games`;
- кнопка «Изменить рейтинг» отправляет `PATCH /api/games/{id}`;
- кнопка «Удалить» отправляет `DELETE /api/games/{id}`.

### Пример запроса из JavaScript

```javascript
async function loadGames() {
  const response = await fetch("/api/games");

  if (!response.ok) {
    throw new Error(`Ошибка загрузки: ${response.status}`);
  }

  const games = await response.json();
  renderGames(games);
}
```

### Пример создания записи

```javascript
async function createGame(gameData) {
  const response = await fetch("/api/games", {
    method: "POST",
    headers: {
      "Content-Type": "application/json"
    },
    body: JSON.stringify(gameData)
  });

  if (!response.ok) {
    throw new Error(`Ошибка создания: ${response.status}`);
  }

  return await response.json();
}
```

### Пример удаления записи

```javascript
async function deleteGame(id) {
  const response = await fetch(`/api/games/${id}`, {
    method: "DELETE"
  });

  if (response.status !== 204) {
    throw new Error(`Ошибка удаления: ${response.status}`);
  }
}
```

## Рекомендуемый стек

Для выполнения работы рекомендуется следующий стек:

| Часть приложения | Технология |
|---|---|
| Backend | Python |
| Веб-фреймворк | FastAPI |
| База данных | PostgreSQL |
| Работа с БД | SQLAlchemy |
| Frontend | HTML, CSS, JavaScript |
| Документация API | Swagger UI / OpenAPI |

FastAPI выбран как рекомендуемый вариант, потому что он автоматически генерирует OpenAPI-документацию и удобно работает с Pydantic-схемами. Использование другого Python-фреймворка, например Django REST Framework или Flask.

## Рекомендуемая структура проекта

```text
project/
├── backend/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py
│   │   ├── database.py
│   │   ├── models.py
│   │   ├── schemas.py
│   │   ├── crud.py
│   │   └── routers/
│   │       ├── __init__.py
│   │       └── games.py
│   ├── alembic/
│   │   └── versions/
│   ├── alembic.ini
│   ├── requirements.txt
│   └── .env
├── frontend/
│   ├── index.html
│   ├── styles/
│   │   └── main.css
│   └── scripts/
│       └── main.js
└── README.md
```

Назначение файлов:

| Файл или папка | Назначение |
|---|---|
| `main.py` | Точка входа backend-приложения |
| `database.py` | Подключение к базе данных |
| `models.py` | Модели SQLAlchemy, описывающие таблицы |
| `schemas.py` | Pydantic-схемы для запросов и ответов |
| `crud.py` | Функции создания, чтения, обновления и удаления |
| `routers/` | HTTP-маршруты API |
| `alembic/` | Миграции базы данных |
| `requirements.txt` | Зависимости Python-проекта |
| `.env` | Локальные настройки, например строка подключения к БД |

Файл `.env` не должен попадать в Git-репозиторий. Для этого его нужно добавить в `.gitignore`.

## Пример структуры FastAPI

### `main.py`

```python
from fastapi import FastAPI
from app.routers import games

app = FastAPI(
    title="Games Catalog API",
    version="1.0.0",
    description="REST API для каталога видеоигр"
)

app.include_router(games.router, prefix="/api")
```

### `models.py`

```python
from sqlalchemy import Integer, Numeric, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class Game(Base):
    __tablename__ = "games"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[str | None] = mapped_column(Text)
    genre: Mapped[str] = mapped_column(String(100), nullable=False)
    platform: Mapped[str] = mapped_column(String(100), nullable=False)
    release_year: Mapped[int] = mapped_column(Integer, nullable=False)
    rating: Mapped[float | None] = mapped_column(Numeric(3, 1))
    image_url: Mapped[str | None] = mapped_column(String(500))
```

### `schemas.py`

```python
from datetime import datetime
from pydantic import BaseModel, Field


class GameCreate(BaseModel):
    title: str = Field(min_length=1, max_length=200)
    description: str | None = None
    genre: str = Field(min_length=1, max_length=100)
    platform: str = Field(min_length=1, max_length=100)
    release_year: int = Field(ge=1950, le=2100)
    rating: float | None = Field(default=None, ge=0, le=10)
    image_url: str | None = None


class GameUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=200)
    description: str | None = None
    genre: str | None = Field(default=None, min_length=1, max_length=100)
    platform: str | None = Field(default=None, min_length=1, max_length=100)
    release_year: int | None = Field(default=None, ge=1950, le=2100)
    rating: float | None = Field(default=None, ge=0, le=10)
    image_url: str | None = None


class Game(BaseModel):
    id: int
    title: str
    description: str | None
    genre: str
    platform: str
    release_year: int
    rating: float | None
    image_url: str | None
    created_at: datetime

    model_config = {
        "from_attributes": True
    }
```

### `crud.py`

```python
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Game
from app.schemas import GameCreate, GameUpdate


async def get_games(db: AsyncSession) -> list[Game]:
    result = await db.execute(select(Game))
    return result.scalars().all()


async def get_game(db: AsyncSession, game_id: int) -> Game | None:
    return await db.get(Game, game_id)


async def create_game(db: AsyncSession, data: GameCreate) -> Game:
    game = Game(**data.model_dump())
    db.add(game)
    await db.commit()
    await db.refresh(game)
    return game


async def update_game(
    db: AsyncSession,
    game: Game,
    data: GameUpdate
) -> Game:
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(game, field, value)

    await db.commit()
    await db.refresh(game)
    return game


async def delete_game(db: AsyncSession, game: Game) -> None:
    await db.delete(game)
    await db.commit()
```

### `routers/games.py`

```python
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app import crud
from app.database import get_db
from app.schemas import Game, GameCreate, GameUpdate

router = APIRouter(
    prefix="/games",
    tags=["Games"]
)


@router.get("", response_model=list[Game])
async def read_games(db: AsyncSession = Depends(get_db)):
    return await crud.get_games(db)


@router.post(
    "",
    response_model=Game,
    status_code=status.HTTP_201_CREATED
)
async def create_game(
    data: GameCreate,
    db: AsyncSession = Depends(get_db)
):
    return await crud.create_game(db, data)


@router.get("/{game_id}", response_model=Game)
async def read_game(
    game_id: int,
    db: AsyncSession = Depends(get_db)
):
    game = await crud.get_game(db, game_id)

    if game is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Game not found"
        )

    return game


@router.patch("/{game_id}", response_model=Game)
async def update_game(
    game_id: int,
    data: GameUpdate,
    db: AsyncSession = Depends(get_db)
):
    game = await crud.get_game(db, game_id)

    if game is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Game not found"
        )

    return await crud.update_game(db, game, data)


@router.delete("/{game_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_game(
    game_id: int,
    db: AsyncSession = Depends(get_db)
):
    game = await crud.get_game(db, game_id)

    if game is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Game not found"
        )

    await crud.delete_game(db, game)
```

## Варианты по темам

Ниже приведены примеры того, какую сущность можно выбрать в качестве основной.

| Тема | Основная сущность | Пример endpoint-ов |
|---|---|---|
| Сайт с видеоиграми | Игра | `/api/games` |
| Трекер чтения новелл | Новелла | `/api/novels` |
| Кулинарная книга | Рецепт | `/api/recipes` |
| Каталог компьютерных компонентов | Компонент | `/api/components` |
| Складской учёт | Товар | `/api/products` |
| Игра «Сломанный телефон» | Сообщение | `/api/messages` |
| Персонализированные заметки | Заметка | `/api/notes` |
| Афиша мероприятий | Мероприятие | `/api/events` |
| Сайт с попутчиками | Поездка | `/api/trips` |
| Квесты в браузере | Квест | `/api/quests` |
| Каталог вакансий | Вакансия | `/api/vacancies` |
| Справочник грибов | Гриб | `/api/mushrooms` |
| Справочник собак | Порода | `/api/dog-breeds` |
| Справочник котов | Порода | `/api/cat-breeds` |
| Аналог Дрома | Объявление | `/api/listings` |
| Каталог настолок | Настольная игра | `/api/board-games` |
| Каталог автозапчастей | Запчасть | `/api/parts` |
| Магазин чая | Товар | `/api/teas` |
| Brawl Stars | Персонаж | `/api/characters` |
| Панель статистики компьютера | Метрика | `/api/metrics` |
| Сервис фото + ИИ | Фото | `/api/photos` |
| Личный дневник или заметки | Запись | `/api/diary-entries` |
| Дневник репетитора | Ученик | `/api/students` |

## Что должно работать на защите

Показать:

1. Запущенный backend.
2. Открытую Swagger-документацию.
3. Создание записи через `POST`.
4. Получение списка записей через `GET`.
5. Получение одной записи по `id`.
6. Обновление записи через `PATCH` или `PUT`.
7. Удаление записи через `DELETE`.
8. Проверку, что данные действительно сохраняются в БД.
9. Загрузку данных на frontend через `fetch`.
10. Создание, изменение и удаление записи из интерфейса сайта.

## Что сдаётся

1. Ссылка на Git-репозиторий.
2. Инструкцию по запуску backend и frontend.
3. Скриншот Swagger UI с раскрытыми методами API.
4. Скриншот таблицы в базе данных с добавленными записями.
5. Скриншот frontend, на котором данные загружены с backend.
6. Краткое описание сущностей и API в `README.md`.

## README.md

В `README.md` необходимо указать:

- название проекта;
- выбранную тему;
- основную сущность;
- список полей сущности;
- список реализованных endpoint-ов;
- используемый стек;
- инструкцию по установке зависимостей;
- инструкцию по запуску базы данных;
- инструкцию по запуску backend;
- инструкцию по запуску frontend;
- ссылку на Swagger UI;
- примеры запросов.

Пример раздела README:

```markdown
# Каталог видеоигр

Веб-приложение для хранения и просмотра информации о видеоиграх.

## Основная сущность

Игра (`Game`).

Поля:

- `id`
- `title`
- `description`
- `genre`
- `platform`
- `release_year`
- `rating`
- `image_url`
- `created_at`

## API

| Метод | Путь | Описание |
|---|---|---|
| GET | `/api/games` | Получить список игр |
| POST | `/api/games` | Создать игру |
| GET | `/api/games/{id}` | Получить игру по id |
| PATCH | `/api/games/{id}` | Частично обновить игру |
| DELETE | `/api/games/{id}` | Удалить игру |

## Запуск backend

```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

Swagger UI:

http://127.0.0.1:8000/docs

## Запуск frontend

Открыть `frontend/index.html` через локальный сервер, например:

```bash
cd frontend
python -m http.server 5500
```

Затем открыть:

http://127.0.0.1:5500
```
