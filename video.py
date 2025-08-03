import os
from pathlib import Path
import subprocess
from typing import List, Iterator
from embedding import embed_video_chunk, load_embedding, save_embedding, check_embedding_exists
from config import CHUNK_LENGTH, EMBEDDING_DIR, TEMP_VIDEO_DIR
from utils import VideoRange, get_video_duration

class VideoExtractor:
    """
    A class to extract video segments based on provided time ranges.
    It is iterable, yielding the path to each extracted chunk.
    """

    def __init__(self, video_path: Path, ranges: List[VideoRange]):
        """
        Initializes the VideoExtractor.

        :param video_path: Path to the temporary video file to be chunked.
        :param ranges: A list of VideoRange objects specifying the segments to extract.
        """
        self.video_path = video_path
        self.ranges = ranges
        self.cached = True
        self.lower_quality_video = self.extract_lower_quality_video(video_path)
        self._index = 0

    def __iter__(self) -> Iterator[Path]:
        """Returns the iterator object itself."""
        return self
    
    def __next__(self):
        """
        Extracts the next video segment based on the provided ranges
        and returns the embedding and path to the segment file.
        """
        if self.cached:
            segment_path = EMBEDDING_DIR / f"{self.video_path.stem}_video_{self._index + 1}.npy"
            if segment_path.exists():
                embedding = load_embedding(segment_path)
                self._index += 1
                return embedding, segment_path
        if self._index < len(self.ranges):
            # print(f"Processing video segment {self._index + 1}/{len(self.ranges)} for {self.video_path.name}")
            video_range = self.ranges[self._index]
            start_time = video_range.start
            end_time = video_range.end
            segment_path = TEMP_VIDEO_DIR / f"{self.video_path.stem}_segment_{self._index}.mp4"
            # print(f"Extracting video segment from {start_time} to {end_time} seconds into {segment_path}")
            cmd = [
                'ffmpeg', '-ss', str(start_time), '-i', str(self.lower_quality_video), '-t', str(CHUNK_LENGTH),
                '-c:v', 'copy', '-c:a', 'copy', '-y', str(segment_path)
            ]
            subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            self._index += 1
            video_embedding = embed_video_chunk(segment_path)
            segment_path = EMBEDDING_DIR / f"{self.video_path.stem}_video_{self._index}.npy"
            save_embedding(video_embedding, segment_path)
            video_embedding = video_embedding.cpu().numpy()
            return video_embedding, segment_path
        else:
            # Clean up the temporary low-quality video file after processing
            if self.lower_quality_video.exists():
                os.unlink(self.lower_quality_video)
            raise StopIteration

    def extract_lower_quality_video(self, video_path: Path, width: int = 64, height: int = 64) -> Path:
        """
        Extract a lower quality version of the video by resizing it.
        Returns the path to the resized video.
        """
        # return video_path
        for i in range(1, len(self.ranges) + 1):
            segment_path = EMBEDDING_DIR / f"{self.video_path.stem}_video_{i}.npy"
            if not segment_path.exists():
                self.cached = False
        if self.cached:
            self.cached = True
            return None, None
        video_duration = get_video_duration(video_path)
        output_path = TEMP_VIDEO_DIR / f"{video_path.stem}_low_quality.mp4"
        cmd = [
            'ffmpeg', '-hwaccel', 'cuda', '-i', str(video_path),
            '-vf', f'scale={width}:{height}',
            '-c:v', 'libx264', '-preset', 'fast', '-crf', '28',
            '-y', str(output_path),
            '-v', 'error',
            '-progress', 'pipe:1'       # machine-readable progress
        ]
        process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        
        for line in process.stdout:
            if "out_time_ms" in line:
                # Parse progress in microseconds
                out_time = (int(line.strip().split('=')[1]) / 10000) / video_duration if line.strip().split('=')[1] != 'N/A' else 0
                # You can render a progress bar here
                print(f"\rProgress: {out_time:.2f}%          ", end='', flush=True)
        return output_path