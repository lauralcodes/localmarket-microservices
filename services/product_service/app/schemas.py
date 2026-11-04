from decimal import Decimal

from pydantic import BaseModel, Field

class ProductCreate(BaseModel):
    name: str = Field(min_length=1, max_length=150)
    description: str | None = Field(default=None)
    price: Decimal = Field(gt=0, max_digits=10, decimal_places=2)
    shop_name: str = Field(min_length=1, max_length=150)

# create separate Pydantic model for updates
class ProductUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=150)
    description: str | None = None
    price: Decimal | None = Field(
        default=None,
        gt=0,
        max_digits=10,
        decimal_places=2,
    )
    shop_name: str | None = Field(default=None, min_length=1, max_length=150)