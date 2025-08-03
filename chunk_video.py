from pathlib import Path
from audio import AudioExtractor
from utils import video_ranges
from embedder import EmbedExtractor

def chunk_video(video_path: Path):
    """
    Function to chunk video files.
    This function will handle the logic for chunking video files
    into smaller segments based on the audio chunks.
    """

    ranges = video_ranges(video_path)
    embed_extractor = EmbedExtractor(video_path, ranges)
    return embed_extractor