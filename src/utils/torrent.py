import os
import subprocess
import time

from config.config import settings
from logger import logger


def timing_decorator(func):
    def wrapper(*args, **kwargs):
        logger.info("Starting...")
        start_time = time.time()
        result = func(*args, **kwargs)
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

        logger.info(f"Time taken: {time_str}")
        return result

    return wrapper


class Torrent:
    def __init__(self):
        pass

    @timing_decorator
    def create(
        self,
        content_path,
        pt_tracker,
        torrent_name="",
        comment="",
        exclude_pattern="(jpg)$|(nfo)$|DS_Store",
    ):
        # If source_path is a folder
        if os.path.isdir(content_path):
            torrent_basename = os.path.basename(content_path)
            torrent_output_folder_path = os.path.join(
                settings.torrent_save_path, torrent_basename
            )
        elif os.path.isfile(content_path):
            torrent_basename = os.path.splitext(os.path.basename(content_path))[0]
            torrent_filename_withoutext = os.path.splitext(torrent_basename)[0]

            torrent_output_folder_path = os.path.join(
                settings.torrent_save_path,
                torrent_filename_withoutext,
            )
        # return print(torrent_dir)
        if not os.path.exists(torrent_output_folder_path):
            os.makedirs(torrent_output_folder_path)
        if torrent_name == "":
            torrent_name = torrent_basename
        torrent_output_filepath = os.path.join(
            torrent_output_folder_path, f"{torrent_name}.torrent"
        )

        command = [
            "py3createtorrent",
            content_path,
            "--exclude-pattern-ci",
            exclude_pattern,
            "--private",
            "-t",
            pt_tracker,
            "-c",
            comment,
            "-o",
            torrent_output_filepath,
            "--name",
            torrent_basename,
            "--force",
        ]

        try:
            result = subprocess.run(
                command, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE
            )
            # print("Torrent created successfully.")
            logger.info(result.stdout.decode())
        except subprocess.CalledProcessError as e:
            # print("An error occurred while creating the torrent.")
            logger.error(e.stderr.decode())


if __name__ == "__main__":
    torrent_dir = settings.torrent_save_path
    pt_tracker = settings.from_env("pttime").tracker
    content_path = "/volume1/System/CloudDoc/code/python/pt/src/utils"
    comment = "This is a test comment."
    exclude_pattern = "(jpg)$|(nfo)$|DS_Store"
    t = Torrent()
    t.create(
        content_path,
        pt_tracker,
        # torrent_name="test",
        comment=comment,
        exclude_pattern=exclude_pattern,
    )
