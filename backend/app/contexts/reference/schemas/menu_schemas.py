from pydantic import BaseModel


class MenuItemResponse(BaseModel):
    id: str
    category: str
    name: str
    price: float

    model_config = {"from_attributes": True}


class MenuResponse(BaseModel):
    pizzas: list[MenuItemResponse]
    bases: list[MenuItemResponse]
    toppings: list[MenuItemResponse]
