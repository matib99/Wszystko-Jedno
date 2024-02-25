# ear holds IFwhisper transcription and speech recognition recorders, all is encapsulated inside VoiceInput class
# tongue holds a reign over speech generation and cloning functions - those and constants by whom they succeed
# mind sends a signal to ollama to deploy the character, namely - mistral 7B quantized to 4 bits

from .tongue import audio_time
from .tongue import play_audio_queue
from .tongue import play_audio_full
from .tongue import compute_latents
from .tongue import stream_loop
from .tongue import prepare_the_voice
from .tongue import prepare_the_stream

from .ear import VoiceInput

from .mind import prepare_the_will
from .mind import thrust_thy_words_static
from .mind import thrust_and_hear

class Tongue:
    def __init__(self):
        self.audio_time = audio_time
        self.play_audio_queue = play_audio_queue
        self.play_audio_full = play_audio_full
        self.compute_latents = compute_latents
        self.stream_loop = stream_loop
        self.prepare_the_voice = prepare_the_voice
        self.prepare_the_stream = prepare_the_stream

class Mind:
    def __init__(self):
        self.prepare_the_will = prepare_the_will
        self.thrust_thy_words_static = thrust_thy_words_static
        self.thrust_and_hear = thrust_and_hear

tongue = Tongue()
mind = Mind()