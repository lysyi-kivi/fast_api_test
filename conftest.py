import os
os.environ["TESTING"] = "1"

import sys
import pytest
from httpx import AsyncClient, ASGITransport
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

sys.path.insert(0, os.path.dirname(__file__))

from routers import products, orders, users

test_app = FastAPI()

test_app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

test_app.include_router(products.router)
test_app.include_router(orders.router)
test_app.include_router(users.router)

@test_app.get("/")
async def root():
    return {"message": "Hello World"}

@pytest.fixture(scope="session")
async def client():
    async with AsyncClient(transport=ASGITransport(app=test_app), base_url="http://test") as c:
        yield c