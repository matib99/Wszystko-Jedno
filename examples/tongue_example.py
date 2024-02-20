import os
import time
import torch
import torchaudio
from TTS.tts.configs.xtts_config import XttsConfig
from TTS.tts.models.xtts import Xtts
import numpy as np
import pyaudio


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
    data = wav[data_index:end_index].tobytes()
    stream.write(data)

def play_audio_full(waveform, stream):
    wav = waveform.cpu().numpy().astype(np.float32)
    # Convert the tensor slice to bytes and write to the stream
    data = wav.tobytes()
    stream.write(data)

def compute_latents(sample="../samples/sample.wav"):
    print("Computing speaker latents...")
    gpt_cond_latent, speaker_embedding = model.get_conditioning_latents(audio_path=["../samples/sample.wav"])
    return gpt_cond_latent, speaker_embedding


def stream_loop(gpt_cond_latent, speaker_embedding, stream, text="this is only a sample", language="en", play_live = True):
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


if __name__=="__main__":
    
    #opening model (from https://huggingface.co/coqui/XTTS-v2)
    print("Loading model...")
    config = XttsConfig()
    config.load_json("./XTTS-v2/config.json")

    model = Xtts.init_from_config(config)
    model.load_checkpoint(config, checkpoint_dir="./XTTS-v2/", use_deepspeed=False) #if set to true requires CUDA_HOME variable, doesn't seem to work on CPU but deepspeed alone can be used with it. To be explored.

    print("opening stream")
    p = pyaudio.PyAudio()
    stream = p.open(format=sample_format,
                    channels=channels,
                    rate=sample_rate,
                    output=True)


    #computing latents for specific sample
    gpt_cond_latent, speaker_embedding = compute_latents("../samples/sample.wav")

    stream_loop(gpt_cond_latent, speaker_embedding, stream, text="puritanic cows drop the ball into the pool of tears", language="en", play_live=False) #play_live should be set to True whenever audio generates faster than it lasts




    print("closing stream")
    stream.stop_stream()
    stream.close()

    p.terminate()
