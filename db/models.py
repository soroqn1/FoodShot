from datetime import datetime

from sqlalchemy import BigInteger, DateTime, Float, ForeignKey, String, func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    pass


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    username: Mapped[str | None] = mapped_column(String(255))
    icr: Mapped[float] = mapped_column(Float)
    isf: Mapped[float] = mapped_column(Float)
    target_bg: Mapped[float] = mapped_column(Float)
    insulin_type: Mapped[str | None] = mapped_column(String(50))
    language: Mapped[str] = mapped_column(String(5), server_default="en")
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    meals: Mapped[list["MealLog"]] = relationship(
        back_populates="user", cascade="all, delete-orphan"
    )


class MealLog(Base):
    __tablename__ = "meal_logs"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("users.id"))
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    dish_name: Mapped[str | None] = mapped_column(String(255))
    portion_g: Mapped[float | None] = mapped_column(Float)
    carbs_g: Mapped[float | None] = mapped_column(Float)
    kcal: Mapped[float | None] = mapped_column(Float)
    protein_g: Mapped[float | None] = mapped_column(Float)
    fat_g: Mapped[float | None] = mapped_column(Float)
    bolus_dose: Mapped[float | None] = mapped_column(Float)
    current_bg: Mapped[float | None] = mapped_column(Float)
    photo_file_id: Mapped[str | None] = mapped_column(String(255))

    user: Mapped["User"] = relationship(back_populates="meals")
