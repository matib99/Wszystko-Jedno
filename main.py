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
        default_mic="SM900T Microphone: USB Audio (hw:3,0)",
        # record_timeout=2,
        # phrase_timeout=3,
        pause_threshold=2
    )

    print("Preparing text generation...")
    llm = mind.prepare_the_will()

    print("Preparing audio generation...")
    audio_model = tongue.prepare_the_voice()

    print("Opening audio generation stream...")
    p, stream = tongue.prepare_the_stream()
    
    gpt_cond_latent, speaker_embedding = tongue.compute_latents(audio_model, "./samples/sample.wav")

    while True:
        if write_question:
            human_sentence = input("Write what thou wilt:\t")
        else:
            print("make thyself heard")
            human_sentence = vinput.get_phrase()
            print(f"Alas! Thine words resound! Thou exclaimed thusly:\n\t{human_sentence}")
        
        if human_sentence=="end":
            break

        response = mind.thrust_and_hear(llm, human_sentence)

        #printing the response sentence by sentence
        print("\nIt beared thee the fruit:\n")
        for i in response:
            print(i)
        
        #transforming response to voice
        for text in response:
            tongue.stream_loop(audio_model, gpt_cond_latent, speaker_embedding, stream, text=text, language="en", play_live=False)


    print("closing stream")
    stream.stop_stream()
    stream.close()

    p.terminate()

    #closes ollama process
    run_bash_command("pgrep ollama | xargs kill", shell=True)