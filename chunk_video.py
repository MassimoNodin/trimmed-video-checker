from pathlib import Path
from audio import AudioExtractor
from utils import video_ranges

def chunk_video(video_path: Path):
    """
    Function to chunk video files.
    This function will handle the logic for chunking video files
    into smaller segments based on the audio chunks.
    """

    ranges = video_ranges(video_path)
    audio_extractor = AudioExtractor(video_path, ranges)
    return audio_extractor, None