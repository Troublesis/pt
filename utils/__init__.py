import requests
from bs4 import BeautifulSoup
import random
import time


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
    span_element = soup.find('span', class_='badge badge-secondary')

    if span_element:
        if span_element != "0 torrents":
            
            span_element = soup.find('span', {'data-toggle': 'tooltip'})

            # Check if the <span> element was found
            if span_element:
                # Find the <a> element directly following the <span> element
                a_element = span_element.find_next_sibling('a')
                
                # Check if the <a> element was found
                if a_element and a_element.has_attr('href') and a_element.has_attr('title'):
                    href = a_element['href']
                    title = a_element['title']
                    print(f'{title}')
                    print(f'{href}')
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
    video_extensions = ['.mp4', '.avi', '.mkv', '.mov', '.flv', '.wmv', 'm2ts']

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

# Example usage:
video_files = find_video_files('/Volumes/Data2/HD/videos/3d/manual-sort/asia/FC2/')
# print(video_files)
for video in video_files:
    print(video)
    exoticaz_search(video)




# print(exoticaz_search("ipx-580"))

