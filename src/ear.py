from ctypes import *
from contextlib import contextmanager, redirect_stderr
import torch
from transformers import pipeline
import optimum #maybe can be omitted, idk
import speech_recognition as sr
import os
from sys import platform
import numpy as np

ERROR_HANDLER_FUNC = CFUNCTYPE(None, c_char_p, c_int, c_char_p, c_int, c_char_p)

def py_error_handler(filename, line, function, err, fmt):
    pass

c_error_handler = ERROR_HANDLER_FUNC(py_error_handler)

@contextmanager
def noalsaerr():
    asound = cdll.LoadLibrary('libasound.so')
    asound.snd_lib_error_set_handler(c_error_handler)
    yield
    asound.snd_lib_error_set_handler(None)

@contextmanager
def suppress_jack_errors():
    with open(os.devnull, 'w') as devnull:
        with redirect_stderr(devnull):
            yield

class VoiceInput():
    def __init__(self, whisper_model='small', non_english=False, energy_treshold=1000, default_mic='pulse', record_timeout=2, phrase_timeout=3, pause_threshold=1.5):
        self.recorder = sr.Recognizer()
        self.recorder.energy_threshold = energy_treshold
        self.dynamic_energy_treshold = True

        self.recorder.pause_threshold = 1.5

        self.pipe = pipeline("automatic-speech-recognition",
                "./models/whisper-model/",
                torch_dtype=torch.float32,
                device="cpu")

        with noalsaerr(), suppress_jack_errors(): #prevents some unimportant errors from being printed
            if 'linux' in platform:
                mic_name = default_mic
                if not mic_name or mic_name == 'list':
                    print("Available microphone devices are: ")
                    for index, name in enumerate(sr.Microphone.list_microphone_names()):
                        print(f"Microphone with name \"{name}\" found")
                    return
                else:
                    for index, name in enumerate(sr.Microphone.list_microphone_names()):
                        if mic_name in name:
                            source = sr.Microphone(
                                sample_rate=16000, device_index=index)
                            break
            else:
                    source = sr.Microphone(sample_rate=16000)

        self.source = source
        self.record_timeout = record_timeout
        self.phrase_timeout = phrase_timeout
        

        with noalsaerr(), source:
            self.recorder.adjust_for_ambient_noise(source)
    
    def get_phrase(self):
        with noalsaerr(), self.source:
            audio = self.recorder.listen(self.source)
        
        #transcribing audio to readable float32 format
        audio_np = np.frombuffer(audio.frame_data,dtype="int16")
        data = audio_np.astype(np.float32) / np.iinfo("int16").max

        print("\nVoice recorded, now transcribing\n")
        
        #converting to float32 recognizable by insanely fast whisper
        if data.dtype != np.float32:
            print("Converting to float32")
            data = waveform_data.astype(np.float32) / np.iinfo(waveform_data.dtype).max

        audio = {
            "path": None,
            "array": data,
            "sampling_rate": 16000        
        }

        outputs = self.pipe(audio)

        return outputs["text"]


# variables description:
#
# self.energy_threshold = 300  # minimum audio energy to consider for recording
# self.dynamic_energy_threshold = True
# self.dynamic_energy_adjustment_damping = 0.15
# self.dynamic_energy_ratio = 1.5
# self.pause_threshold = 0.8  # seconds of non-speaking audio before a phrase is considered complete
# self.operation_timeout = None  # seconds after an internal operation (e.g., an API request) starts before it times out, or ``None`` for no timeout
#
# self.phrase_threshold = 0.3  # minimum seconds of speaking audio before we consider the speaking audio a phrase - values below this are ignored (for filtering out clicks and pops)
# self.non_speaking_duration = 0.5  # seconds of non-speaking audio to keep on both sides of the recording