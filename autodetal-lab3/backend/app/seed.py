"""Первичное заполнение: выполняется один раз, пока нет категорий."""
from sqlalchemy import select, func
from sqlalchemy.orm import Session
from .database import Base
from .models import Category, Part

CATEGORIES = [("engine", "Двигатель"), ("brakes", "Тормоза"), ("ignition", "Зажигание"), ("suspension", "Подвеска"), ("drive", "Привод"), ("other", "Другое")]
PARTS = [('Масляный фильтр', 'engine', 'Задерживает загрязнения в системе смазки двигателя.', 'AP-FL-001', 'Резьба M20 × 1,5', 490, 'filter.svg'), ('Тормозной диск', 'brakes', 'Рабочая поверхность для торможения колеса колодками.', 'AP-BR-002', 'Диаметр 280 мм', 3200, 'brake.svg'), ('Свеча зажигания', 'ignition', 'Создаёт искру для воспламенения смеси в бензиновом двигателе.', 'AP-IG-003', 'Резьба M14 × 1,25', 650, 'plug.svg'), ('Воздушный фильтр', 'engine', 'Очищает воздух перед поступлением во впускную систему.', 'AP-FL-004', 'Размер 250 × 180 мм', 890, 'air.svg'), ('Амортизатор', 'suspension', 'Гасит колебания кузова и помогает колесу сохранять контакт с дорогой.', 'AP-SU-005', 'Тип: газомасляный', 4500, 'shock.svg'), ('Поликлиновой ремень', 'drive', 'Передаёт вращение от двигателя к навесным агрегатам.', 'AP-DR-006', 'Профиль 6PK, длина 1050 мм', 1100, 'belt.svg')]

def init_db(engine, seed=True):
    Base.metadata.create_all(engine)
    if not seed:
        return
    with Session(engine) as db:
        if db.scalar(select(func.count()).select_from(Category)):
            return  # Удалённые пользователем детали не создаются заново.
        categories = {}
        for slug, name in CATEGORIES:
            category = Category(slug=slug, name=name)
            db.add(category)
            categories[slug] = category
        db.flush()
        for name, slug, description, article, parameter, price, image in PARTS:
            db.add(Part(name=name, category_id=categories[slug].id, description=description, article=article, parameter=parameter, price=price, image_url=f"/assets/images/{image}"))
        db.commit()
