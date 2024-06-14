import os
import time

import ffmpeg
import libtorrent as lt
import requests


def get_video_path_by_name(video_name):
    """
    Searches for a video by name using the Emby API and returns the complete name and path of the video file.

    Parameters:
    video_name (str): The name of the video to search for.

    Returns:
    str: The complete path of the video file if found, else None.
    """

    # Emby server URL and endpoint for searching items
    url = "http://192.168.0.47:10074/emby/Items"

    # Parameters for the API request
    querystring = {
        "Recursive": "true",
        "IncludeItemTypes": "episodes",  # Searching for episodes, can be changed if needed
        "api_key": "d789b96a1319452abb1e150b709fc3d6",
        "Fields": "Path",
        "SearchTerm": video_name,
    }

    # Making the API request
    response = requests.get(url, params=querystring)

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
            print(f"EMBY Video Name: {video_name}")
            print(video_path)
            return video_path
        else:
            print("No items found for the search term.")
            return None
    else:
        # Handling the case where the API request failed
        print(
            f"Error: Unable to fetch data from Emby API. Status code: {response.status_code}"
        )
        return None


def timing_decorator(func):
    def wrapper(video_path, torrent_path, *args, **kwargs):
        print(f"...Generating torrent: {video_path}")
        start_time = time.time()
        result = func(video_path, torrent_path, *args, **kwargs)
        end_time = time.time()
        elapsed_time = end_time - start_time

        # Convert elapsed time to hours, minutes, and seconds
        hours, rem = divmod(elapsed_time, 3600)
        minutes, seconds = divmod(rem, 60)
        if hours > 0:
            time_str = (
                f"{int(hours)} hours, {int(minutes)} minutes, and {seconds:.2f} seconds"
            )
        elif minutes > 0:
            time_str = f"{int(minutes)} minutes and {seconds:.2f} seconds"
        else:
            time_str = f"{seconds:.2f} seconds"

        print(f"Time taken for {video_path}: {time_str}")
        return result

    return wrapper


@timing_decorator
def create_private_torrent(
    file_path, torrent_path, tracker_url="https://tracker.exoticaz.to/announce"
):
    fs = lt.file_storage()
    lt.add_files(fs, file_path)

    t = lt.create_torrent(fs, flags=lt.create_torrent.v1_only)
    t.add_tracker(tracker_url)

    # 设置种子为私有种子
    t.set_priv(True)

    lt.set_piece_hashes(t, os.path.dirname(file_path))
    torrent_file = t.generate()

    with open(torrent_path, "wb") as f:
        f.write(lt.bencode(torrent_file))

    print(f"Private torrent created: {torrent_path}")


def confirm_torrent_name(video_name):
    """
    Ask the user to confirm or manually enter the desired torrent name.

    Parameters:
    video_name (str): The base name of the video to generate the torrent name.

    Returns:
    str: The confirmed or manually entered torrent name.
    """
    torrent_name = f"{video_name}.torrent"
    confirm = input(
        f"Confirm if you want the torrent name as (y/manual): {torrent_name}\n"
    )

    if confirm == "y" or confirm == "":
        return torrent_name
    else:
        # Recursively call the function to get manual input until a valid name is provided
        return confirm_torrent_name(confirm)


def generate_screenshots(video_path, torrent_dir, num_screenshots=4):
    # Get video duration
    probe = ffmpeg.probe(video_path)
    duration = float(probe["format"]["duration"])

    # Calculate timestamps for evenly spaced frames
    timestamps = [
        round(duration * i / (num_screenshots + 1), 2)
        for i in range(1, num_screenshots + 1)
    ]

    # Generate screenshots
    for i, timestamp in enumerate(timestamps):
        ffmpeg.input(video_path, ss=timestamp).output(
            os.path.join(torrent_dir, f"frame_%d.png"), vframes=1, qscale=2
        ).run()


def google_search(query, torrent_dir):
    api_key = (
        "AIzaSyD_3n4Ema5ISdHieqyCIANCmaMbBq4W7BI"  # Replace with your Google API key
    )
    cx = "c473c96408c114f41"  # Replace with your Custom Search Engine ID (cx)
    url = f"https://www.googleapis.com/customsearch/v1?q={query}&cx={cx}&key={api_key}&safe=off"

    try:
        response = requests.get(url)
        response.raise_for_status()  # Raise an exception for bad status codes
        results = response.json()
        if results:
            search_result_path = os.path.join(torrent_dir, "output.txt")
            with open(search_result_path, "w") as file:
                for item in results.get("items", [])[:4]:
                    file.write(item.get("title"))
                    file.write(item.get("link"))
    except requests.exceptions.RequestException as e:
        print("Error fetching results:", e)
        return None


def main():
    # Example usage
    data = [
        "FC2-1035997",
        "FC2-1040032",
        "FC2-1040038",
        "FC2-1040158",
        "FC2-1050737",
        "FC2-1073663",
        "FC2-1083921",
        "FC2-1090559",
        "FC2-1097870",
        "FC2-1108030",
        "FC2-1110408",
        "FC2-1119209",
        "FC2-1131537",
        "FC2-1343386",
        "FC2-389339",
        "FC2-683577",
        "FC2-687368",
        "FC2-692522",
        "FC2-761819",
        "FC2-762165",
        "FC2-792132",
        "FC2-794563",
        "FC2-797221",
        "FC2-805782",
        "FC2-817156",
        "FC2-834923",
        "FC2-855043",
        "FC2-996935",
        "FC2PPV-930703",
    ]
    for video_name in data:
        # video_name = input("Enter video name: ")
        video_path = get_video_path_by_name(video_name)
        if video_path:
            # torrent_name = confirm_torrent_name(video_name)
            torrent_name = video_name
            torrent_dir = os.path.join("./torrents", video_name)
            os.makedirs(torrent_dir, exist_ok=True)
            torrent_path = os.path.join(torrent_dir, f"{torrent_name}.torrent")
            create_private_torrent(video_path, torrent_path)
            generate_screenshots(video_path, torrent_dir)
            google_search(video_name, torrent_dir)


if __name__ == "__main__":
    main()
