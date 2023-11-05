import yaml

from mailjet_rest import Client
from settings.config import EMAIL_SENDER_NAME
from typing import Dict, List, Union

from jinja2 import Environment, FileSystemLoader, Template
from settings.config import (
    EMAIL_TEMPLATE_FOLDER,
    EMAIL_TEMPLATE,
)


class EmailNotifier:
    def __init__(self):
        # TODO: consider replacing with env variables
        with open("settings/keys.yaml", "r") as config_file:
            config = yaml.safe_load(config_file)

        self.client = Client(
            auth=(config.get("MAILJET_API_KEY"), config.get("MAILJET_API_SECRET")),
            version="v3.1",
        )  # https://www.mailjet.com/

    @staticmethod
    def group_items_by_shop(
        discounted_items_dict: Dict[str, Union[str, float]]
    ) -> Dict[str, List[Dict[str, Union[str, float]]]]:
        grouped_items = {}
        for item in discounted_items_dict:
            shop_name = item["shop_name"]
            if shop_name not in grouped_items:
                grouped_items[shop_name] = []
            grouped_items[shop_name].append(item)

        return grouped_items

    def build_plain_text_email_content(
        self, discounted_items_dict: Dict[str, Union[str, float]]
    ) -> str:
        grouped_items = self.group_items_by_shop(discounted_items_dict)

        # loop through items and build message to send
        message = ""
        for shop_name, items in grouped_items.items():
            message += f"== {shop_name.upper()} ==\n"

            sorted_items = sorted(items, key=lambda x: x["item_name"])
            for item in sorted_items:
                item_name = item["item_name"]
                base_price = "{:.2f}".format(item["base_price"])
                discounted_price = "{:.2f}".format(item["discounted_price"])
                item_url = item["item_url"]
                # update_timestamp = item["update_timestamp"]

                message += f"\t{item_name}\n"
                message += f"\t\t* {base_price}€ --> {discounted_price}€\n"
                message += f"\t\t* {item_url}\n"

        return message

    def build_html_email_content(
        self, discounted_items_dict: Dict[str, Union[str, float]]
    ) -> Template:
        grouped_items = self.group_items_by_shop(discounted_items_dict)

        env = Environment(loader=FileSystemLoader(EMAIL_TEMPLATE_FOLDER))
        template = env.get_template(EMAIL_TEMPLATE)

        return template.render(grouped_items=grouped_items)

    def build_email_content(
        self, email_style: str, discounted_items_dict: Dict[str, Union[str, float]]
    ) -> str:
        if email_style == "text":
            email_content = self.build_plain_text_email_content(discounted_items_dict)
        elif email_style == "html":
            email_content = self.build_html_email_content(discounted_items_dict)
        else:
            raise ValueError("EMAIL_STYLE in config.py must be 'text' or 'html'.")

        return email_content

    def send_email(
        self,
        from_email: str,
        to_email: str,
        subject: str,
        content: str,
        content_type: str = "text",
    ):
        data = {
            "Messages": [
                {
                    "From": {"Email": from_email, "Name": EMAIL_SENDER_NAME},
                    "To": [{"Email": to_email}],
                    "Subject": subject,
                    "TextPart": content,
                }
            ]
        }

        if content_type == "text":
            data["Messages"][0]["TextPart"] = content
        elif content_type == "html":
            data["Messages"][0]["HTMLPart"] = content
        else:
            raise ValueError("content_type must be TextPart or HTMLPart.")

        try:
            response = self.client.send.create(data=data)
            if response.status_code != 200:
                print(f"Something went wrong, status code: {response.status_code}")
                print(f"{response.json()}")
        except Exception as e:
            print(f"Error sending email: {e}")
