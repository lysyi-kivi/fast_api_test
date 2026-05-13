from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from pydantic import BaseModel
from typing import Optional
from database import get_db
from models import Product
from auth.dependencies import get_current_user
from cache import get_cache, set_cache, delete_cache

router = APIRouter(prefix="/products", tags=["products"])

class ProductCreate(BaseModel):
    name: str
    price: float
    in_stock: bool = True

class ProductUpdate(BaseModel):
    name: Optional[str] = None
    price: Optional[float] = None
    in_stock: Optional[bool] = None

@router.get("/")
async def get_products(db: AsyncSession = Depends(get_db)):
    # Проверяем кэш
    cached = await get_cache("products:all")
    if cached is not None:
        print("Данные из кэша!")
        return cached

    # Если кэша нет — идём в БД
    result = await db.execute(select(Product))
    products = result.scalars().all()
    products_list = [
        {"id": p.id, "name": p.name, "price": p.price, "in_stock": p.in_stock}
        for p in products
    ]

    # Сохраняем в кэш на 60 секунд
    await set_cache("products:all", products_list, expire=60)
    print("Данные из БД, сохранили в кэш!")
    return products_list

@router.get("/{product_id}")
async def get_product(product_id: int, db: AsyncSession = Depends(get_db)):
    # Кэш для отдельного товара
    cached = await get_cache(f"products:{product_id}")
    if cached:
        print(f"Товар {product_id} из кэша!")
        return cached

    product = await db.get(Product, product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Товар не найден")

    product_dict = {
        "id": product.id,
        "name": product.name,
        "price": product.price,
        "in_stock": product.in_stock
    }
    await set_cache(f"products:{product_id}", product_dict, expire=60)
    return product_dict

@router.post("/", status_code=201)
async def create_product(
    data: ProductCreate,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    product = Product(**data.model_dump())
    db.add(product)
    await db.commit()
    await db.refresh(product)
    # Инвалидируем кэш списка товаров
    await delete_cache("products:all")
    return product

@router.patch("/{product_id}")
async def update_product(
    product_id: int,
    data: ProductUpdate,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    product = await db.get(Product, product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Товар не найден")
    for key, value in data.model_dump(exclude_none=True).items():
        setattr(product, key, value)
    await db.commit()
    await db.refresh(product)
    # Инвалидируем кэш
    await delete_cache("products:all")
    await delete_cache(f"products:{product_id}")
    return product

@router.delete("/{product_id}", status_code=204)
async def delete_product(
    product_id: int,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    product = await db.get(Product, product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Товар не найден")
    await db.delete(product)
    await db.commit()
    # Инвалидируем кэш
    await delete_cache("products:all")
    await delete_cache(f"products:{product_id}")