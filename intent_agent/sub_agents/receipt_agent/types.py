from pydantic import BaseModel, computed_field, Field
from typing import Literal




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
    date: str = Field(..., description="Date of the receipt in YYYY-mm-dd format")
    currency: Literal["EUR", "PLN"] = Field(..., description="Supported currency code")

    @computed_field
    @property
    def total_amount(self) -> float:
        """
        Calculates the total amount of the receipt based on its items.
        """
        return sum(item.quantity * item.unit_price for item in self.items)
