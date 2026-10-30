"""Pydantic проверяет JSON до обращения к базе данных."""
from datetime import datetime, timezone
from decimal import Decimal
from typing import Annotated, Literal
from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

Name = Annotated[str, Field(min_length=3, max_length=60)]
Description = Annotated[str, Field(min_length=10, max_length=240)]
Article = Annotated[str, Field(min_length=4, max_length=20, pattern=r"^[A-ZА-ЯЁ0-9-]+$")]
Price = Annotated[Decimal, Field(ge=1, le=1000000, max_digits=9, decimal_places=2, allow_inf_nan=False)]
CategoryID = Annotated[int, Field(gt=0, strict=True)]
Parameter = Annotated[str, Field(max_length=120)]
ImageURL = Literal["/assets/images/filter.svg", "/assets/images/brake.svg", "/assets/images/plug.svg", "/assets/images/air.svg", "/assets/images/shock.svg", "/assets/images/belt.svg"]

EXAMPLE = {"name": "Салонный фильтр", "description": "Очищает воздух в салоне автомобиля от пыли.", "article": "AP-CB-007", "price": "790.50", "category_id": 1, "parameter": "Угольный, 200 × 180 мм", "image_url": "/assets/images/filter.svg"}

class InputModel(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)
    @field_validator("article", mode="before", check_fields=False)
    @classmethod
    def normalize_article(cls, value):
        return value.strip().upper() if isinstance(value, str) else value

class PartCreate(InputModel):
    name: Name
    description: Description
    article: Article
    price: Price
    category_id: CategoryID
    parameter: Parameter = "Добавлено пользователем"
    image_url: ImageURL = "/assets/images/filter.svg"
    model_config = ConfigDict(json_schema_extra={"examples": [EXAMPLE]})

class PartUpdate(InputModel):
    name: Name | None = None
    description: Description | None = None
    article: Article | None = None
    price: Price | None = None
    category_id: CategoryID | None = None
    parameter: Parameter | None = None
    image_url: ImageURL | None = None
    model_config = ConfigDict(json_schema_extra={"examples": [{"price": "849.90"}]})
    @model_validator(mode="before")
    @classmethod
    def reject_explicit_null(cls, values):
        # Отсутствующее поле не меняется; явный null недопустим для NOT NULL.
        if isinstance(values, dict) and any(value is None for value in values.values()):
            raise ValueError("Поля запчасти не могут быть null; не передавайте неизменяемые поля.")
        return values

class CategoryRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    name: str
    slug: str

class PartRead(BaseModel):
    model_config = ConfigDict(from_attributes=True, json_schema_extra={"examples": [{**EXAMPLE, "id": 7, "category": {"id": 1, "name": "Двигатель", "slug": "engine"}, "created_at": "2026-10-30T12:00:00Z"}]})
    id: int
    name: str
    description: str
    article: str
    price: Decimal
    category_id: int
    category: CategoryRead
    parameter: str
    image_url: str
    created_at: datetime
    @field_validator("created_at")
    @classmethod
    def utc_timestamp(cls, value):
        return value.replace(tzinfo=timezone.utc) if value.tzinfo is None else value

class ErrorRead(BaseModel):
    detail: str
