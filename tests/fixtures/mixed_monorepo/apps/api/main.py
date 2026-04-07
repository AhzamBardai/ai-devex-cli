"""FastAPI e-commerce backend."""
from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI(title="E-Commerce API", version="1.0.0")


class Product(BaseModel):
    id: str
    name: str
    price_usd: float
    stock: int


@app.get("/api/products/{product_id}", response_model=Product)
async def get_product(product_id: str) -> Product:
    return Product(id=product_id, name="Widget", price_usd=9.99, stock=100)
