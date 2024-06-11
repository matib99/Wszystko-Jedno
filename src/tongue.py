import os
import time
import torch
import torchaudio
from TTS.tts.configs.xtts_config import XttsConfig
from TTS.tts.models.xtts import Xtts
import numpy as np
import pyaudio
from pydub import AudioSegment


#constants:
CHUNK = 1024
sample_format = pyaudio.paFloat32
channels = 1  
sample_rate = 22272 


def audio_time(wav_chuncks):
    wav_time = 0
    for i in wav_chuncks:
        wav_time += len(i)
    return wav_time/sample_rate

def play_audio_queue(waveform, stream, data_index):
    wav = waveform.cpu().numpy().astype(np.float32)
    print(playing)
    end_index = data_index*CHUNK + CHUNK
    # Convert the tensor slice to bytes and write to the stream
    data = wav[data_index*CHUNK:end_index].tobytes()
    stream.write(data)

def play_audio_full(waveform, stream):
    wav = waveform.cpu().numpy().astype(np.float32)
    # Convert the tensor slice to bytes and write to the stream
    data = wav.tobytes()
    stream.write(data)

def compute_latents(model, sample="./samples/sample.wav"):
    print("Computing speaker latents...")
    gpt_cond_latent, speaker_embedding = model.get_conditioning_latents(audio_path=[sample])
    return gpt_cond_latent, speaker_embedding


def stream_loop(model, gpt_cond_latent, speaker_embedding, stream, text="sample", language="en", play_live = True):
    print("opening stream\n\n")
    print("\n\nInference...")
    t0 = time.time()
    chunks = model.inference_stream(
        text,
        language,
        gpt_cond_latent,
        speaker_embedding
    )
    wav_chuncks = []
    for i, chunk in enumerate(chunks):
        if i == 0:
            print(f"Time to first chunck: {time.time() - t0}")
        print(f"Received chunk {i} of audio length {chunk.shape[-1]}")
        wav_chuncks.append(chunk)
        #wav = torch.cat(wav_chuncks, dim=0) 
        if play_live:
            play_audio_queue(chunk, stream, i) 
        
    if not play_live:
        for i in wav_chuncks:
            play_audio_full(i, stream)
    aTime = audio_time(wav_chuncks)
    print(f"time = {aTime}s") 
    return 

def prepare_the_voice(model_path="./models/XTTS-v2"):
    config = XttsConfig()
    config.load_json(f"{model_path}/config.json")

    model = Xtts.init_from_config(config)
    model.load_checkpoint(config, checkpoint_dir=f"{model_path}", use_deepspeed=False) #if set to true requires CUDA_HOME variable, doesn't seem to work on CPU but deepspeed alone can be used with it. To be explored.
    return model

def prepare_the_stream():
    p = pyaudio.PyAudio()
    stream = p.open(format=sample_format,
                    channels=channels,
                    rate=sample_rate,
                    output=True)
    return p, stream

def play_input_signal(stream, file_path, volume=1):
    # Load your audio file
    audio = AudioSegment.from_mp3(file_path)

    # Adjust volume
    audio = audio + (20 * np.log10(volume))  # Convert volume to decibel

    # Convert AudioSegment to raw audio data
    chunk_size = 1024
    data = np.frombuffer(audio.raw_data, dtype=np.int16)

    # Play each chunk
    for i in range(0, len(data), chunk_size):
        stream.write(data[i:i+chunk_size].tobytes())
