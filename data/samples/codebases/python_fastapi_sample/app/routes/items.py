from fastapi import APIRouter
from app.services.item_service import ItemService
router = APIRouter()
service = ItemService()
@router.get("/items")
async def list_items(): return service.list_all()
@router.post("/items")
async def create_item(item: dict): return service.create(item)
