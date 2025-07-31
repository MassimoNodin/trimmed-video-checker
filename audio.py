from pathlib import Path
import wave
import subprocess
from typing import List

CHUNK_LENGTH = 5  # seconds
OVERLAPPING_COUNT = 0 # Times Overlapped

TEMP_AUDIO_DIR = Path("temp")
TEMP_AUDIO_DIR.mkdir(exist_ok=True)

class AudioRange:
    def __init__(self, start: float, end: float):
        self.start = start
        self.end = end

    def __repr__(self):
        return f"AudioRange(start={self.start}, end={self.end})"


def audio_ranges(wav_path: Path):
    """
    Function to chunk audio files.
    Creates audio files of CHUNK_LENGTH seconds each.
    Creates overlapping chunks based on OVERLAPPING_COUNT.
    """
    ranges = []
    # Get the total duration of the audio file
    total_duration = get_audio_duration(wav_path)

    new_chunk_length = CHUNK_LENGTH / (2 ** (OVERLAPPING_COUNT))
    start = 0
    while start + CHUNK_LENGTH <= total_duration:
        ranges.append(AudioRange(start, start + CHUNK_LENGTH))
        start = start + new_chunk_length
    return ranges

def get_audio_duration(wav_path: Path) -> float:
    """
    Function to get the duration of an audio file.
    Returns the duration in seconds.
    """

    with wave.open(str(wav_path), 'rb') as wav_file:
        frames = wav_file.getnframes()
        rate = wav_file.getframerate()
        duration = frames / float(rate)
    return duration

def extract_wav_file(video_path: Path) -> Path:
    """
    Function to extract the audio from a video file and save it as a wave file.
    Returns the path to the extracted wave file.
    """
    wav_path = TEMP_AUDIO_DIR / f"{video_path.stem}.wav"
    cmd = [
        'ffmpeg', '-i', str(video_path), '-vn', '-acodec', 'pcm_s16le', "-threads", "2", str(wav_path)
    ]
    subprocess.run(cmd, check=True)
    return Path(wav_path)

def extract_wav_files(wav_path: Path, ranges: List[AudioRange]):
    """
    Function to extract audio segments from a wave file based on the provided ranges.
    Saves the extracted segments in the TEMP_AUDIO_DIR.
    """
    return