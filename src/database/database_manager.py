import datetime
import sqlite3

from typing import Any, Dict, Optional, List, Tuple


class DatabaseManager:
    def __init__(self, database_name: str):
        self.database_name = database_name
        self.conn = None
        self.cursor = None
        self.connect_database()

    def connect_database(self):
        self.conn = sqlite3.connect(self.database_name)
        self.cursor = self.conn.cursor()

    def initialize_database(self):
        self.cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS Items (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL
            )
        """
        )

        self.cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS ItemURLs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                item_id INTEGER,
                item_url TEXT NOT NULL,
                shop_name TEXT NOT NULL,
                FOREIGN KEY (item_id) REFERENCES Items (id)
            )
        """
        )

        self.cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS ShopDetails (
                item_id INTEGER,
                item_url_id INTEGER,
                update_timestamp TEXT NOT NULL,
                shop_item_id TEXT NOT NULL,
                shop_item_name TEXT,
                base_price REAL,
                discounted_price REAL,
                PRIMARY KEY (item_id, item_url_id, update_timestamp),
                FOREIGN KEY (item_id) REFERENCES Items (id),
                FOREIGN KEY (item_url_id) REFERENCES ItemURLs (id)
            )
        """
        )

        self.conn.commit()

    def close_connection(self):
        self.conn.close()

    def get_item_id_and_url_id(
        self, item_name: str, item_url: str, shop_name: str
    ) -> Optional[Tuple[int, int]]:
        self.cursor.execute(
            """
            SELECT Items.id AS item_id, ItemURLs.id AS item_url_id
            FROM Items
            LEFT JOIN ItemURLs
            ON Items.id = ItemURLs.item_id
            WHERE Items.name = ? AND ItemURLs.item_url = ? AND shop_name = ?
        """,
            (item_name, item_url, shop_name),
        )

        return self.cursor.fetchone()

    def insert_item(self, item_name: str, item_url: str, shop_name: str):
        self.cursor.execute("SELECT id FROM Items WHERE name = ?", (item_name,))
        existing_item = self.cursor.fetchone()

        if existing_item:
            item_id = existing_item[0]
            # print(f"Item `{item_name}` already exists with item_id: {item_id}")
        else:
            self.cursor.execute("INSERT INTO Items (name) VALUES (?)", (item_name,))
            item_id = self.cursor.lastrowid
            print(f"Inserted item_id: {item_id}")

        self.cursor.execute(
            "INSERT INTO ItemURLs (item_id, item_url, shop_name) VALUES (?, ?, ?)",
            (item_id, item_url, shop_name),
        )
        item_url_id = self.cursor.lastrowid
        print(f"Inserted item_url_id: {item_url_id}")

        self.conn.commit()

    def insert_item_information(
        self,
        item_name: str,
        shop_name: str,
        item_url: str,
        shop_item_id: str,
        shop_item_name: str,
        base_price: float,
        discounted_price: float,
    ):
        # if available, get item_id and item_url_id based on item_name, item_url and shop_name
        result = self.get_item_id_and_url_id(
            item_name=item_name, item_url=item_url, shop_name=shop_name
        )
        if result:
            item_id, item_url_id = result
        else:
            # add item to DB since it does not exist yet
            self.insert_item(
                item_name=item_name, item_url=item_url, shop_name=shop_name
            )

            # now item_id and item_url_id are ready
            item_id, item_url_id = self.get_item_id_and_url_id(
                item_name=item_name, item_url=item_url, shop_name=shop_name
            )

        # update table with details
        update_timestamp = (
            datetime.datetime.utcnow().replace(tzinfo=datetime.timezone.utc).isoformat()
        )
        self.cursor.execute(
            """
            INSERT INTO ShopDetails (
            item_id, item_url_id, update_timestamp, shop_item_id, shop_item_name, base_price, discounted_price
            )
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """,
            (
                item_id,
                item_url_id,
                update_timestamp,
                shop_item_id,
                shop_item_name,
                base_price,
                discounted_price,
            ),
        )

        self.conn.commit()

        # print("Inserted a new record with item information.")

    def get_discounted_items_today(self) -> List[Dict[str, Any]]:
        discounted_items = []

        self.cursor.execute(
            """
            SELECT
             name,
             base_price,
             discounted_price,
             shop_name,
             item_url,
             update_timestamp
            FROM (
                SELECT 
                    I.name,
                    SD.base_price,
                    SD.discounted_price,
                    IU.shop_name,
                    IU.item_url,
                    update_timestamp,
                    ROW_NUMBER() OVER (PARTITION BY IU.id ORDER BY SD.update_timestamp DESC) AS rn
                FROM ShopDetails SD
                INNER JOIN ItemURLs IU
                 ON SD.item_url_id = IU.id
                INNER JOIN Items I
                 ON SD.item_id = I.id
                WHERE discounted_price < base_price
                 AND SD.update_timestamp >= strftime('%Y-%m-%dT00:00:00.000000+00:00', 'now', 'utc')
            ) T1
            WHERE T1.rn = 1
        """
        )

        for row in self.cursor.fetchall():
            (
                item_name,
                base_price,
                discounted_price,
                shop_name,
                item_url,
                update_timestamp,
            ) = row

            discounted_items.append(
                {
                    "item_name": item_name,
                    "base_price": base_price,
                    "discounted_price": discounted_price,
                    "shop_name": shop_name,
                    "item_url": item_url,
                    "update_timestamp": update_timestamp,
                }
            )

        return discounted_items
