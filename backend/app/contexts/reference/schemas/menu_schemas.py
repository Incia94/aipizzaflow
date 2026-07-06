from pydantic import BaseModel


class MenuItemResponse(BaseModel):
    id: int
    name: str
    category: str
    available_bases: list[str]
    available_toppings: list[str]
    price: float

    model_config = {"from_attributes": True}


class MenuResponse(BaseModel):
    items: list[MenuItemResponse]
