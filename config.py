from pathlib import Path
import torch

TEMP_AUDIO_DIR = Path("temp")
TEMP_AUDIO_DIR.mkdir(exist_ok=True)

TEMP_VIDEO_DIR = Path("temp")
TEMP_VIDEO_DIR.mkdir(exist_ok=True)

CHUNK_LENGTH = 5  # seconds
OVERLAPPING_COUNT = 0 # Times Overlapped
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")