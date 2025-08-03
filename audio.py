import os
from pathlib import Path
import subprocess
from typing import List, Iterator

import librosa
import torch
from embedding import embed_audio_chunk, check_embedding_exists, load_embedding, save_embedding
from config import TEMP_AUDIO_DIR, CHUNK_LENGTH, EMBEDDING_DIR
from utils import VideoRange, get_video_duration
import torch.nn.functional as F

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
        self.cached = True
        self.waveform, self.sr = self._extract_waveform()
        self._index = 0

    def _extract_waveform(self) -> torch.Tensor:
        """
        Extracts the audio from the video file and saves it as a wave file.
        Returns the path to the extracted wave file.
        """
        for i in range(1, len(self.ranges) + 1):
            segment_path = EMBEDDING_DIR / f"{self.video_path.stem}_audio_{i}.npy"
            if not segment_path.exists():
                self.cached = False        
        if self.cached:
            self.cached = True
            return None, None
        wav_path = TEMP_AUDIO_DIR / f"{self.video_path.stem}.wav"
        cmd = [
            'ffmpeg', '-i', str(self.video_path), "-y",'-vn', '-acodec', 'pcm_s16le', '-ar', '48000', '-ac', '1','-progress', 'pipe:1', str(wav_path)
        ]
        video_duration = get_video_duration(self.video_path)
        process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        
        for line in process.stdout:
            if "out_time_ms" in line:
                # Parse progress in microseconds
                out_time = (int(line.strip().split('=')[1]) / 10000) / video_duration if line.strip().split('=')[1] != 'N/A' else 0
                # You can render a progress bar here
                print(f"\rProgress: {out_time:.2f}%", end='', flush=True)

        audio_data, sr = librosa.load(str(wav_path), sr=48000, mono=True)
        waveform = torch.tensor(audio_data).unsqueeze(0)
        if waveform.shape[0] > 1:
            waveform = waveform.mean(dim=0, keepdim=True)
        
        chunk_samples = int(CHUNK_LENGTH * sr)
        current_samples = waveform.shape[1]
        remainder = current_samples % chunk_samples
        if remainder != 0:
            padding_needed = chunk_samples - remainder
            waveform = F.pad(waveform, (0, padding_needed))
        return waveform, sr

    def __iter__(self) -> Iterator[Path]:
        """Returns the iterator object itself."""
        return self

    def __next__(self) -> Path:
        """
        Extracts the next audio segment based on the provided ranges
        and returns the path to the segment file.
        """
        if self.cached:
            segment_path = EMBEDDING_DIR / f"{self.video_path.stem}_audio_{self._index + 1}.npy"
            if segment_path.exists():
                embedding = load_embedding(segment_path)
                self._index += 1
                return embedding, segment_path
        if self._index < len(self.ranges):
            # print(f"Processing audio segment {self._index + 1}/{len(self.ranges)} for {self.video_path.name}")
            audio_range = self.ranges[self._index]
            start_time = audio_range.start * self.sr
            end_time = audio_range.end * self.sr
            waveform_segment = self.waveform[:, int(start_time):int(end_time)]
            self._index += 1
            audio_embedding = embed_audio_chunk(waveform_segment)
            segment_path = EMBEDDING_DIR / f"{self.video_path.stem}_audio_{self._index}.npy"
            save_embedding(audio_embedding, segment_path)
            audio_embedding = audio_embedding.cpu().numpy()
            return audio_embedding, waveform_segment
        else:
            os.unlink(TEMP_AUDIO_DIR / f"{self.video_path.stem}.wav") if (TEMP_AUDIO_DIR / f"{self.video_path.stem}.wav").exists() else None
            raise StopIteration