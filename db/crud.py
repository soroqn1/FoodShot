from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from db.models import MealLog, User


async def get_user(session: AsyncSession, user_id: int) -> User | None:
    result = await session.execute(select(User).where(User.id == user_id))
    return result.scalar_one_or_none()


async def create_user(session: AsyncSession, **kwargs) -> User:
    user = User(**kwargs)
    session.add(user)
    await session.commit()
    await session.refresh(user)
    return user


async def update_user(session: AsyncSession, user_id: int, **kwargs) -> User | None:
    user = await get_user(session, user_id)
    if user:
        for key, value in kwargs.items():
            setattr(user, key, value)
        await session.commit()
        await session.refresh(user)
    return user


async def create_meal_log(session: AsyncSession, **kwargs) -> MealLog:
    meal = MealLog(**kwargs)
    session.add(meal)
    await session.commit()
    await session.refresh(meal)
    return meal


async def get_user_history(
    session: AsyncSession, user_id: int, limit: int = 10
) -> list[MealLog]:
    result = await session.execute(
        select(MealLog)
        .where(MealLog.user_id == user_id)
        .order_by(MealLog.created_at.desc())
        .limit(limit)
    )
    return list(result.scalars().all())


async def update_user_language(session: AsyncSession, user_id: int, language: str):
    await session.execute(
        update(User).where(User.id == user_id).values(language=language)
    )
    await session.commit()
