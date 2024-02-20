import torch
from transformers import pipeline
import optimum
#temp
from scipy.io import wavfile
import numpy as np

if __name__=="__main__":
    pipe = pipeline("automatic-speech-recognition",
                    "./whisper-model/",
                    torch_dtype=torch.float32,
                    device="cpu")

    sample_rate, waveform_data = wavfile.read('../samples/sample.wav')

    print(waveform_data)

    if waveform_data.dtype != np.float32:
        print("Converting to float32")
        waveform_data = waveform_data.astype(np.float32) / np.iinfo(waveform_data.dtype).max


    print(sample_rate)
    print(waveform_data)

    audio = {
        "path": None,
        "array": waveform_data,
        "sampling_rate": sample_rate        
    }

    outputs = pipe(audio,
                #chunk_length_s=30,
                #batch_size=24,
                #return_timestamps=True
                )

    print(outputs["text"])
