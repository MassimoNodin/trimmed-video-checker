import os
from audio import AudioExtractor
from video import VideoExtractor

class EmbedExtractor:
    def __init__(self, video_path, ranges):
        self.video_path = video_path
        self.ranges = ranges
        self.audio_extractor = AudioExtractor(video_path, ranges)
        self.video_extractor = VideoExtractor(video_path, ranges)

    def __iter__(self):
        return self
    
    def __next__(self):
        try:
            audio_embedding, audio_segment_path = next(self.audio_extractor)
            video_embedding, video_segment_path = next(self.video_extractor)
            return audio_embedding, audio_segment_path, video_embedding, video_segment_path
        except StopIteration:
            raise StopIteration