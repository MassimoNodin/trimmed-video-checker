import sys
import termios
import tty
import chunk_video
from embedding import load_index
from pathlib import Path
import faiss
import random

def add_video(video_path: Path):
    print(f"\nAdding video: {video_path.name}")
    
    audio_extractor, video_extractor = chunk_video.chunk_video(video_path)
    return video_extractor, audio_extractor

def get_char():
    fd = sys.stdin.fileno()
    old_settings = termios.tcgetattr(fd)
    try:
        tty.setraw(fd)
        ch = sys.stdin.read(1)  # Read one character
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
    return ch

def get_inputs(visual_weight, eps):
    print(f"Current Visual Weight: {visual_weight}, Current Audio Weight: {round(1 - visual_weight, 2)}, Current EPS: {eps}")
    key = print("Press 'w' to increase visual weight, 's' to decrease, 'a' to decrease eps, 'd' to increase eps, or 'q' to confirm: ")
    key = get_char()
    if key == 'w':
        visual_weight = round(min(1.0, visual_weight + 0.05), 2)
    if key == "W":
        visual_weight = round(min(1.0, visual_weight + 0.01), 2)
    elif key == 's':
        visual_weight = round(max(0.0, visual_weight - 0.05), 2)
    if key == "S":
        visual_weight = round(max(0.0, visual_weight - 0.01), 2)
    elif key == 'a':
        eps = round(max(0.0001, eps - 0.001), 4)
    elif key == "A":
        eps = round(max(0.0001, eps - 0.0001), 4)
    elif key == 'd':
        eps = round(min(1.0, eps + 0.001), 4)
    elif key == "D":
        eps = round(min(1.0, eps + 0.0001), 4)
    elif key == 'q':
        return visual_weight, eps, True
    return visual_weight, eps, False

def main():
    visual_feats = []
    audio_feats = []

    video_paths = []

    index: faiss.IndexFlatL2 = load_index()
    video_files = list(Path("/mnt/nvme/clipsviewer/videos_test/PS5/CREATE/Video Clips/Grand Theft Auto V").glob("*.mp4"))
    random.shuffle(video_files)
    for video_file in video_files:
        video_extractor, audio_extractor = add_video(video_file)
        chunks = []
        best_index = (None, float('inf'))
        for chunk in audio_extractor:
            chunk_np = chunk[0].cpu().numpy().reshape(1, -1)
            video_paths.append(chunk[1])
            if index.ntotal > 0:
                D, I = index.search(chunk_np, 1)
                if D[0][0] < best_index[1]:
                    best_index = (I[0][0], D[0][0])
            chunks.append(chunk_np)
        for chunk in chunks:
            index.add(chunk)
        print(f"Most similar index: {video_paths[best_index[0]].name}, Distance: {best_index[1]}") if best_index[0] is not None else print("No similar index found.")

    print(f"Loaded FAISS index with {index.ntotal} entries.")

main()