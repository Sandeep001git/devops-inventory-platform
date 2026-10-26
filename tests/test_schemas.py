import pytest
from pydantic import ValidationError

from app.schemas import InventoryItemCreate


def test_valid_inventory_item() -> None:
    item = InventoryItemCreate(name="Keyboard", quantity=10)

    assert item.name == "Keyboard"
    assert item.description is None
    assert item.quantity == 10


def test_rejects_empty_name() -> None:
    with pytest.raises(ValidationError):
        InventoryItemCreate(name="", quantity=1)


def test_rejects_negative_quantity() -> None:
    with pytest.raises(ValidationError):
        InventoryItemCreate(name="Keyboard", quantity=-1)
