import os
from pathlib import Path

from sqlalchemy import create_engine, text

DATABASE_URL = os.environ["DATABASE_URL"]
ROOT = Path(__file__).resolve().parents[1]

FILES = [
    ("pizza", ROOT / "menu" / "Types_of_Pizza.txt"),
    ("base", ROOT / "menu" / "Types_of_Base.txt"),
    ("topping", ROOT / "menu" / "Types_of_Toppings.txt"),
]

engine = create_engine(DATABASE_URL)


def main():
    with engine.begin() as conn:
        for category, file_path in FILES:
            for line in file_path.read_text(encoding="utf-8").splitlines():
                if not line.strip():
                    continue

                item_id, name, price = line.split(";")

                conn.execute(
                    text("""
                        insert into menu_items
                        (id, category, name, price, is_available)
                        values
                        (:id, :category, :name, :price, true)
                        on conflict (id) do update set
                            category = excluded.category,
                            name = excluded.name,
                            price = excluded.price,
                            is_available = true;
                    """),
                    {
                        "id": item_id.strip(),
                        "category": category,
                        "name": name.strip(),
                        "price": float(price.strip()),
                    },
                )


if __name__ == "__main__":
    main()
