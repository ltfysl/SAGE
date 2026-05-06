from app.models.item import Item
class ItemService:
    def list_all(self): return Item.query.all()
    def create(self, data): return Item(**data).save()
