import requests
from bs4 import BeautifulSoup

from config.config import settings
from logger import logger
from utils.emby import Emby
from utils.qbit import Qbit


class Exoticaz:
    def __init__(self):
        self.headers = {
            "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
            "accept-language": "en,zh;q=0.9",
            "cache-control": "max-age=0",
            "cookie": settings.from_env("exo").cookie,
            "user-agent": settings.user_agent,
        }

    def download_torrent(self, torrent_download_url, torrent_name):
        """
        下载torrent文件并保存到指定路径。

        Args:
            torrent_download_url (str): torrent文件的下载链接。
            torrent_name (str): torrent文件的名称。

        Returns:
            str: 保存torrent文件的完整路径。

        """
        torrent_path = os.path.join(
            settings.torrent_save_path, f"{torrent_name}.torrent"
        )

        try:
            response = requests.get(torrent_download_url, headers=self.headers)

            if response.status_code == 200:
                with open(torrent_path, "wb") as file:
                    file.write(response.content)
                logger.info(f"File downloaded successfully and saved as {torrent_path}")
                return torrent_path
            else:
                logger.error(
                    f"Failed to download file. HTTP Status Code: {response.status_code}"
                )
        except requests.RequestException as e:
            logger.error(f"An error occurred during file download: {e}")

    def get_torrent_info(self, url):
        """
        获取torrent信息

        Args:
            url (str): torrent页面的URL

        Returns:
            Tuple[str, str]: 包含torrent下载链接和JAV ID的元组，如果获取失败则返回(None, 错误信息)

        """
        try:
            response = requests.get(url, headers=self.headers)
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

    def search(self, id):
        """
        在Exoticaz上搜索种子。

        Args:
            id (str): JAV ID或视频名称

        Returns:
            bool: 如果找到种子则返回True，否则返回False

        Raises:
            ElementNotFoundException: 如果找不到元素则引发此异常

        """
        url = "https://exoticaz.to/torrents"
        querystring = {"search": id}
        response = requests.get(url, headers=self.headers, params=querystring)
        # Parse the HTML content
        soup = BeautifulSoup(
            response.content.decode("utf-8", errors="replace"), "html.parser"
        )
        # print(soup)
        span_element = soup.find("span", class_="badge badge-secondary")

        if span_element:
            if span_element != "0 torrents":
                span_element = soup.find("span", {"data-toggle": "tooltip"})
                # Check if the <span> element was found
                if span_element:
                    # Find the <a> element directly following the <span> element
                    a_element = span_element.find_next_sibling("a")
                    if (
                        a_element
                        and a_element.has_attr("href")
                        and a_element.has_attr("title")
                    ):
                        href = a_element["href"]
                        title = a_element["title"]
                        logger.info(f"{title}")
                        logger.info(f"{href}")
                        return True
                    else:
                        logger.info("No torrent info found")
                else:
                    logger.info("No torrent found")
            else:
                raise ElementNotFoundException("Element not found")
        return False

    def reseed(self, url, video_name=None):
        """
        根据提供的Torrent下载URL，下载Torrent文件，并上传到qBittorrent进行保种。

        Args:
            url (str): Torrent下载URL。
            video_name (str, optional): 视频文件名。默认为None，使用从URL中解析出的文件名。

        Returns:
            None

        Raises:
            ValueError: 下载Torrent文件失败。
            FileNotFoundError: 未找到对应的视频文件。
            Exception: 其他未预期的错误。
        """
        try:
            # 获取Torrent下载URL和JAV ID
            torrent_download_url, jav_name = self.get_torrent_info(url)
            if video_name is not None:
                jav_name = video_name

            # 下载Torrent文件
            torrent_path = self.download_torrent(torrent_download_url, jav_name)
            if not torrent_path or not os.path.exists(torrent_path):
                raise ValueError("Failed to download torrent file.")

            # 获取视频文件的路径
            emby = Emby()
            video_path = emby.get_video_path_by_name(jav_name)
            if not video_path or not os.path.exists(video_path):
                msg = f"No video file found for jav_id: {jav_name}"
                logger.error(msg)
                raise FileNotFoundError(msg)

            # 设置保存路径（通常是视频文件所在的目录）
            save_path = os.path.dirname(video_path)

            # 上传Torrent到qBittorrent

            qbit = Qbit()
            qbit.upload_torrent(torrent_path, save_path, category="保种")

            logger.info(f"Torrent uploaded successfully for {jav_name}")

        except ValueError as ve:
            logger.error(f"Error processing torrent or video files: {ve}")
        except FileNotFoundError as fe:
            logger.error(f"Error: {fe}")
        except Exception as e:
            logger.error(f"Unexpected error in exoticaz_reseed: {e}")


if __name__ == "__main__":
    exo = Exoticaz()
    exo.search("IPX-580")
