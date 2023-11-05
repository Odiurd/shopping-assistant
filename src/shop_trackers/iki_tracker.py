import json
import requests
import time

from lxml import html
from typing import Dict, Union

from .shop_tracker import ShopTracker


class IkiTracker(ShopTracker):
    def __init__(self):
        super().__init__("iki", "https://lastmile.lt/en/product/IKI/")

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
        script_elements = tree.xpath("//script")
        script_content = script_elements[
            -1
        ].text_content()  # product info is stored in the last block

        try:
            script_dict = json.loads(script_content)
        except json.JSONDecodeError as e:
            raise ValueError("Current price not found for ", item_url)

        product = script_dict["props"]["pageProps"]["product"]

        item_information = {
            "item_url": item_url,
            "shop_item_id": product["productId"],
            "shop_item_name": product["name"]["lt"],
            "base_price": product["prc"]["p"],
            "discounted_price": product["prc"]["l"],
        }

        return item_information
