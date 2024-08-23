import os

from config.config import settings
from logger import logger
from utils.torrent import Torrent


def generate_jav_torrent():
    exclude_pattern = "(jpg)$|(nfo)$|DS_Store"
    pt_tracker = input("1: EXO 2: PTTIME\nEnter tracker number: ")
    if pt_tracker == "1":
        pt_tracker = "https://exoticaz.com/announce"
    elif pt_tracker == "2" or pt_tracker == "":
        pt_tracker = "https://www.pttime.org/announce.php"
    content_path = (
        input("Enter file / folder path: ")
        .replace("X:/", "/volume3/Data2/")
        .replace("Y:/", "/volume2/Data1/")
        .replace("/Volumes/Data2", "/volume3/Data2")
        .replace("/Volumes/Data1", "/volume2/Data1")
    )
    torrent_foldername = os.path.basename(content_path)
    comment = torrent_foldername
    torrent_dir = os.path.join(settings.torrent_save_path, torrent_foldername)
    if not os.path.exists(torrent_dir):
        os.makedirs(torrent_dir)
    torrent_path = os.path.join(torrent_dir, f"{torrent_foldername}.torrent")

    t = Torrent()
    t.create(
        content_path=content_path,
        pt_tracker=pt_tracker,
        # torrent_name="test",
        comment=comment,
        exclude_pattern=exclude_pattern,
    )
    logger.info(f"Torrent saved: {torrent_path}")


def menu():
    menu = input(
        """
1. Generate JAV Torrent
2. Generate gif
3. Generate screenshots
4. Generate Media Info
5. Generate JAV Torrent
6. Upload torrent to qbit
\n"""
    )
    if menu == "1":

        generate_jav_torrent()


if __name__ == "__main__":
    pass
    while True:
        menu()
