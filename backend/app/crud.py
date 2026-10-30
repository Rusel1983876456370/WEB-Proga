"""Операции с данными; значения передаются через ORM, без склейки SQL."""
from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from .models import Category, Part


def get_parts(db: Session):
    return db.scalars(select(Part).order_by(Part.id)).all()

def get_part(db: Session, part_id: int):
    part = db.get(Part, part_id)
    if part is None:
        raise HTTPException(404, "Запчасть не найдена")
    return part

def require_category(db: Session, category_id: int):
    if db.get(Category, category_id) is None:
        raise HTTPException(400, "Указанная категория не существует")

def commit(db: Session):
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(400, "Нарушено ограничение БД. Артикул должен быть уникальным.") from None

def create_part(db: Session, data):
    require_category(db, data.category_id)
    part = Part(**data.model_dump())
    db.add(part)
    commit(db)
    db.refresh(part)
    return part

def update_part(db: Session, part: Part, data):
    changes = data.model_dump(exclude_unset=True)
    if not changes:
        raise HTTPException(400, "Укажите хотя бы одно поле для изменения")
    if "category_id" in changes:
        require_category(db, changes["category_id"])
    for field, value in changes.items():
        setattr(part, field, value)
    commit(db)
    db.refresh(part)
    return part

def delete_part(db: Session, part: Part):
    db.delete(part)
    commit(db)
