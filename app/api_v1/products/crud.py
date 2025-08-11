"""
Create
Read
Update
Delete
"""

from sqlalchemy import select
from sqlalchemy.engine import Result
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.product import Product
from .schemas import ProductCreate, ProductUpdate, ProductUpdatePartial


async def get_products(session: AsyncSession) -> list[Product]:
    # выражение SELECT * FROM product ORDER BY id
    stat = select(Product).order_by(Product.id)
    # Асинхронное выполнение выражения
    result: Result = await session.execute(stat)
    # Извлекает без обертки tuple, all() = изменяет iter on list
    products = result.scalars().all()
    return list(products)


async def get_product(session: AsyncSession, product_id: int) -> Product | None:
    # SELECT * FROM product WHERE id = :product_id;
    return await session.get(Product, product_id)


async def create_product(session: AsyncSession, product_in: ProductCreate) -> Product:
    # Превращает JSON форму Pydantic в dict() и создает ORM-объект
    product = Product(**product_in.model_dump())
    # Добавляет ORM-Объект product в БД, но еще объект не вставлен в БД
    session.add(product)
    # SQL-Запрос на INSERT INTO - Добавление в БД, без commit() никаких изменений не было бы
    await session.commit()
    # # # await session.refresh(product)
    # Возвращаем созданный ORM-Объект
    return product


async def update_product(
    session: AsyncSession,
    product: Product,
    product_update: ProductUpdate | ProductUpdatePartial,
    partial: bool = False,
) -> Product:
    for key, value in product_update.model_dump(exclude_unset=partial).items():
        setattr(product, key, value)
    await session.commit()
    return product


async def delete_product(
    session: AsyncSession,
    product: Product,
) -> None:
    await session.delete(product)
    await session.commit()
