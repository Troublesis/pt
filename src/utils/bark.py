from urllib.parse import quote_plus

import requests

from config.config import settings
from logger import logger


class Bark:
    """
    A class to send notifications using the Bark service.
    """

    def __init__(self, group: str):
        """
        Initializes the Bark with API key, URL, and group from the configuration.

        Args:
            group (str): The group for the notifications.
        """
        self.group = group

    def send(
        self,
        title: str,
        body: str,
        url: str,
        sound: str = "birdsong",
        icon_url: str = None,
        level: str = "active",
        is_archive: int = 1,
    ):
        """
        Send a notification using the Bark service.

        Args:
            title (str): The title of the notification.
            body (str): The body content of the notification.
            url (str): The URL to open when the notification is tapped.
            sound (str): The sound to play with the notification.
            icon_url (str): The URL of the icon to display with the notification.
            level (str): The urgency level of the notification.
            is_archive (int): Whether to archive the notification (1 for yes, 0 for no).

        Returns:
            bool: True if the notification was sent successfully, False otherwise.
        """
        # Ensure parameters are strings
        title = str(title)
        body = str(body)
        url = str(url)
        sound = str(sound)
        icon_url = str(icon_url)
        level = str(level)
        is_archive = str(is_archive)

        # URL encode the parameters
        encoded_params = {
            "group": quote_plus(self.group),
            "title": quote_plus(title),
            "body": quote_plus(body),
            "url": quote_plus(url),
            "icon": quote_plus(icon_url),
        }
        # log.debug(encoded_params)

        # Construct the full URL for the Bark API request
        full_url = (
            f'{settings.from_env("bark").url}/{settings.from_env("bark").api}/{encoded_params["body"]}?'
            f"url={encoded_params['url']}&icon={encoded_params['icon']}&"
            f"sound={sound}&group={encoded_params['group']}&"
            f"title={encoded_params['title']}&badge=1&level={level}&"
            f"isArchive={is_archive}"
        )

        try:
            # Send the GET request to the Bark API
            response = requests.get(full_url)
            response.raise_for_status()  # Raises an HTTPError for bad responses
            logger.info(f"Message sent to Bark successfully!")
            return True
        except requests.RequestException as e:
            logger.error(f"Failed to send message to Bark: {e}")
            return False


if __name__ == "__main__":
    bark = Bark("test")
    bark.send(
        title="Test", body="This is a test notification.", url="https://www.google.com"
    )
