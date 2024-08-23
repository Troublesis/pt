from qbittorrentapi import Client

from config.config import settings
from logger import logger


class Qbit:
    """
    A class to manage connection to the qBittorrent Web API.

    Attributes:
        host (str): The host URL for the qBittorrent API.
        username (str): The username for authentication.
        password (str): The password for authentication.
        client (Client or None): An instance of the qBittorrent API client.

    Methods:
        create_client(): Creates and returns a qBittorrent API client instance.
    """

    def __init__(self):
        """
        Initializes QBitTorrentClient with configuration values.
        """
        self.host = settings.from_env("qbit").host
        self.username = settings.from_env("qbit").username
        self.password = settings.from_env("qbit").password

    def client(self) -> Client:
        """
        Creates and returns a qBittorrent API client instance.

        This method attempts to create a connection to the qBittorrent Web API
        using credentials stored in the configuration. If successful, it assigns
        the client instance to the `client` attribute. If an error occurs, it logs
        the error and sends a notification via the Bark service.

        Returns:
            Client or None: A qBittorrent API client instance if successful, None otherwise.

        Raises:
            ValueError: If required configuration values are missing.
        """
        try:
            if not all([self.host, self.username, self.password]):
                raise ValueError("Missing required qBittorrent configuration values")

            self.client = Client(
                host=self.host, username=self.username, password=self.password
            )
            logger.info("qBittorrent logged in.")
            return self.client

        except ValueError as ve:
            logger.error(f"Configuration error: {ve}")
        except Exception as e:
            logger.error(f"Error creating qBittorrent client: {e}")
        return None

    def upload_torrent(self, torrent_path: str, save_path: str, category: str = "保种"):
        # 打印正在添加的torrent信息
        logger.info(f"...Adding torrent: {torrent_path} to: {save_path}")
        try:
            # 调用qbitapi().torrents_add方法添加torrent
            self.client.torrents_add(
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
        except Exception as e:
            # 捕获所有异常并打印
            logger.error(f"Error adding or deleting torrent: {e}")
        else:
            # 打印完成信息
            logger.info("Upload done.")


if __name__ == "__main__":
    qbit = Qbit()
    client = qbit.client()
