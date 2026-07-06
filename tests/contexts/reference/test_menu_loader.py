from unittest.mock import MagicMock

import pytest

from app.contexts.reference.entities.menu_item import MenuItem
from app.contexts.reference.repositories.menu_repository import MenuRepository
from app.contexts.reference.schemas.menu_schemas import MenuResponse
from app.contexts.reference.service import MenuLoader


@pytest.fixture
def mock_repository() -> MenuRepository:
    return MagicMock(spec=MenuRepository)


@pytest.fixture
def service(mock_repository: MenuRepository) -> MenuLoader:
    return MenuLoader(mock_repository)


def test_load_menu_returns_menu_response(service, mock_repository):
    mock_repository.get_available_items.return_value = [
        MenuItem(
            id=1, name="Margherita", category="Classic",
            available_bases=["Thin Crust", "Thick Crust"],
            available_toppings=["Mozzarella", "Tomato"],
            price=299.0, is_available=True,
        ),
    ]

    result = service.load_menu()

    assert isinstance(result, MenuResponse)
    assert len(result.items) == 1
    assert result.items[0].name == "Margherita"
    assert result.items[0].price == 299.0
    assert result.items[0].available_bases == ["Thin Crust", "Thick Crust"]


def test_load_menu_returns_empty_list_when_no_items(service, mock_repository):
    mock_repository.get_available_items.return_value = []

    result = service.load_menu()

    assert result.items == []
    mock_repository.get_available_items.assert_called_once()


def test_load_menu_maps_all_fields(service, mock_repository):
    mock_repository.get_available_items.return_value = [
        MenuItem(
            id=7, name="BBQ Chicken", category="Non-Veg",
            available_bases=["Thin Crust"],
            available_toppings=["Grilled Chicken", "BBQ Sauce"],
            price=449.0, is_available=True,
        ),
    ]

    result = service.load_menu()

    item = result.items[0]
    assert item.id == 7
    assert item.category == "Non-Veg"
    assert item.available_toppings == ["Grilled Chicken", "BBQ Sauce"]


def test_seed_skips_when_database_already_populated(service, mock_repository, tmp_path):
    mock_repository.count.return_value = 3

    csv_file = tmp_path / "menu.csv"
    csv_file.write_text("name,category,available_bases,available_toppings,price\n")

    service.seed_from_file(str(csv_file))

    mock_repository.save_items.assert_not_called()


def test_seed_loads_items_from_csv_when_empty(service, mock_repository, tmp_path):
    mock_repository.count.return_value = 0

    csv_file = tmp_path / "menu.csv"
    csv_file.write_text(
        "name,category,available_bases,available_toppings,price\n"
        "Margherita,Classic,Thin Crust|Thick Crust,Mozzarella|Tomato,299.00\n"
        "Pepperoni,Non-Veg,Thin Crust,Pepperoni|Mozzarella,399.00\n"
    )

    service.seed_from_file(str(csv_file))

    mock_repository.save_items.assert_called_once()
    saved = mock_repository.save_items.call_args[0][0]
    assert len(saved) == 2
    assert saved[0].name == "Margherita"
    assert saved[0].available_bases == ["Thin Crust", "Thick Crust"]
    assert saved[1].name == "Pepperoni"
    assert saved[1].price == 399.0


def test_seed_parses_pipe_separated_bases_and_toppings(service, mock_repository, tmp_path):
    mock_repository.count.return_value = 0

    csv_file = tmp_path / "menu.csv"
    csv_file.write_text(
        "name,category,available_bases,available_toppings,price\n"
        "Farmhouse,Veg,Thin Crust|Thick Crust|Stuffed Crust,Corn|Capsicum|Onion,349.00\n"
    )

    service.seed_from_file(str(csv_file))

    saved = mock_repository.save_items.call_args[0][0]
    assert saved[0].available_bases == ["Thin Crust", "Thick Crust", "Stuffed Crust"]
    assert saved[0].available_toppings == ["Corn", "Capsicum", "Onion"]
