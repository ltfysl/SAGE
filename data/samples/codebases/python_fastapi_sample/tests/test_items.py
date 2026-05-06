from app.services.item_service import ItemService
def test_create_item():
    service = ItemService()
    result = service.create({"name": "test"})
    assert result is not None
