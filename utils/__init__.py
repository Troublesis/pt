import os
import random
import subprocess
import time

import ffmpeg
import libtorrent as lt
import requests
from bs4 import BeautifulSoup
from qbittorrentapi import Client


def upload_torrent(torrent_path, save_path, category="保种"):
    print(f"...Adding torrent: {torrent_path} to: {save_path}")
    qbitapi().torrents_add(
        torrent_files=torrent_path,
        save_path=save_path,
        category=category,
        is_skip_checking=True,
        is_paused=False,
    )
    print(f"...Deleting: {torrent_path}")
    os.remove(torrent_path)
    print("All done.")


def qbitapi():
    """创建并返回 qBittorrent API 客户端实例。

    Args:
        host: qBittorrent Web API 的主机地址。
        username: qBittorrent Web API 的用户名。
        password: qBittorrent Web API 的密码。

    Returns:
        qBittorrent API 客户端实例。
    """
    host = "http://192.168.0.47:10063"
    username = "bamboo5320"
    password = "Blessed9."
    try:
        client = Client(host=host, username=username, password=password)
        print("Successfully login qbit.")
        return client
    except Exception as e:
        print(f"Error creating qBittorrent client: {e}")
        return None


def create_gif(video_name, start_time, duration=5):
    video_path = f"/volume3/Data2/HD/videos/3d/manual-sort/asia/FC2/{video_name}"
    output_name = f'{start_time.replace(":", "_")}.gif'

    # Convert duration to end time
    start_parts = list(map(int, start_time.split(":")))
    start_seconds = start_parts[0] * 3600 + start_parts[1] * 60 + start_parts[2]
    end_seconds = start_seconds + int(duration)
    end_hours = end_seconds // 3600
    end_minutes = (end_seconds % 3600) // 60
    end_seconds = end_seconds % 60
    end_time = f"{end_hours:02}:{end_minutes:02}:{end_seconds:02}"

    # ffmpeg command
    command = [
        "ffmpeg",
        "-ss",
        start_time,
        "-to",
        end_time,
        "-i",
        video_path,
        "-vf",
        "fps=10,scale=640:-1:flags=lanczos",
        output_name,
    ]

    # Execute the command
    subprocess.run(command, stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT)
    # subprocess.run(command, check=True)


def create_gifs():
    video_name = input("Enter video name: ")
    start_time_list = []
    while True:
        start_time = input("Enter start time (format HH:MM:SS) or 'y' to stop: ")
        if start_time.lower() == "y" or start_time == "":
            break
        start_time_list.append(start_time)

    for start_time in start_time_list:
        create_gif(video_name, start_time)


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


def random_time(time1=20, time2=30):
    # Generate a random number of seconds between 20 and 30
    wait_time = random.uniform(time1, time2)

    # Print the wait time (optional)
    print(f"Waiting for {wait_time:.2f} seconds...")

    # Wait for the generated time
    time.sleep(wait_time)

    # Print a message after waiting (optional)
    print("Wait is over!")


class ElementNotFoundException(Exception):
    pass


def pttime_search(id, str_limit=50):
    url = "https://www.pttime.org/adults.php"

    querystring = {"spstate": "0", "incldead": "1", "search": id, "search_area": "0"}

    headers = {
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Encoding": "gzip, deflate",
        "Cookie": "c_lang_folder=chs; c_secure_uid=MzIyMTA%3D; c_secure_pass=4a23757ed0d840f7cb5c143c9a7a7587; c_secure_ssl=eWVhaA%3D%3D; c_secure_tracker_ssl=eWVhaA%3D%3D; c_secure_login=bm9wZQ%3D%3D; cf_clearance=AFm9n2Jss.j8717JKAnElGZGSbp72eo5PacmM6PRA7E-1716086353-1.0.1.1-9YUdSYEysxSQJsImdvWc8jclXLia488EXckQtko0GyoB5XTYdViCS1pf_ywtIf_PJnLAs4wY2HpMIz1uTqywCA",
        "Connection": "keep-alive",
        "Sec-Fetch-Mode": "navigate",
        "Host": "www.pttime.org",
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36",
        "Sec-Fetch-Site": "same-origin",
        "Referer": "referer",
        "Sec-Fetch-Dest": "document",
        "Accept-Language": "zh-CN,zh-Hans;q=0.9",
    }

    response = requests.get(url, headers=headers, params=querystring)

    # Parse the HTML content
    soup = BeautifulSoup(
        response.content.decode("utf-8", errors="replace"), "html.parser"
    )

    # Find the first table with class "torrentname"
    torrent_table = soup.find("table", class_="torrentname")

    # If table found, get the text from the first row
    if torrent_table:
        first_torrent_row = torrent_table.find("tr")
        if first_torrent_row:
            first_torrent_text = first_torrent_row.get_text()
            # Check if str_limit is provided and return trimmed text accordingly
            return (
                first_torrent_text.strip()[:str_limit]
                if str_limit is not None
                else first_torrent_text.strip()
            )
        else:
            raise Exception("Something wrong!")
    else:
        # Selecting the element using the CSS selector
        element = soup.find("table", class_="mainouter mt5")
        if element:
            result = element.find("td", class_="text")
            # Getting the content of the selected element
            content = result.text.strip() if element else None
            if content == "没有种子。请用准确的关键字重试。":
                return None
            else:
                raise Exception(content)
        else:
            raise Exception("Something wrong!")


# print(pttime_search("ipx-580"))


def exoticaz_search(id):
    url = "https://exoticaz.to/torrents"

    querystring = {"search": id}

    headers = {
        # "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
        # "Accept-Encoding": "gzip, deflate, br, zstd",
        "Cookie": "cf_clearance=ucDLuP6WUDkB5Au3kQfnHSDhPwmWX4qIqJa4i8Vhcas-1715989505-1.0.1.1-y0OltdhGHeyiapRnBPmF67Pl73Il6IERl5CQNB1mKkx67TpSjgcHSCzXZUeXULNREgbxy5PvePd2lzPNa_WDqQ; remember_web_59ba36addc2b2f9401580f014c7f58ea4e30989d=eyJpdiI6IlRlUEJZQ0phK2RnbmNWSlF1aTVkcEE9PSIsInZhbHVlIjoiYXBtbllzVGFuV0dwQjBycFNRMmJZQnYyMGZHcjZDXC8rK1E1cWtmWDBvd1MyWER1K3JSTlpcL1FQcHRpVm9wS0phaHJcL3RwUFBQXC9rcFJLczZKTFVLTDh2ZERKcXRFdDR3ZGhuS0xBMjRjdUlRcjY1eDBpakE2UDd4VFhUdXVuVEJrZXYyMGY3NE1INzBYcm9pdXhFdmppcUE0OEpqQzhcL24rMFVzQ01JZUZtTjQ9IiwibWFjIjoiZjJjYTIxYTJhMDY2MzZlZDVhOTBjMWViYTU1MzA1ZDlmMDA2ZmY1YWM4MjkwZGI0NWVlMzkwMGNlMjNjZGI4ZiJ9; love=11290; XSRF-TOKEN=eyJpdiI6IjJVUnNaTXlGOG5aRU1KSlFqeTRvREE9PSIsInZhbHVlIjoiTmNPM1I1MFBpckQwSEwxQVR6eTh4cTdxWUJUZEdoalBpU2tHa0lYelVoQnh2T1JWZnMwMTlUQU9SRVwvZUJKclkiLCJtYWMiOiJhMjFhYTgyYzcxYzhlOGYyMjI2M2QzOWRjNDExMDUzYmI1YjJhNWM4OTNkZmYyNjk3MzlmNzFhMmJiOTdiYmY4In0%3D; exoticaz_session=eyJpdiI6IkVrbW1cL1VSK1R3Y3RLdlwvS040dTZ1QT09IiwidmFsdWUiOiJUV1wvbUZlaGxIb3hTZmdXXC9XKzBGTEF6MElSTkRyV3hRaUpkcUp5YTdoWjFrc3IxQSt3U0JJRVR5aUJUZUt2dFUiLCJtYWMiOiIzY2RlOTAwOWQzZTBmOTFiOTEyMDY2ODQ1OGU2MTJhYjFmZDlkN2JlMDA5N2FlZWFkYWQyZDIxOTk5MmFjMTEyIn0%3D",
        "Connection": "keep-alive",
        "Sec-Fetch-Mode": "navigate",
        "Host": "exoticaz.to",
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36",
        "Sec-Fetch-Site": "same-origin",
        "Referer": "https://exoticaz.to/torrents",
        "Sec-Fetch-Dest": "document",
        "Accept-Language": "zh,en;q=0.9",
        "Content-Type": "text/html; charset=UTF-8",
    }

    response = requests.get(url, headers=headers, params=querystring)
    # print(response.text)
    # Parse the HTML content
    soup = BeautifulSoup(
        response.content.decode("utf-8", errors="replace"), "html.parser"
    )
    span_element = soup.find("span", class_="badge badge-secondary")

    if span_element:
        if span_element != "0 torrents":

            span_element = soup.find("span", {"data-toggle": "tooltip"})

            # Check if the <span> element was found
            if span_element:
                # Find the <a> element directly following the <span> element
                a_element = span_element.find_next_sibling("a")

                # Check if the <a> element was found
                if (
                    a_element
                    and a_element.has_attr("href")
                    and a_element.has_attr("title")
                ):
                    href = a_element["href"]
                    title = a_element["title"]
                    print(f"{title}")
                    print(f"{href}")
                else:
                    print("No torrent info found")
            else:
                print("No torrent found")
        else:
            raise ElementNotFoundException("Element not found")
        random_time()


import os


def find_video_files(path):
    # Define a list of video file extensions
    video_extensions = [".mp4", ".avi", ".mkv", ".mov", ".flv", ".wmv", "m2ts"]

    # Initialize an empty list to hold the file names
    video_files = []

    # Walk through the directory
    for root, dirs, files in os.walk(path):
        for file in files:
            # Check if the file has a video extension
            if any(file.lower().endswith(ext) for ext in video_extensions):
                # Get the base name of the file without the extension
                file_name = os.path.splitext(file)[0]
                # Append the file name to the list
                video_files.append(file_name)

    return video_files


# # Example usage:
# video_files = find_video_files("/Volumes/Data2/HD/videos/3d/manual-sort/asia/FC2/")
# # print(video_files)
# for video in video_files:
#     print(video)
#     exoticaz_search(video)

if __name__ == "__main__":
    # create_private_torrent(
    #     "/volume3/Data2/HD/videos/3d/manual-sort/asia/FC2/1218225509.M2TS",
    #     "1218225509.torrent",
    # )
    upload_torrent(
        torrent_path="[exoticaz.to] fc2.ppv.1218225509.compeletly.naked.doing.a.blowjob.inside.operation.room.torrent",
        save_path="/volume3/Data2/HD/videos/3d/manual-sort/asia/FC2/",
    )
    pass
