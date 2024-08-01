import math
import os
import random
import re
import subprocess
import time
from multiprocessing import Pool

import ffmpeg
import libtorrent as lt
import requests
from bs4 import BeautifulSoup
from PIL import Image, ImageDraw, ImageFont
from pymediainfo import MediaInfo
from qbittorrentapi import Client

# Define a list of video file extensions
global video_extensions
video_extensions = [".mp4", ".avi", ".mkv", ".mov", ".flv", ".wmv", "m2ts"]


def auto_convert_memory(bits):
    units = ["b", "Kb", "Mib", "Gib", "TB", "PB"]
    unit_index = 0
    while bits >= 1024 and unit_index < len(units) - 1:
        bits /= 1024.0
        unit_index += 1
    return f"{bits:.1f} {units[unit_index]}"


def auto_convert_duration(milliseconds):
    seconds = milliseconds / 1000
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    seconds = int(seconds % 60)
    duration_str = ""
    if hours > 0:
        duration_str += f"{hours} h "
    if minutes > 0:
        duration_str += f"{minutes} min "
    if seconds > 0 or (hours == 0 and minutes == 0):
        duration_str += f"{seconds} s"
    return duration_str.strip()


def auto_convert_bitrate(bitrate):
    units = ["b/s", "kb/s", "Mb/s", "Gb/s", "Tb/s", "Pb/s"]
    unit_index = 0
    while bitrate >= 1024 and unit_index < len(units) - 1:
        bitrate /= 1024.0
        unit_index += 1
    return f"{bitrate:.1f} {units[unit_index]}"


def convert_aspect_ratio(decimal_ratio):
    # Find the closest integer ratio
    tolerance = 0.01
    closest_ratio = None
    for i in range(1, 20):  # Assuming a maximum ratio of 20
        for j in range(1, 20):
            if abs(float(decimal_ratio) - (i / j)) < tolerance:
                closest_ratio = f"{i}:{j}"
                break
        if closest_ratio:
            break
    return closest_ratio if closest_ratio else decimal_ratio


def auto_convert_memory(bits):
    units = ["b", "Kb", "Mib", "Gib", "TB", "PB"]
    unit_index = 0
    while bits >= 1024 and unit_index < len(units) - 1:
        bits /= 1024.0
        unit_index += 1
    return f"{bits:.1f} {units[unit_index]}"


def auto_convert_duration(milliseconds):
    seconds = milliseconds / 1000
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    seconds = int(seconds % 60)
    duration_str = ""
    if hours > 0:
        duration_str += f"{hours} h "
    if minutes > 0:
        duration_str += f"{minutes} min "
    if seconds > 0 or (hours == 0 and minutes == 0):
        duration_str += f"{seconds} s"
    return duration_str.strip()


def auto_convert_bitrate(bitrate):
    units = ["b/s", "kb/s", "Mb/s", "Gb/s", "Tb/s", "Pb/s"]
    unit_index = 0
    while bitrate >= 1024 and unit_index < len(units) - 1:
        bitrate /= 1024.0
        unit_index += 1
    return f"{bitrate:.1f} {units[unit_index]}"


def convert_aspect_ratio(decimal_ratio):
    # Find the closest integer ratio
    tolerance = 0.01
    closest_ratio = None
    for i in range(1, 20):  # Assuming a maximum ratio of 20
        for j in range(1, 20):
            if abs(float(decimal_ratio) - (i / j)) < tolerance:
                closest_ratio = f"{i}:{j}"
                break
        if closest_ratio:
            break
    return closest_ratio if closest_ratio else decimal_ratio


def generate_media_info_string(file_path):
    media_info = MediaInfo.parse(file_path)
    info_string = ""

    for track in media_info.tracks:
        if track.track_type == "General":
            info_string += f"General\n"
            info_string += f"Complete name                  : {track.file_name}\n"
            info_string += f"Format                         : {track.format}\n"
            info_string += f"Format profile                 : {track.format_profile}\n"
            info_string += f"Codec ID                       : {track.codec_id}\n"
            info_string += f"File size                      : {auto_convert_memory(track.file_size)}\n"
            info_string += f"Duration                       : {auto_convert_duration(track.duration)}\n"
            info_string += f"Overall bit rate               : {auto_convert_bitrate(track.overall_bit_rate)}\n"
            info_string += f"Frame rate                     : {track.frame_rate} FPS\n"
            info_string += (
                f"Writing application            : {track.writing_application}\n"
            )
            info_string += "\n"

        elif track.track_type == "Video":
            info_string += f"Video\n"
            info_string += (
                f"ID                             : {track.stream_identifier}\n"
            )
            info_string += f"Format                         : {track.format}\n"
            info_string += f"Format/Info                    : {track.format_info}\n"
            info_string += f"Format profile                 : {track.format_profile}\n"
            info_string += f"Format settings                : {track.format_settings}\n"
            info_string += (
                f"Format settings, CABAC         : {track.format_settings_cabac}\n"
            )
            info_string += f"Format settings, Reference fra : {track.format_settings_reference_frames}\n"
            info_string += f"Codec ID                       : {track.codec_id}\n"
            info_string += f"Codec ID/Info                  : {track.codec_id_info}\n"
            info_string += f"Duration                       : {auto_convert_duration(track.duration)}\n"
            info_string += f"Bit rate                       : {auto_convert_bitrate(track.bit_rate)}\n"
            info_string += f"Width                          : {track.width} pixels\n"
            info_string += f"Height                         : {track.height} pixels\n"
            info_string += f"Display aspect ratio           : {convert_aspect_ratio(track.display_aspect_ratio)}\n"
            info_string += f"Frame rate mode                : {track.frame_rate_mode}\n"
            info_string += f"Frame rate                     : {track.frame_rate} FPS\n"
            info_string += f"Color space                    : {track.color_space}\n"
            info_string += (
                f"Chroma subsampling             : {track.chroma_subsampling}\n"
            )
            info_string += f"Bit depth                      : {track.bit_depth} bits\n"
            info_string += f"Scan type                      : {track.scan_type}\n"
            info_string += f"Bits/(Pixel*Frame)             : {track.bits_pixel}\n"
            info_string += f"Stream size                    : {auto_convert_memory(track.stream_size)}\n"
            info_string += f"Writing library                : {track.writing_library}\n"
            info_string += (
                f"Encoding settings              : {track.encoding_settings}\n"
            )
            info_string += f"Language                       : {track.language}\n"
            info_string += (
                f"Codec configuration box        : {track.codec_configuration_box}\n"
            )
            info_string += "\n"

        elif track.track_type == "Audio":
            info_string += f"Audio\n"
            info_string += (
                f"ID                             : {track.stream_identifier}\n"
            )
            info_string += f"Format                         : {track.format}\n"
            info_string += f"Format/Info                    : {track.format_info}\n"
            info_string += f"Codec ID                       : {track.codec_id}\n"
            info_string += f"Duration                       : {track.duration_string}\n"
            info_string += f"Bit rate mode                  : {track.bit_rate_mode}\n"
            info_string += f"Bit rate                       : {auto_convert_bitrate(track.bit_rate)}\n"
            info_string += (
                f"Channel(s)                     : {track.channel_s} channels\n"
            )
            info_string += f"Channel layout                 : {track.channel_layout}\n"
            info_string += f"Sampling rate                  : {track.sampling_rate}\n"
            info_string += f"Frame rate                     : {track.frame_rate} FPS\n"
            info_string += (
                f"Compression mode               : {track.compression_mode}\n"
            )
            info_string += f"Stream size                    : {auto_convert_memory(track.stream_size)}\n"
            info_string += f"Language                       : {track.language}\n"
            info_string += f"Default                        : {track.default}\n"
            info_string += f"Alternate group                : {track.alternate_group}\n"
            info_string += "\n"

    return info_string


def upload_torrent(torrent_path, save_path, category="保种"):
    # 打印正在添加的torrent信息
    print(f"...Adding torrent: {torrent_path} to: {save_path}")

    # 尝试获取qBittorrent API 客户端实例
    client = qbitapi()
    if client is None:
        print("Failed to connect to qBittorrent API. Skipping torrent upload.")
        return

    try:
        # 调用qbitapi().torrents_add方法添加torrent
        client.torrents_add(
            # 设置torrent文件路径
            torrent_files=torrent_path,
            # 设置保存路径
            save_path=save_path,
            # 设置分类
            category=category,
            # 跳过校验
            is_skip_checking=True,
            # 不停止torrent
            is_stopped=False,
            is_paused=False,
        )
        # 打印正在删除的torrent文件路径
        # print(f"...Deleting: {torrent_path}")
        # 尝试删除torrent文件
        # os.remove(torrent_path)
    except Exception as e:
        # 捕获所有异常并打印
        print(f"Error adding or deleting torrent: {e}")
    else:
        # 打印完成信息
        print("All done.")


def qbitapi():
    """创建并返回 qBittorrent API 客户端实例。

    Returns:
        qBittorrent API 客户端实例或None。
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


def generate_gif(video_path, start_time, duration=5):
    """
    ffmpeg -ss 00:00:00 -to 00:00:05 -i "/volume3/Data2/HD/videos/3d/manual-sort/asia/合集/兔崽baby/V/闺蜜太坏了！明明知道我快忍不住了还加大档位！一没忍住就把跳蛋给喷出来惹，顺带的把丝袜都喷湿了，只能趁没人发现赶紧回家了🥺.mp4" -vf "fps=10,scale=512:-1:flags=lanczos" ./torrents/1.gif
    """
    video_path = video_path.replace("X:/", "/volume3/Data2/")
    output_name = f'{start_time.replace(":", "_")}.gif'
    if start_time == "":
        start_time = "00:00:00"
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
        generate_gif(video_name, start_time)


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
            # print(video_path)
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
    def wrapper(filepath, torrent_path, *args, **kwargs):
        print(f"\n...Generating torrent: {filepath}")
        start_time = time.time()
        result = func(filepath, torrent_path, *args, **kwargs)
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

        print(f"Time taken: {time_str}\n")
        return result

    return wrapper


@timing_decorator
def create_torrent(
    filepath,
    torrent_dir,
    torrent_name="",
    comment="",
    exclude_pattern="(jpg)$",
    pt_tracker="https://www.pttime.org/announce.php",
):
    """
    # https://www.pttime.org/announce.php
    # https://tracker.exoticaz.to/announce
    """
    torrent_dir = os.path.join(
        "/volume1/System/CloudDoc/code/mac/python/pt/torrents", torrent_dir
    )
    # return print(torrent_dir)
    if not os.path.exists(torrent_dir):
        os.makedirs(torrent_dir)
    if torrent_name == "":
        torrent_dir = os.path.join(torrent_dir, f"{torrent_filename}.torrent")
    else:
        torrent_dir = os.path.join(torrent_dir, f"{torrent_name}.torrent")

    command = [
        "py3createtorrent",
        filepath,
        "--exclude-pattern-ci",
        exclude_pattern,
        "--private",
        "-t",
        pt_tracker,
        "-c",
        comment,
        "-o",
        torrent_dir,
        "--name",
        torrent_name,
        "--force",
    ]

    try:
        result = subprocess.run(
            command, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE
        )
        print("Torrent created successfully.")
        print(result.stdout.decode())
    except subprocess.CalledProcessError as e:
        print("An error occurred while creating the torrent.")
        print(e.stderr.decode())


@timing_decorator
def generate_private_torrent(
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

    print(f"Private torrent created.")


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


def generate_screenshots(video_path, save_path, num_screenshots=2):
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
            os.path.join(save_path, f"frame_{str(timestamp).replace('.', '_')}.jpg"),
            vframes=1,
            qscale=2,
            update=1,
        ).global_args("-loglevel", "quiet").run(overwrite_output=True)


def google_search(query, txt_path):
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
            with open(txt_path, "w") as file:
                for item in results.get("items", [])[:4]:
                    file.write(f'{item.get("title")}\n')
                    file.write(f'{item.get("link")}\n')
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


headers = {
    "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
    "accept-language": "en,zh;q=0.9",
    "cache-control": "max-age=0",
    "cookie": "cf_clearance=7IMPclTnva8aHSGJK1hTUAkcnjYQIWKUpA4V.mbFG4o-1717605930-1.0.1.1-1Aq2chOfOjNLHLayGFSOxElBKMxi2OkvoiJqtD1rdHJe8ewpZUnBEIkB6NoXMhjHAjn_r9i9OaXc8mue2hbbDA; remember_web_59ba36addc2b2f9401580f014c7f58ea4e30989d=eyJpdiI6IkZ3TzBCNFlpQ1lCRVVYYVROOUp6ZVE9PSIsInZhbHVlIjoiQmRnbmtPUWZoaWxxMThSb3dJdjFyblR1YjJrSFNveG1TQlwvajlsUU01VFMzaE1TN09QT05Idmt1YjNpQkptQlwvMDJFYjBpXC9SVUI5ZXM4RUFhSHkzT2pZa1pDN1B0R1hqWEVEVFdaV2VKdzYwMitXSUdyak9kanVpdHA3VVhFS29WY0RvbGs4R3VmXC9xVU9JMVJ3WVRVaVwvU0FcLytOSUtFMFpcL1ZTZTZJRk5UUT0iLCJtYWMiOiIzNmI4YjBhOGQ1M2NjYWJkNDIwMTIxOWE3ZTcwZWE2NzhhOWU1ZTU2YjY3NmEyNjA5MDkwYzVjMjczNjViNTA4In0%3D; love=11290; XSRF-TOKEN=eyJpdiI6IjhjblFNVW9QTFJ1T1VvR01KVEU4TkE9PSIsInZhbHVlIjoiV2p3UWpPV0s5dnpDUUd6bndZOHFBNmxJYXR6QnY2WUpKa1hxSXBuVTlDeVVYVm5FMGExVzd6SjA5dm5QT3krVCIsIm1hYyI6ImQ2ZjEwOGU3ZTAyNzcyMzZhZDNmZWMzOTAxOWYxYTU0ZGYxNDhmZTFlODM2OTc4M2M1Y2QxZmQ3NWI1NjRjM2YifQ%3D%3D; exoticaz_session=eyJpdiI6IlRsWUV0d3ZJQXVaTTRId3JGRUUrY1E9PSIsInZhbHVlIjoiYWd6UUNEUkp4a3FwSXIwXC9FMGxib3c0WTlLOWdQZk9YVzhjWG5BeFRxb0h1RmxybFU0ZjYzTlVwR0g4ZExYWGEiLCJtYWMiOiIzNTk0NTcxMjMxOGUyNmEwZTZmYWI3MDkyYTAzNmM2OTcyOGMyYWNiZWYzZDhhNDdmZGQ5NjkyN2VmODhjMDRiIn0%3D",
    "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.0.0 Safari/537.36",
}


def exoticaz_search(id, headers=headers):
    url = "https://exoticaz.to/torrents"

    querystring = {"search": id}

    # headers = {
    #     # "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
    #     # "Accept-Encoding": "gzip, deflate, br, zstd",
    #     "Cookie": "cf_clearance=ucDLuP6WUDkB5Au3kQfnHSDhPwmWX4qIqJa4i8Vhcas-1715989505-1.0.1.1-y0OltdhGHeyiapRnBPmF67Pl73Il6IERl5CQNB1mKkx67TpSjgcHSCzXZUeXULNREgbxy5PvePd2lzPNa_WDqQ; remember_web_59ba36addc2b2f9401580f014c7f58ea4e30989d=eyJpdiI6IlRlUEJZQ0phK2RnbmNWSlF1aTVkcEE9PSIsInZhbHVlIjoiYXBtbllzVGFuV0dwQjBycFNRMmJZQnYyMGZHcjZDXC8rK1E1cWtmWDBvd1MyWER1K3JSTlpcL1FQcHRpVm9wS0phaHJcL3RwUFBQXC9rcFJLczZKTFVLTDh2ZERKcXRFdDR3ZGhuS0xBMjRjdUlRcjY1eDBpakE2UDd4VFhUdXVuVEJrZXYyMGY3NE1INzBYcm9pdXhFdmppcUE0OEpqQzhcL24rMFVzQ01JZUZtTjQ9IiwibWFjIjoiZjJjYTIxYTJhMDY2MzZlZDVhOTBjMWViYTU1MzA1ZDlmMDA2ZmY1YWM4MjkwZGI0NWVlMzkwMGNlMjNjZGI4ZiJ9; love=11290; XSRF-TOKEN=eyJpdiI6IjJVUnNaTXlGOG5aRU1KSlFqeTRvREE9PSIsInZhbHVlIjoiTmNPM1I1MFBpckQwSEwxQVR6eTh4cTdxWUJUZEdoalBpU2tHa0lYelVoQnh2T1JWZnMwMTlUQU9SRVwvZUJKclkiLCJtYWMiOiJhMjFhYTgyYzcxYzhlOGYyMjI2M2QzOWRjNDExMDUzYmI1YjJhNWM4OTNkZmYyNjk3MzlmNzFhMmJiOTdiYmY4In0%3D; exoticaz_session=eyJpdiI6IkVrbW1cL1VSK1R3Y3RLdlwvS040dTZ1QT09IiwidmFsdWUiOiJUV1wvbUZlaGxIb3hTZmdXXC9XKzBGTEF6MElSTkRyV3hRaUpkcUp5YTdoWjFrc3IxQSt3U0JJRVR5aUJUZUt2dFUiLCJtYWMiOiIzY2RlOTAwOWQzZTBmOTFiOTEyMDY2ODQ1OGU2MTJhYjFmZDlkN2JlMDA5N2FlZWFkYWQyZDIxOTk5MmFjMTEyIn0%3D",
    #     "Connection": "keep-alive",
    #     "Sec-Fetch-Mode": "navigate",
    #     "Host": "exoticaz.to",
    #     "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36",
    #     "Sec-Fetch-Site": "same-origin",
    #     "Referer": "https://exoticaz.to/torrents",
    #     "Sec-Fetch-Dest": "document",
    #     "Accept-Language": "zh,en;q=0.9",
    #     "Content-Type": "text/html; charset=UTF-8",
    # }

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


def find_video_files(path):

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


def generate_screenshot(args):
    timestamp, index, video_path, save_path, target_width, target_height = args
    output_path = os.path.join(save_path, f"thumbnail_{index}.jpg")
    (
        ffmpeg.input(video_path, ss=timestamp)
        .filter("scale", target_width, target_height)
        .output(output_path, vframes=1, q=2, update=1)
        .run(overwrite_output=True)
        .global_args("-loglevel", "quiet")
        .run(overwrite_output=True)
    )


def generate_thumbnail_sheet(
    video_path, save_path="./thumbnails", columns=4, rows=6, target_width=248
):
    """
    Generate screenshots from a video while maintaining the video's original scale.

    :param video_path: Path to the video file
    :param save_path: Path to save the screenshots
    :param num_screenshots: Number of screenshots to generate
    :param target_width: Target width for the screenshots
    :param target_height: Target height for the screenshots
    """

    # Get video duration and original dimensions
    num_screenshots = columns * rows
    probe = ffmpeg.probe(video_path)
    duration = float(probe["format"]["duration"])
    video_stream = next(
        stream for stream in probe["streams"] if stream["codec_type"] == "video"
    )
    audio_stream = next(
        (stream for stream in probe["streams"] if stream["codec_type"] == "audio"), None
    )

    # Get information
    info_text = (
        f"File Name: {os.path.basename(video_path)}\n"
        f"Size: {auto_convert_memory(float(probe['format']['size']))}\n"
        f"Resolution: {video_stream['width']}x{video_stream['height']}, FPS: {eval(video_stream['avg_frame_rate']):.2f}\n"
        f"Video Codec: {video_stream['codec_name'].upper()}, Audio Codec: {audio_stream['codec_name'].upper()}\n"
        f"Duration: {int(float(video_stream['duration']) // 3600)}:{int(float(video_stream['duration']) // 60 % 60)}:{int(float(video_stream['duration']) % 60)}"
    )
    original_width = int(video_stream["width"])
    original_height = int(video_stream["height"])

    # Calculate aspect ratio
    aspect_ratio = original_width / original_height

    # Calculate target dimensions while maintaining aspect ratio

    target_height = int(target_width / aspect_ratio)

    # Calculate timestamps for evenly spaced frames
    timestamps = [
        round(duration * i / (num_screenshots + 1), 2)
        for i in range(1, num_screenshots + 1)
    ]

    # # Generate screenshots
    # for i, timestamp in enumerate(timestamps):
    #     output_path = os.path.join(save_path, f"thumbnail_{i}.jpg")
    #     (
    #         ffmpeg.input(video_path, ss=timestamp)
    #         .filter("scale", target_width, target_height)
    #         .output(output_path, vframes=1, q=2, update=1)
    #         .run(overwrite_output=True)
    #     )  # .global_args("-loglevel", "quiet").run(overwrite_output=True)
    # Create arguments for each timestamp
    args_list = [
        (timestamp, i, video_path, save_path, target_width, target_height)
        for i, timestamp in enumerate(timestamps)
    ]

    # Define the number of processes to use
    num_processes = os.cpu_count()  # Use number of CPU cores

    # Create a pool of worker processes
    with Pool(num_processes) as pool:
        # Map timestamps to worker processes
        pool.map(generate_screenshot, args_list)

    width_margin = 10
    height_margin = 10
    height_gap = 90
    sheet_width = (target_width + width_margin - 5) * columns
    sheet_height = (target_height + height_margin + 5) * rows
    thumbnail_size = (sheet_width, sheet_height)
    # Resize thumbnail while maintaining aspect ratio
    # thumbnail.thumbnail((max_width, max_height))

    thumbnail_sheet = Image.new("RGB", (sheet_width, sheet_height), color="black")
    thumbnail_sheet_path = os.path.join(save_path, "thumbnail_sheet.jpg")

    # Create a drawing context
    draw = ImageDraw.Draw(thumbnail_sheet)
    font_size = 50
    font = ImageFont.load_default()

    # Draw the text on the thumbnail sheet
    text_x = width_margin
    text_y = height_margin
    draw.multiline_text((text_x, text_y), info_text, fill="white", font=font)

    for i in range(columns * rows):

        col = i % columns
        row = i // columns

        thumbnail_path = f"{save_path}/thumbnail_{i}.jpg"
        thumbnail = Image.open(thumbnail_path)

        # Calculate thumbnail position to align at the bottom
        thumbnail_x = col * target_width + width_margin
        thumbnail_y = row * target_height + height_gap
        # print(i, col, row, thumbnail_x, thumbnail_y)
        thumbnail_sheet.paste(thumbnail, (thumbnail_x, thumbnail_y))

    thumbnail_sheet.save(thumbnail_sheet_path)


def generate_jav_torrent():
    # video = input("Enter video name: ")
    # video_name = os.path.splitext(os.path.basename(video))[0]
    # video_path = get_video_path_by_name(video_name)
    # torrent_foldername = input("Enter torrent name: ")
    content_path = input("Enter torrent content full path: ")
    torrent_foldername = os.path.basename(content_path)
    # return print(os.path.basename(content_path))
    # if os.path.isdir(content_path):
    #     video_path = input("Enter video full path: ")
    # else:
    #     video_path = content_path
    # comment = input("Enter comment: ")
    comment = torrent_foldername
    # video_name = "[HorrorPorn] Hell Hoes"
    # video_path = "/volume3/Data2/HD/videos/3d/manual-sort/asia/另类/地狱锄 猎奇重口资源 高价高质成人恐怖微电影 一群女人被怪物俘虏想要活命就得出卖肉体4K原版/UIDHUISDDD (3)/[HorrorPorn] Hell Hoes.mp4"
    torrent_dir = (
        f"/volume1/System/CloudDoc/code/mac/python/pt/torrents/{torrent_foldername}"
    )
    if not os.path.exists(torrent_dir):
        os.makedirs(torrent_dir)
    torrent_path = os.path.join(torrent_dir, f"{torrent_foldername}.torrent")
    create_torrent(
        content_path,
        torrent_dir,
        torrent_name=torrent_foldername,
        comment=comment,
        exclude_pattern="(nfo)$|DS_Store",
        pt_tracker="https://www.pttime.org/announce.php",
    )
    # generate_screenshots(video_path, torrent_dir)

    # txt_path = os.path.join(torrent_dir, "output.txt")
    # # with open(txt_path, "a") as file:
    # #     file.write(generate_media_info_string(video_path))
    # google_search(torrent_foldername, txt_path)
    # generate_thumbnail_sheet(video_path, save_path=torrent_dir)
    # # print(content_path)
    # generate_media_info_string(video_path)


def menu():
    menu = input(
        """
1. Generate torrent
2. Generate gif
3. Generate screenshots
4. Generate Media Info
5. Generate JAV Torrent
\n"""
    )
    if menu == "1":
        filepath = (
            input("Enter file / folder path: ")
            .replace("X:/", "/volume3/Data2/")
            .replace("Y:/", "/volume2/Data1/")
        )
        # return print(filepath)
        torrent_name = input("Enter torrent name: ")

        comment = input("Enter comment: ")

        create_torrent(
            filepath,
            torrent_name,
            torrent_name=torrent_name,
            comment=comment,
            exclude_pattern="(nfo)$|DS_Store",
            pt_tracker="https://www.pttime.org/announce.php",
        )
    if menu == "2":
        video_path = input("Enter video path: ")
        start_time = input("Enter start time(00:00:00): ")
        generate_gif(
            video_path=video_path,
            start_time=start_time,
            duration=5,
        )
    if menu == "3":
        # ffmpeg command
        video_path = input("Enter video path: ")
        # Walk through the directory
        for root, dirs, files in os.walk(video_path):
            for file in files:
                # Check if the file has a video extension
                if any(file.lower().endswith(ext) for ext in video_extensions):
                    # Get the base name of the file without the extension
                    file_name = os.path.splitext(file)[0]

                    command = [
                        "ffmpegthumbnailer",
                        "-i",
                        video_path,
                        "-s",
                        "0",
                        "-o",
                        f"{file_name}.jpg",
                        "-m",
                    ]
    if menu == "4":
        file_path = input("Enter file path: ")
        print(generate_media_info_string(file_path))
    if menu == "5":
        generate_jav_torrent()


def download_exoticaz_torrent(torrent_download_url, torrent_name, headers=headers):
    torrent_path = (
        f"/volume1/System/CloudDoc/code/mac/python/pt/torrents/{torrent_name}.torrent"
    )

    try:
        response = requests.get(torrent_download_url, headers=headers)

        if response.status_code == 200:
            with open(torrent_path, "wb") as file:
                file.write(response.content)
            print(f"File downloaded successfully and saved as {torrent_path}")
            return torrent_path
        else:
            print(f"Failed to download file. HTTP Status Code: {response.status_code}")
    except requests.RequestException as e:
        print(f"An error occurred during file download: {e}")


def get_exoticaz_torrent_info(url, headers=headers):
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()  # 检查请求是否成功
        soup = BeautifulSoup(response.content, "html.parser")

        # 查找包含'.torrent'的下载链接
        download_link_tag = None
        for tag in soup.find_all("a", href=True, title=True):
            if ".torrent" in tag["href"]:
                download_link_tag = tag
                break

        if download_link_tag:
            torrent_download_url = download_link_tag["href"]
            title = download_link_tag["title"]

            # 使用正则表达式从标题中提取括号内的内容
            match = re.search(r"\[(.*?)\]", title)
            if match:
                jav_id = match.group(1)
                return torrent_download_url, jav_id
            else:
                return None, "No JAV ID found in title"
        else:
            return None, "No torrent link found"

    except requests.RequestException as e:
        return None, f"Request error: {e}"


def exoticaz_reseed(url, video_name=None):
    try:
        # 获取Torrent下载URL和JAV ID
        torrent_download_url, jav_name = get_exoticaz_torrent_info(url)
        if video_name is not None:
            jav_name = video_name

        # 下载Torrent文件
        torrent_path = download_exoticaz_torrent(torrent_download_url, jav_name)
        if not torrent_path or not os.path.exists(torrent_path):
            raise ValueError("Failed to download torrent file.")

        # 获取视频文件的路径
        video_path = get_video_path_by_name(jav_name)
        if not video_path or not os.path.exists(video_path):
            raise FileNotFoundError(f"No video file found for jav_id: {jav_name}")

        # 设置保存路径（通常是视频文件所在的目录）
        save_path = os.path.dirname(video_path)

        # 上传Torrent到qBittorrent
        upload_torrent(torrent_path, save_path, category="保种")

        print(f"Torrent uploaded successfully for {jav_name}")

    except ValueError as ve:
        print(f"Error processing torrent or video files: {ve}")
    except FileNotFoundError as fe:
        print(f"Error: {fe}")
    except Exception as e:
        print(f"Unexpected error in exoticaz_reseed: {e}")


if __name__ == "__main__":
    # while True:
    #     menu()
    url = "https://exoticaz.to/torrent/99837"
    exoticaz_reseed(url)
    # main()
    # create_private_torrent(
    #     "/volume3/Data2/HD/videos/3d/manual-sort/asia/FC2/1218225509.M2TS",
    #     "1218225509.torrent",
    # )
    # upload_torrent(
    #     torrent_path="[exoticaz.to] horrorporn.hell.hoes.torrent",
    #     save_path="/volume3/Data2/HD/videos/3d/manual-sort/asia/另类/地狱锄 猎奇重口资源 高价高质成人恐怖微电影 一群女人被怪物俘虏想要活命就得出卖肉体4K原版/UIDHUISDDD (3)/",
    # )

    # generate_screenshots(
    #     video_path="/volume3/Data2/downloads/保种/Extremely rare internal customization leaked, slave girl trained for private filming, graceful and immature body, shaved pussy, lustful and seductive.mp4",
    #     save_path="./",
    #     num_screenshots=2,
    # )

    pass
