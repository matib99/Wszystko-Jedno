from src import tongue
from src import mind
from src import VoiceInput

write_question = False

if __name__ == "__main__":
    print("Preparing voice input...")
    vinput = VoiceInput(
        whisper_model='small',
        non_english=False,
        energy_treshold=1000,
        #default_mic='Blue Snowball: USB Audio (hw:1,0)',
        default_mic="default",
        # record_timeout=2,
        # phrase_timeout=3,
        pause_threshold=2
    )

    print("Preparing text generation...")
    mind.prepare_the_will()

    print("Preparing audio generation...")
    model = tongue.prepare_the_voice()

    print("Opening audio generation stream...")
    p = pyaudio.PyAudio()
    stream = p.open(format=sample_format,
                    channels=channels,
                    rate=sample_rate,
                    output=True)
    gpt_cond_latent, speaker_embedding = compute_latents("./polska_próbka.wav")

    while True:
        if write_question:
            human_sentence = input("Write what thou wilt:\t")
        else:
            print("make thyself heard")
            human_sentence = vinput.get_phrase()
            print(f"Thine words resound! Thou exclaimed what follows:\n\t{human_sentence}")
        
        if human_sentence=="end":
            break

        response = mind.thrust_thy_words_static(human_sentence)

        #transforming response to voice
        tongue.stream_loop(gpt_cond_latent, speaker_embedding, stream, text="response", language="pl", play_live=False)


    print("closing stream")
    stream.stop_stream()
    stream.close()

    p.terminate()