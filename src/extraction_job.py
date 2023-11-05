from datetime import datetime
import csv

from settings.config import DATABASE_FILE, ITEMS_TO_TRACK_FILE
from database.database_manager import DatabaseManager
from shop_trackers.barbora_tracker import BarboraTracker
from shop_trackers.iki_tracker import IkiTracker

DEBUG_MODE = False

if __name__ == "__main__":
    # initialize items
    with open(ITEMS_TO_TRACK_FILE, newline="") as tsvfile:
        items_to_track = list(csv.DictReader(tsvfile, delimiter="\t"))

    print(
        f"{datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')} - Found {len(items_to_track)} items to track"
    )

    # initialize shop assistants
    shop_trackers = [BarboraTracker(), IkiTracker()]

    # initialize db
    db_manager = DatabaseManager(DATABASE_FILE)
    db_manager.initialize_database()

    # process items one shop at a time
    for item_to_track in items_to_track:
        for shop_tracker in shop_trackers:
            item_url_suffix_shop = item_to_track[
                f"item_url_suffix_{shop_tracker.shop_name}"
            ]

            if item_url_suffix_shop is None or item_url_suffix_shop == "":
                # item does not exist in this shop
                continue

            if DEBUG_MODE:
                item_info = shop_tracker.extract_mock_item_information(
                    base_url=shop_tracker.base_url,
                    item_url_suffix=item_url_suffix_shop,
                )
            else:
                # TODO: add error handling
                item_info = shop_tracker.extract_item_information(
                    item_url_suffix=item_url_suffix_shop
                )

            db_manager.insert_item_information(
                item_name=item_to_track["item_name"],
                shop_name=shop_tracker.shop_name,
                item_url=item_info["item_url"],
                shop_item_id=item_info["shop_item_id"],
                shop_item_name=item_info["shop_item_name"],
                base_price=item_info["base_price"],
                discounted_price=item_info["discounted_price"],
            )

    db_manager.close_connection()
    print(
        f"{datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')} - item data saved correctly"
    )
