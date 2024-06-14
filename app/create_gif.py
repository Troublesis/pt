import subprocess


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


if __name__ == "__main__":
    video_name = input("Enter video name: ")
    start_time_list = []
    while True:
        start_time = input("Enter start time (format HH:MM:SS) or 'y' to stop: ")
        if start_time.lower() == "y" or start_time == "":
            break
        start_time_list.append(start_time)

    for start_time in start_time_list:
        create_gif(video_name, start_time)
