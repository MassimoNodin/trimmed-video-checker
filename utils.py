import json
from pathlib import Path
import subprocess
from config import CHUNK_LENGTH, OVERLAPPING_COUNT

class VideoRange:
    def __init__(self, start: float, end: float):
        self.start = start
        self.end = end

    def __repr__(self):
        return f"VideoRange(start={self.start}, end={self.end})"
    
def get_video_duration(video_path):
    result = subprocess.run(
        ['ffprobe', '-v', 'error', '-select_streams', 'v:0',
         '-show_entries', 'format=duration', '-of', 'json', video_path],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT
    )
    info = json.loads(result.stdout)
    return float(info['format']['duration'])

def video_ranges(video_path: Path):
    """
    Generate video ranges based on the total duration of the video.
    This function will create ranges for chunking the video into smaller segments.
    Each segment will be of length CHUNK_LENGTH, with overlapping segments based on OVERLAPPING_COUNT.
    """
    ranges = []
    # Get the total duration of the video file
    total_duration = get_video_duration(video_path)

    new_chunk_length = CHUNK_LENGTH / (2 ** (OVERLAPPING_COUNT))
    start = 0
    while start + CHUNK_LENGTH <= total_duration:
        ranges.append(VideoRange(start, start + CHUNK_LENGTH))
        start = start + new_chunk_length
    return ranges