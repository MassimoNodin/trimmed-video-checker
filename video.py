import os
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
    subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    return output_path

def extract_video_chunks(video_path: Path, ranges: List[VideoRange]) -> List[Path]:
    """
    Function to extract video segments based on the provided ranges.
    Saves the extracted segments in the TEMP_VIDEO_DIR.
    """
    extracted_files = []
    for i, video_range in enumerate(ranges):
        start_time = video_range.start
        end_time = video_range.end
        segment_path = TEMP_VIDEO_DIR / f"{video_path.stem}_segment_{i}.mp4"
        cmd = [
            'ffmpeg', '-i', str(video_path), '-ss', str(start_time), '-to', str(end_time),
            '-c:v', 'copy', '-c:a', 'copy', '-y', str(segment_path)
        ]
        subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        extracted_files.append(segment_path)
    os.unlink(video_path) if video_path.exists() else None
    return extracted_files