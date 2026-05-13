import os
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from routers import products, orders, users, chat
import time

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.middleware("http")
async def add_process_time(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(process_time)
    print(f"{request.method} {request.url.path}")
    return response

app.include_router(products.router)
app.include_router(orders.router)
app.include_router(users.router)
app.include_router(chat.router)

@app.get("/")
async def root():
    return {"message": "Hello World"}