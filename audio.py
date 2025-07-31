from pathlib import Path
import subprocess
from typing import List, Iterator
from config import TEMP_AUDIO_DIR
from utils import VideoRange

class AudioExtractor:
    """
    A class to extract audio segments from a video file iteratively.
    """
    def __init__(self, video_path: Path, ranges: List[VideoRange]):
        """
        Initializes the AudioExtractor by extracting the full audio from the video.

        Args:
            video_path: The path to the video file.
            ranges: A list of VideoRange objects specifying the segments to extract.
        """
        self.video_path = video_path
        self.ranges = ranges
        self.wav_path = self._extract_full_wav()
        self._index = 0

    def _extract_full_wav(self) -> Path:
        """
        Extracts the audio from the video file and saves it as a wave file.
        Returns the path to the extracted wave file.
        """
        wav_path = TEMP_AUDIO_DIR / f"{self.video_path.stem}.wav"
        cmd = [
            'ffmpeg', '-i', str(self.video_path), "-y", '-vn', '-acodec', 'pcm_s16le', '-ar', '48000', '-ac', '1', str(wav_path)
        ]
        subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        return wav_path

    def __iter__(self) -> Iterator[Path]:
        """Returns the iterator object itself."""
        return self

    def __next__(self) -> Path:
        """
        Extracts the next audio segment based on the provided ranges
        and returns the path to the segment file.
        """
        if self._index < len(self.ranges):
            audio_range = self.ranges[self._index]
            start_time = audio_range.start
            end_time = audio_range.end
            segment_path = TEMP_AUDIO_DIR / f"{self.wav_path.stem}_segment_{self._index}.wav"
            cmd = [
                'ffmpeg', '-i', str(self.wav_path), '-ss', str(start_time), "-y", '-vn', '-to', str(end_time), '-acodec', 'pcm_s16le', '-ar', '48000', '-ac', '1', str(segment_path)
            ]
            subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            self._index += 1
            return segment_path
        else:
            raise StopIteration