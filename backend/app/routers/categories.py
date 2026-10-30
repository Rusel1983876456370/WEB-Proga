from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, Path
from sqlalchemy import select
from sqlalchemy.orm import Session
from ..database import get_db
from ..models import Category
from ..schemas import CategoryRead, ErrorRead

router = APIRouter(prefix="/categories", tags=["Категории"])

@router.get("", response_model=list[CategoryRead], summary="Получить справочник категорий", responses={500: {"model": ErrorRead}})
def read_categories(db: Annotated[Session, Depends(get_db)]):
    return db.scalars(select(Category).order_by(Category.id)).all()

@router.get("/{category_id}", response_model=CategoryRead, summary="Получить категорию по ID", responses={404: {"model": ErrorRead}, 500: {"model": ErrorRead}})
def read_category(category_id: Annotated[int, Path(gt=0)], db: Annotated[Session, Depends(get_db)]):
    category = db.get(Category, category_id)
    if category is None:
        raise HTTPException(404, "Категория не найдена")
    return category
