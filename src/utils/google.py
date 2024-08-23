import os

import requests

from config.config import settings
from logger import logger


# Define a filter function for specific logs
def google_log(record):
    # Example condition: Save logs with 'specific' keyword to a separate log file
    return "[google]" in record["message"]


google_format = "<green>{time:YYYY-MM-DD HH:mm:ss}</green> {message}"
logger.add(
    "logs/google.log", filter=google_log, rotation="100 MB", format=google_format
)


# https://developers.google.com/custom-search/v1/introduction
def google_search(query):
    """
    Perform a search using Google Custom Search API and save the results to a local file.

    Args:
        query (str): The search query to perform.

    Returns:
        bool or None: Returns True if the search is successful and results are saved to the local file,
                      otherwise returns None if an error occurs.

    Raises:
        No explicit exceptions are raised, but errors during the request or JSON processing are
        caught and printed to the console.

    Note:
        This function requires a valid Google API key and a Custom Search Engine ID (cx) to be
        configured in the settings.
    """
    api_key = settings.from_env("google").api  # Replace with your Google API key
    cx = settings.from_env(
        "google"
    ).search_engine_id  # Replace with your Custom Search Engine ID (cx)
    url = f"https://www.googleapis.com/customsearch/v1?q={query}&cx={cx}&key={api_key}&safe=off"

    try:
        response = requests.get(url)
        response.raise_for_status()  # Raise an exception for bad status codes
        results = response.json()
        if results:
            for item in results.get("items", [])[:4]:
                title = f'[google] {item.get("title")}'
                link = f'[google] {item.get("link")}'
                logger.info(title)
                logger.info(link)
            return True
    except requests.exceptions.RequestException as e:
        logger.error("Error fetching results:", e)
        return None


if __name__ == "__main__":
    google_search("python")
