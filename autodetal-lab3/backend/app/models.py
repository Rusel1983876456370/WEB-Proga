"""Две связанные сущности: категория (1) -> запчасти (N)."""
from datetime import datetime, timezone
from decimal import Decimal
from sqlalchemy import CheckConstraint, DateTime, ForeignKey, Integer, Numeric, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from .database import Base

class Category(Base):
    __tablename__ = "categories"
    __table_args__ = (
        CheckConstraint("length(trim(name)) BETWEEN 1 AND 60", name="ck_category_name"),
        CheckConstraint("length(trim(slug)) BETWEEN 1 AND 30", name="ck_category_slug"),
    )
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(60), unique=True, nullable=False)
    slug: Mapped[str] = mapped_column(String(30), unique=True, nullable=False)
    parts: Mapped[list["Part"]] = relationship(back_populates="category")

class Part(Base):
    __tablename__ = "parts"
    __table_args__ = (
        CheckConstraint("length(trim(name)) BETWEEN 3 AND 60", name="ck_part_name"),
        CheckConstraint("length(trim(description)) BETWEEN 10 AND 240", name="ck_part_description"),
        CheckConstraint("length(trim(article)) BETWEEN 4 AND 20 AND article = upper(article)", name="ck_part_article"),
        CheckConstraint("price >= 1 AND price <= 1000000 AND abs(price * 100 - round(price * 100)) < 0.00001", name="ck_part_price"),
        CheckConstraint("length(parameter) <= 120", name="ck_part_parameter"),
        CheckConstraint("image_url IN ('/assets/images/filter.svg', '/assets/images/brake.svg', '/assets/images/plug.svg', '/assets/images/air.svg', '/assets/images/shock.svg', '/assets/images/belt.svg')", name="ck_part_image"),
        {"sqlite_autoincrement": True},
    )
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(60), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    article: Mapped[str] = mapped_column(String(20), unique=True, nullable=False)
    price: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    category_id: Mapped[int] = mapped_column(ForeignKey("categories.id", ondelete="RESTRICT"), nullable=False, index=True)
    parameter: Mapped[str] = mapped_column(String(120), nullable=False, default="Добавлено пользователем")
    image_url: Mapped[str] = mapped_column(String(100), nullable=False, default="/assets/images/filter.svg")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc))
    category: Mapped[Category] = relationship(back_populates="parts", lazy="joined")
