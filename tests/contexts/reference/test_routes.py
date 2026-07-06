import pytest

from app.contexts.reference.entities.menu_item import MenuItem


@pytest.fixture
def available_menu_items(db_session) -> list[MenuItem]:
    items = [
        MenuItem(
            name="Margherita", category="Classic",
            available_bases=["Thin Crust", "Thick Crust", "Stuffed Crust"],
            available_toppings=["Mozzarella", "Tomato Sauce", "Extra Cheese"],
            price=299.0, is_available=True,
        ),
        MenuItem(
            name="Pepperoni", category="Non-Veg",
            available_bases=["Thin Crust", "Thick Crust"],
            available_toppings=["Pepperoni", "Mozzarella", "Jalapenos"],
            price=399.0, is_available=True,
        ),
        MenuItem(
            name="Discontinued", category="Classic",
            available_bases=["Thin Crust"],
            available_toppings=["Cheese"],
            price=199.0, is_available=False,
        ),
    ]
    db_session.add_all(items)
    db_session.commit()
    return items


def test_retrieve_menu_returns_200(client):
    response = client.get("/menu")

    assert response.status_code == 200


def test_retrieve_menu_response_structure(client, available_menu_items):
    response = client.get("/menu")
    body = response.json()

    assert "items" in body
    assert isinstance(body["items"], list)


def test_retrieve_menu_excludes_unavailable_items(client, available_menu_items):
    response = client.get("/menu")
    items = response.json()["items"]

    assert len(items) == 2
    names = {item["name"] for item in items}
    assert "Discontinued" not in names


def test_retrieve_menu_item_has_required_fields(client, available_menu_items):
    response = client.get("/menu")
    item = response.json()["items"][0]

    assert "id" in item
    assert "name" in item
    assert "category" in item
    assert "available_bases" in item
    assert "available_toppings" in item
    assert "price" in item


def test_retrieve_menu_returns_empty_list_when_no_items(client):
    response = client.get("/menu")
    body = response.json()

    assert body["items"] == []


def test_retrieve_menu_bases_and_toppings_are_lists(client, available_menu_items):
    response = client.get("/menu")
    item = response.json()["items"][0]

    assert isinstance(item["available_bases"], list)
    assert isinstance(item["available_toppings"], list)
    assert len(item["available_bases"]) > 0
