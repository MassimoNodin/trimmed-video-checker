class VideoRange:
    def __init__(self, start: float, end: float):
        self.start = start
        self.end = end

    def __repr__(self):
        return f"VideoRange(start={self.start}, end={self.end})"