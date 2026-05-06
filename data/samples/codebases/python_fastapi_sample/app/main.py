from fastapi import FastAPI
from app.routes.items import router as items_router
app = FastAPI()
app.include_router(items_router)
