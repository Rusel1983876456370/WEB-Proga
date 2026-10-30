from typing import Annotated
from fastapi import APIRouter, Depends, Path, Response
from sqlalchemy.orm import Session
from .. import crud
from ..database import get_db
from ..schemas import PartCreate, PartRead, PartUpdate, ErrorRead

router = APIRouter(prefix="/parts", tags=["Запчасти"])
DB = Annotated[Session, Depends(get_db)]
PartID = Annotated[int, Path(gt=0, description="Уникальный целочисленный ID запчасти", examples=[1])]
ERRORS = {400: {"model": ErrorRead, "description": "Некорректный запрос или повторяющийся артикул"}, 404: {"model": ErrorRead, "description": "Запчасть не найдена"}, 500: {"model": ErrorRead, "description": "Внутренняя ошибка сервера"}}

@router.get("", response_model=list[PartRead], summary="Получить все запчасти", responses={500: ERRORS[500]})
def read_parts(db: DB):
    return crud.get_parts(db)

@router.post("", response_model=PartRead, status_code=201, summary="Создать запчасть", responses=ERRORS)
def create_part(data: PartCreate, db: DB, response: Response):
    part = crud.create_part(db, data)
    response.headers["Location"] = f"/api/parts/{part.id}"
    return part

@router.get("/{part_id}", response_model=PartRead, summary="Получить запчасть по ID", responses={404: ERRORS[404], 500: ERRORS[500]})
def read_part(part_id: PartID, db: DB):
    return crud.get_part(db, part_id)

@router.patch("/{part_id}", response_model=PartRead, summary="Изменить поля запчасти", responses=ERRORS)
def update_part(part_id: PartID, data: PartUpdate, db: DB):
    return crud.update_part(db, crud.get_part(db, part_id), data)

@router.delete("/{part_id}", status_code=204, summary="Удалить запчасть", responses={404: ERRORS[404], 500: ERRORS[500]})
def delete_part(part_id: PartID, db: DB):
    crud.delete_part(db, crud.get_part(db, part_id))
    return Response(status_code=204)
