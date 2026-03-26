from __future__ import annotations

from typing import Optional

from pydantic import BaseModel, Field


class Customer(BaseModel):
    customer_id: int
    customer_name: Optional[str] = Field(max_length=5)
    customer_address: Optional[str] = None

    model_config = {'extra':'forbid'}

    def __str__(self):
        return str(self.customer_id) +' '+ self.customer_name + ' '+  self.customer_address


class CustomerOut(BaseModel):
    customer_id: int
    customer_name: str
