from pathlib import Path
from config import device, TEMP_AUDIO_DIR, TEMP_VIDEO_DIR
import torch
import os
import librosa
import faiss
from transformers import ClapProcessor, ClapModel
processor = ClapProcessor.from_pretrained("laion/clap-htsat-unfused")
model = ClapModel.from_pretrained("laion/clap-htsat-unfused").to(device)

def load_index():
    """
    Function to load the FAISS index for audio embeddings.
    """
    os.remove("index.faiss") if Path("index.faiss").exists() else None # Remove existing index to keep remaking during testing
    index_path = Path("index.faiss")
    if not index_path.exists():
        print("Creating a new FAISS index.")
        d = 512
        index = faiss.IndexFlatL2(d)
        faiss.write_index(index, str(index_path))
    index = faiss.read_index(str(index_path))
    return index

def embed_videos(video_chunks):
    """
    Function to embed video chunks.
    This function will handle the logic for embedding video chunks
    """
    for video_chunk in video_chunks:
        os.unlink(video_chunk) if video_chunk.exists() else None
    return []

def embed_audio(audio_chunks):
    embeddings = []
    for audio_chunk in audio_chunks:
        try:
            audio_data, sr = librosa.load(str(audio_chunk), sr=48000, mono=True)
            waveform = torch.tensor(audio_data).unsqueeze(0)
            if waveform.shape[0] > 1:
                waveform = waveform.mean(dim=0, keepdim=True)
            chunk = waveform.squeeze().cpu().numpy()
            inputs = processor(audios=chunk, sampling_rate=48000, return_tensors="pt").to(device)
            with torch.no_grad():
                emb = model.get_audio_features(**inputs).squeeze().cpu()
            embeddings.append(emb)
            os.unlink(audio_chunk)
        except Exception as e:
            if audio_chunk.exists():
                os.unlink(audio_chunk)
            continue
    return embeddings
    