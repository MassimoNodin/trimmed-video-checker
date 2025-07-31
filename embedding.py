from config import device, TEMP_AUDIO_DIR, TEMP_VIDEO_DIR
import torch
import os
import librosa
from transformers import ClapProcessor, ClapModel
processor = ClapProcessor.from_pretrained("laion/clap-htsat-unfused")
model = ClapModel.from_pretrained("laion/clap-htsat-unfused").to(device)

def embed_videos(video_chunks):
    """
    Function to embed video chunks.
    This function will handle the logic for embedding video chunks
    """

def embed_audio(audio_chunks):
    embeddings = []
    for audio_chunk in audio_chunks:
        try:
            
            print("Loading audio for CLAP...")
            audio_data, sr = librosa.load(str(audio_chunk), sr=48000, mono=True)
            print(f"Audio loaded with shape: {audio_data.shape}, Sample Rate: {sr}")
            waveform = torch.tensor(audio_data).unsqueeze(0)
            if waveform.shape[0] > 1:
                waveform = waveform.mean(dim=0, keepdim=True)
                chunk = chunk.squeeze().cpu().numpy()
                inputs = processor(audios=chunk, sampling_rate=48000, return_tensors="pt").to(device)
                with torch.no_grad():
                    emb = model.get_audio_features(**inputs).squeeze().cpu()
                embeddings.append(emb)
            os.unlink(audio_chunk)
        except Exception as e:
            print(f"CLAP audio processing failed for {audio_chunk}: {e}")
            if audio_chunk.exists():
                os.unlink(audio_chunk)
            continue
    return embeddings
    