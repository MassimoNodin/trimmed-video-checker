import sys
import termios
import tty
import chunk_video
from embedding import load_index
from pathlib import Path
import faiss
import logging

logging.basicConfig(level=logging.INFO)

def add_video(video_path: Path, audio_index: faiss.IndexFlatIP, video_index: faiss.IndexFlatIP, video_paths: list):
    logging.info(f"\nAdding video: {video_path.name}")

    embed_extractor = chunk_video.chunk_video(video_path)
    chunks = []
    best_index = (None, float('inf'))
    length = 0
    start = False
    chunk_count = 0
    for audio_chunk, audio_segment_path, video_chunk, video_segment_path in embed_extractor:
        chunk_count += 1
        # print(f"Processing chunk {chunk_count} - Audio: {audio_segment_path.name}, Video: {video_segment_path.name if video_segment_path else 'None'}")
        chunk_np = audio_chunk.reshape(1, -1)
        chunk_video_np = video_chunk.reshape(1, -1)
        video_paths.append(audio_segment_path)
        if audio_index.ntotal > 0:
            D, I = audio_index.search(chunk_np, 1)
            if D[0][0] > 0.9:
                # print(f"Found Audio Match with {video_paths[I[0][0]].name} - Distance: {D[0][0]}")
                D1, I1 = video_index.search(chunk_video_np, 1)
                if I1[0][0] + 1 == I[0][0] or I1[0][0] - 1 == I[0][0]:
                    logging.info(f"Found Trimmed Video for {video_path.name} - Trimmed Video: {video_paths[I[0][0]].name} - Distance: {D[0][0]}")
                if not start:
                    # print(f"Start of trimmed video: {video_paths[I[0][0]].name}")
                    start = True
                length += 1
            elif start:
                # print(f"End of trimmed video: {video_paths[I[0][0]].name}, Length: {length}")
                start = False
                length = 0
            if D[0][0] < best_index[1]:
                best_index = (I[0][0], D[0][0])
        # print(f"Most similar index: {I[0][0]}, Distance: {D[0][0]}, Length: {length}") if best_index[0] is not None else print("No similar index found.")
        chunks.append((chunk_np, chunk_video_np))
    
    # print(f"Completed processing {chunk_count} chunks for {video_path.name}")
    # print(f"Adding {len(chunks)} embeddings to FAISS index...")
    for chunk in chunks:
        audio_index.add(chunk[0])
        video_index.add(chunk[1])
    # print(f"Successfully added video {video_path.name} to index. Total entries: {audio_index.ntotal}")
    # input()

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
    audio_index, video_index = load_index()
    video_paths = []
    # video_files = list(Path("/mnt/nvme/clipsviewer/videos_test/PS5/CREATE/Video Clips").glob("**/*.mp4"))
    video_files = list(Path("/mnt/nvme/clipsviewer/usb_mount/PS5/CREATE/Video Clips/Grand Theft Auto V").glob("**/*.mp4"))
    total_videos = len(video_files)
    print(f"Found {total_videos} video files to process")
    
    for i, video_file in enumerate(video_files, 1):
        print(f"\n{'='*50}")
        print(f"Processing video {i}/{total_videos}: {video_file.name}")
        print(f"{'='*50}")
        add_video(video_file, audio_index, video_index, video_paths)

    print(f"Loaded Audio FAISS index with {audio_index.ntotal} entries.")
    print(f"Loaded Video FAISS index with {video_index.ntotal} entries.")

main()