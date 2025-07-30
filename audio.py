from pathlib import Path
import wave

CHUNK_LENGTH = 5  # seconds
OVERLAPPING_COUNT = 0 # Times Overlapped

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

