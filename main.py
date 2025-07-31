import chunk_video
from pathlib import Path

def add_video(video_path: Path):
    chunk_video.chunk_video(video_path)
    """
    Function to add a video to the system.
    This function will handle the logic for adding a new video,
    including any necessary validations and processing.
    """
    # Implementation of video addition logic goes here
    pass

add_video(Path("/mnt/nvme/clipsviewer/videos_test/PS5/CREATE/Video Clips/Grand Theft Auto V/dropped.mp4"))