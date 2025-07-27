from enum import Enum
from datetime import datetime

from pydantic import BaseModel, computed_field


class ReceiptCurrency(Enum):
    """
    Enum for supported receipt currencies
    """

    EUR = "EUR"
    PLN = "PLN"


class ReceiptItem(BaseModel):
    """
    Represents an item in a receipt
    """

    name: str
    quantity: int
    unit_price: float


class Receipt(BaseModel):
    """
    Represents a receipt with its details
    """

    shop_name: str
    items: list[ReceiptItem]
    date: datetime
    currency: ReceiptCurrency

    @computed_field
    @property
    def total_amount(self) -> float:
        """
        Calculates the total amount of the receipt based on its items.
        """
        return sum(item.quantity * item.unit_price for item in self.items)
