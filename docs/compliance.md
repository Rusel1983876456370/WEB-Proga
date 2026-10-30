# Соответствие методичке ЛР3

| Требование | Реализация / материал |
|---|---|
| Продолжение существующего сайта | frontend: оформление, иллюстрации, поиск, фильтры и сортировка ЛР2 сохранены |
| Основная сущность | Part, backend/app/models.py |
| Связанная сущность | Category, связь 1:N через category_id |
| Python backend | FastAPI, backend/app/main.py |
| Полный CRUD | GET, POST /api/parts; GET, PATCH, DELETE /api/parts/{part_id} |
| Ресурсные пути во множественном числе | /api/parts, /api/categories |
| Валидация типов, обязательности, длины, диапазона | Pydantic-схемы, backend/app/schemas.py; клиентская валидация формы |
| Коды 200, 201, 204, 400, 404, 422, 500 | Маршруты и обработчики ошибок; тесты |
| Реляционная БД | SQLite, data/autodetal.db |
| PK, типы, NOT NULL | Модели SQLAlchemy; docs/schema.sql |
| UNIQUE | Артикул детали, имя и slug категории |
| CHECK | Цена, дробные копейки, длины обязательных строк, иллюстрация |
| FOREIGN KEY | parts.category_id → categories.id; PRAGMA foreign_keys=ON |
| OpenAPI автоматически | /openapi.json; docs/openapi.json — выгруженный снимок |
| Swagger | /docs, локальные ресурсы без CDN |
| Схемы запросов и ответов, параметры, примеры | PartCreate, PartUpdate, PartRead, CategoryRead, описания маршрутов |
| Frontend fetch: загрузка списка | loadData → GET /api/parts и GET /api/categories |
| Карточки из ответа сервера | makeCard, render |
| Создание через форму | POST /api/parts |
| Обновление хотя бы одного поля | Форма «Изменить» → PATCH, можно менять все поля |
| Удаление через интерфейс | DELETE + подтверждение |
| Сохранение после перезапуска | Реальный файл SQLite; тест двух процессов |
| Инструкция установки и запуска | README.md, start.bat, start.sh |
| Скриншот Swagger с раскрытыми методами | docs/screenshots/02c-swagger-crud-expanded.png; 02-swagger.png |
| Скриншот таблицы с записями | docs/screenshots/03-database.png; реальный SELECT, HTML-представление |
| Скриншот frontend из backend | docs/screenshots/01-frontend.png |
| Краткое описание сущностей и API | README.md |
| Ссылка на Git-репозиторий | Подготовлен локальный bundle; для внешней ссылки нужен репозиторий владельца, URL не предоставлен |

PostgreSQL/SQLAlchemy указаны в рекомендуемом стеке; SQLite явно допустима.
Alembic, аутентификация, пагинация и полный CRUD категорий не входят в минимальный объём ЛР3.
