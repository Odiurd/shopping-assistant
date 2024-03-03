import json
import requests
import time

from lxml import html
from typing import Dict, Union

from .shop_tracker import ShopTracker


class BarboraTracker(ShopTracker):
    def __init__(self):
        super().__init__("barbora", "https://barbora.lt/produktai/")

    def extract_item_information(
        self, item_url_suffix: str
    ) -> Dict[str, Union[float, str]]:
        time.sleep(1)  # slow down requests
        item_url = self.base_url + item_url_suffix
        response = requests.get(
            item_url, headers=self.get_custom_headers_if_available()
        )
        response.raise_for_status()  # raise exception if not 200
        tree = html.fromstring(response.text)

        # TODO: if class="b-product-prices-block--loyalty" is present, requires promotion card

        data = json.loads(
            tree.xpath(
                "//div[@class='b-product-info b-product--js-hook']/@data-b-units"
            )[0]
        )
        price = data["units"][0]["price"]
        retail_price = data["units"][0].get("retail_price", None)
        if retail_price:
            # there is a discount -> crossed out number if the full price
            discounted_price = price
            base_price = retail_price
        else:
            # there is not a discount -> current price is the full price
            discounted_price = None
            base_price = price

        # extract ID
        item_id_element = tree.xpath(
            "//div[@class='b-product-info b-product--js-hook']/@data-b-item-id"
        )
        if not item_id_element:
            raise ValueError("Cannot find item ID")
        shop_item_id = item_id_element[0]

        # extract item name
        item_name_element = tree.xpath(
            "//h1[@class='b-product-info--title'][@itemprop='name']"
        )

        if not item_name_element:
            raise ValueError("Cannot find item name")

        shop_item_name = item_name_element[0].text.strip()

        item_information = {
            "item_url": item_url,
            "shop_item_id": shop_item_id,
            "shop_item_name": shop_item_name,
            "base_price": base_price,
            "discounted_price": discounted_price,
        }

        return item_information
