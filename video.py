from pathlib import Path
import subprocess
from typing import List
from config import TEMP_VIDEO_DIR
from utils import VideoRange

def extract_lower_quality_video(video_path: str, width: int = 64, height: int = 64) -> str:
    """
    Extract a lower quality version of the video by resizing it.
    Returns the path to the resized video.
    """
    output_path = TEMP_VIDEO_DIR / f"{Path(video_path).stem}_low_quality.mp4"
    cmd = [
        'ffmpeg', '-i', video_path, '-vf', f'scale={width}:{height}', '-c:v', 'libx264',
        '-preset', 'fast', '-crf', '28', '-y', output_path
    ]
    subprocess.run(cmd, check=True)
    return output_path