import chunk_video
from embedding import embed_audio, embed_videos
from pathlib import Path

def add_video(video_path: Path):
    print(f"Adding video: {video_path}")
    audio_chunks, video_chunks = chunk_video.chunk_video(video_path)
    embed_audio(audio_chunks)
    """
    Function to add a video to the system.
    This function will handle the logic for adding a new video,
    including any necessary validations and processing.
    """
    # Implementation of video addition logic goes here
    pass

def main():
    for video_file in Path("/mnt/nvme/clipsviewer/videos_test/PS5/CREATE/Video Clips/Grand Theft Auto V").glob("*.mp4"):
        add_video(video_file)

main()