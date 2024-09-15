import speech_recognition as sr
import requests
from time import sleep, time
from io import BytesIO
from pydub import AudioSegment
from pydub.playback import play

# URL of the Flask endpoint
ADJUST_MIC_EVERY_S = 60
PAUSE_THRESHOLD = 1 # 1.5
MIN_DURATION = 2.0 + PAUSE_THRESHOLD
ENERGY_THRESHOLD = 64000 # 16000


def select_microphone():
    # List all available microphones
    mic_list = sr.Microphone.list_microphone_names()
    print("Available Microphones:")
    for i, mic_name in enumerate(mic_list):
        print(f"{i}: {mic_name}")
    
    # Let the user select the microphone by index
    mic_index = int(input("Select the microphone by index: "))
    
    return mic_index


def play_received_audio(audio_data):
    # Load audio from BytesIO stream and play it
    audio_segment = AudioSegment.from_file(audio_data, format="wav")
    play(audio_segment)  # Play the received audio

def initialize_microphone(mic_index, sample_rate=16000, energy_treshold=1000):
    recognizer = sr.Recognizer()
    recognizer.energy_threshold = energy_treshold
    recognizer.dynamic_energy_threshold = True
    
    recognizer.pause_threshold = PAUSE_THRESHOLD

    microphone = sr.Microphone(
        device_index=mic_index, 
        sample_rate=sample_rate,
    )
    return recognizer, microphone

def adjust_microphone_for_noise(recognizer, microphone):
    with microphone as source:
        print("Adjusting for ambient noise, please wait...")
        recognizer.adjust_for_ambient_noise(source)
        print(f"Ambient noise level set to {recognizer.energy_threshold}")

def listen_for_speech(recognizer, microphone):
    if microphone is None:
        print("Microphone is not initialized properly.")
        return None
    audio = None
    with microphone as source:
        if source is None:
            print("Microphone is NONENOEE")
            
        print("Listening for speech with timeout and phrase time limit...")
        try:
            # Listen with a 60-second timeout and 30-second phrase limit
            audio = recognizer.listen(source, timeout=60, phrase_time_limit=30)

            print("Audio captured successfully.")
        except sr.WaitTimeoutError:
            print("No speech detected within the timeout period.")
        duration = len(audio.frame_data) / (audio.sample_rate * audio.sample_width)
        if duration < MIN_DURATION:
            print(f"Audio duration {duration:.2f} is too short, discarding.")
            return None
    return audio

def echo(recognizer, microphone):
    audio = listen_for_speech(recognizer, microphone)
    if audio is None:
        return
    audio_data = BytesIO(audio.get_wav_data())
    play_received_audio(audio_data)

if __name__ == "__main__":
    # Select the microphone
    mic_index = select_microphone()
    print(f"Selected microphone index: {mic_index}")
    print("Initializing the microphone...") 
    recognizer, microphone = initialize_microphone(
        mic_index, 
        sample_rate=48000,
        energy_treshold=ENERGY_THRESHOLD
    )
    adjust_microphone_for_noise(recognizer, microphone)
    adjusting_time = time()

    while True:
        # Listen for speech
        print("Listening for speech...")
        echo(recognizer, microphone) 
        # Check if it's time to adjust the microphone for noise again
        if time() - adjusting_time > ADJUST_MIC_EVERY_S:
            adjust_microphone_for_noise(recognizer, microphone)
            adjusting_time = time()
