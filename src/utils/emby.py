import requests

from config.config import settings
from logger import logger


class Emby:
    """
    A class for interacting with the Emby API.
    """

    def __init__(self):
        """
        Initializes the Emby class.
        """
        pass

    def get_video_path_by_name(self, video_name):
        """
        Searches for a video by name using the Emby API and returns the complete name and path of the video file.

        Parameters:
        video_name (str): The name of the video to search for.

        Returns:
        str: The complete path of the video file if found, else None.
        """

        # Emby server URL and endpoint for searching items
        endpoint = f"{settings.from_env('emby').url}/emby/Items"

        # Parameters for the API request
        querystring = {
            "Recursive": "true",
            "IncludeItemTypes": "episodes",  # Searching for episodes, can be changed if needed
            "api_key": settings.EMBY_API,
            "Fields": "Path",
            "SearchTerm": video_name,
        }

        # Making the API request
        response = requests.get(endpoint, params=querystring)

        # Checking if the request was successful
        if response.status_code == 200:
            # Parsing the JSON response
            data = response.json()

            # Checking if the response contains items
            if "Items" in data and len(data["Items"]) > 0:
                # print(data)
                result = data["Items"][0]
                video_name = result["Name"]
                video_path = result["Path"]
                logger.info(f"EMBY Video Name: {video_name}")
                # print(video_path)
                return video_path
            else:
                logger.warning("No items found for the search term.")
                return None
        else:
            # Handling the case where the API request failed
            logger.error(
                f"Error: Unable to fetch data from Emby API. Status code: {response.status_code}"
            )
            return None


if __name__ == "__main__":
    emby = Emby()
    print(emby.get_video_path_by_name("ipx-580"))
