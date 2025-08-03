import cv2
from PIL import Image
from pathlib import Path
from config import device, TEMP_AUDIO_DIR, TEMP_VIDEO_DIR
import torch
import os
import faiss
import numpy as np
from transformers import ClapProcessor, ClapModel, CLIPModel, CLIPProcessor
import torchvision.transforms as T
processor_audio = ClapProcessor.from_pretrained("laion/clap-htsat-unfused")
model_audio = ClapModel.from_pretrained("laion/clap-htsat-unfused").to(device)
processor_video = CLIPProcessor.from_pretrained("openai/clip-vit-base-patch32")
model_video = CLIPModel.from_pretrained("openai/clip-vit-base-patch32").eval().to(device)

# Frame transform (match CLIP's expected format)
transform = T.Compose([
    T.Resize(224),
    T.CenterCrop(224),
    T.ToTensor(),
    T.Normalize(mean=[0.4815, 0.4578, 0.4082], std=[0.2686, 0.2613, 0.2758]),
])

def save_embedding(embedding, path: Path):
    """
    Save the embedding to a file.
    """
    np.save(path, embedding.cpu().numpy())

def check_embedding_exists(path: Path) -> bool:
    """
    Check if the embedding file exists.
    """
    return path.exists()

def load_embedding(path: Path) -> np.ndarray:
    """
    Load the embedding from a file.
    """
    if check_embedding_exists(path):
        return np.load(path)
    else:
        raise FileNotFoundError(f"Embedding file {path} does not exist.")

def load_index():
    """
    Function to load the FAISS index for audio embeddings.
    """
    # os.remove("index_audio.faiss") if Path("index_audio.faiss").exists() else None # Remove existing index to keep remaking during testing
    # os.remove("index_video.faiss") if Path("index_video.faiss").exists() else None # Remove existing index to keep remaking during testing
    index_audio_path = Path("index_audio.faiss")
    index_video_path = Path("index_video.faiss")
    if not index_audio_path.exists():
        print("Creating a new FAISS index for audio.")
        d = 512
        index = faiss.IndexFlatIP(d)
        faiss.write_index(index, str(index_audio_path))
    index_audio = faiss.read_index(str(index_audio_path))
    if not index_video_path.exists():
        print("Creating a new FAISS index for video.")
        d = 512
        index_video = faiss.IndexFlatIP(d)
        faiss.write_index(index_video, str(index_video_path))
    index_video = faiss.read_index(str(index_video_path))
    return index_audio, index_video

def embed_video_chunk(video_chunk, frame_rate=1):
    """
    Function to embed video chunks using torchcodec.
    This function will handle the logic for embedding video chunks
    """
    try:
        cap = cv2.VideoCapture(str(video_chunk))
        fps = cap.get(cv2.CAP_PROP_FPS)
        frame_interval = max(int(fps // frame_rate), 1)

        sampled_frames = []
        frame_idx = 0

        while cap.isOpened():
            success, frame = cap.read()
            if not success:
                break
            if frame_idx % frame_interval == 0:
                # Convert BGR (OpenCV) to RGB (PIL)
                frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                pil_img = Image.fromarray(frame_rgb)
                sampled_frames.append(pil_img)
            frame_idx += 1

        cap.release()

        if not sampled_frames:
            raise ValueError("No frames extracted from video.")

        # Process and embed
        inputs = processor_video(images=sampled_frames, return_tensors="pt", padding=True).to(device)
        with torch.no_grad():
            features = model_video.get_image_features(**inputs)
            features = features / features.norm(dim=-1, keepdim=True)
            return features.mean(dim=0, keepdim=True)
    except Exception as e:
        print(f"Error processing video chunk {video_chunk}: {e}")
        return torch.Tensor([])
    finally:
        if 'reader' in locals() and reader is not None:
            del reader
        if Path(video_chunk).exists():
            os.unlink(video_chunk)

def embed_audio_chunk(waveform):
    try:
        chunk = waveform.squeeze().cpu().numpy()
        inputs = processor_audio(audios=chunk, sampling_rate=48000, return_tensors="pt").to(device)
        with torch.no_grad():
            emb = model_audio.get_audio_features(**inputs).squeeze().cpu()
        return emb
    except Exception as e:
        print(f"Error processing audio chunk: {e}")
        return np.array([])