from pathlib import Path
import wave
import subprocess
from typing import List

TEMP_AUDIO_DIR = Path("temp")
TEMP_AUDIO_DIR.mkdir(exist_ok=True)

def extract_wav_file(video_path: Path) -> Path:
    """
    Function to extract the audio from a video file and save it as a wave file.
    Returns the path to the extracted wave file.
    """
    wav_path = TEMP_AUDIO_DIR / f"{video_path.stem}.wav"
    cmd = [
        'ffmpeg', '-i', str(video_path), "-y", '-vn', '-acodec', 'pcm_s16le', str(wav_path)
    ]
    subprocess.run(cmd, check=True)
    return Path(wav_path)

def extract_wav_files(wav_path: Path, ranges):
    """
    Function to extract audio segments from a wave file based on the provided ranges.
    Saves the extracted segments in the TEMP_AUDIO_DIR.
    """
    extracted_files = []
    for i, audio_range in enumerate(ranges):
        start_time = audio_range.start
        end_time = audio_range.end
        segment_path = TEMP_AUDIO_DIR / f"{wav_path.stem}_segment_{i}.wav"
        cmd = [
            'ffmpeg', '-i', str(wav_path), '-ss', str(start_time), "-y", '-to', str(end_time),
            '-acodec', 'pcm_s16le', str(segment_path)
        ]
        subprocess.run(cmd, check=True)
        extracted_files.append(segment_path)
    return extracted_files