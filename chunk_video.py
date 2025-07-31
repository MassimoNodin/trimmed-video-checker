from pathlib import Path
import audio
import wave

CHUNK_LENGTH = 5  # seconds
OVERLAPPING_COUNT = 0 # Times Overlapped

class VideoRange:
    def __init__(self, start: float, end: float):
        self.start = start
        self.end = end

    def __repr__(self):
        return f"VideoRange(start={self.start}, end={self.end})"

def video_ranges(wav_path: Path):
    """
    Function to chunk video files.
    Creates video files of CHUNK_LENGTH seconds each.
    Creates overlapping chunks based on OVERLAPPING_COUNT.
    """
    ranges = []
    # Get the total duration of the audio file
    total_duration = get_video_duration(wav_path)

    new_chunk_length = CHUNK_LENGTH / (2 ** (OVERLAPPING_COUNT))
    start = 0
    while start + CHUNK_LENGTH <= total_duration:
        ranges.append(VideoRange(start, start + CHUNK_LENGTH))
        start = start + new_chunk_length
    return ranges

def get_video_duration(video_path: Path) -> float:
    """
    Function to get the duration of a video file.
    Returns the duration in seconds.
    """

    with wave.open(str(video_path), 'rb') as video_file:
        frames = video_file.getnframes()
        rate = video_file.getframerate()
        duration = frames / float(rate)
    return duration

def chunk_video(video_path: Path):
    """
    Function to chunk video files.
    This function will handle the logic for chunking video files
    into smaller segments based on the audio chunks.
    """
    # For demonstration, we will just call the audio_ranges function
    # to get the audio chunks and print them.
    wav_path = audio.extract_wav_file(video_path)
    ranges = video_ranges(wav_path)
    audio_chunks = audio.extract_wav_files(wav_path, ranges)

    for chunk in ranges:
        print(f"Video chunk from {chunk.start} to {chunk.end}")
    
    # Here you would implement the actual video chunking logic
    # based on the audio chunks obtained.