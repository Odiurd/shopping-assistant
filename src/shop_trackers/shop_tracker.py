from abc import ABC, abstractmethod
from typing import Dict, Union


class ShopTracker(ABC):
    def __init__(self, shop_name: str, base_url: str):
        self.shop_name = shop_name
        self.base_url = base_url

    @abstractmethod
    def extract_item_information(self) -> Dict[str, Union[float, str]]:
        pass

    @staticmethod
    def extract_mock_item_information(
        base_url: str, item_url_suffix: str
    ) -> Dict[str, Union[float, str]]:
        item_information = {
            "item_url": base_url + item_url_suffix,
            "shop_item_id": "000000000001234567",
            "shop_item_name": "A product name, 150g",
            "base_price": 10.00,
            "discounted_price": 9.50,
        }
        return item_information

    @staticmethod
    def get_custom_headers_if_available() -> Dict[str, str]:
        try:
            from ..settings.personal_config import CUSTOM_HEADERS
        except ImportError:
            CUSTOM_HEADERS = None  # noqa

        return CUSTOM_HEADERS
