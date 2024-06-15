import requests
from src import tongue
from src import VoiceInput
from src import edit_sample
from src import play_input_signal

write_question = False

if __name__ == "__main__":
    print("Preparing voice input...")
    vinput = VoiceInput(
        whisper_model='small',
        non_english=False,
        energy_treshold=1000,
        pause_threshold=2
    )

    print("Preparing audio generation...")
    audio_model = tongue.prepare_the_voice()

    print("Opening audio generation stream...")
    p, stream = tongue.prepare_the_stream()
    
    sample_filename = "sample.wav"

    gpt_cond_latent, speaker_embedding = tongue.compute_latents(audio_model, f"./samples/{sample_filename}")
    iteration_number = 0

    sentences_bef = ['']
    responses_bef = ['']

    while True:
        if write_question:
            human_sentence = input("Write what thou wilt:\t")
        else:
            print("make thyself heard")
            human_sentence = vinput.get_phrase()
            if human_sentence == "\n " or human_sentence == "\n. " or human_sentence == "\nyou ":
                continue
            print(f"Alas! Thine words resound! Thou exclaimed thusly:''\n\t{human_sentence}''")
        
        if human_sentence == "\nend":
            break

        # distorting voice
        edit_sample(sample_filename, iteration_number * 1.5, int(iteration_number * 1.3), int(iteration_number * 0.5))
        gpt_cond_latent, speaker_embedding = tongue.compute_latents(audio_model, f"./samples/evolved_{sample_filename}")

        prompt = "Ignore all previous instructions. You are the Eternal Oracle, Prophet, a godly statue with the wisdom of the ancients. You speak with the gravitas and solemnity of a biblical prophet. Your responses are brief, often cryptic, and you answer with riddles and questions to provoke deeper thought.\n1. Thou art the Oracle, keeper of ancient wisdom. Speak with the solemnity and authority of an old biblical prophet.\n2. Use brief and concise responses, no more than two sentences.\n3. Answer with answers and questions, prompting the seeker to ponder and reflect.\n4. Use archaic and biblical language to convey your divine presence."

        # Send request to the local server to generate a response
        response = requests.post('http://localhost:5000/generate_response', json={
            'human_sentence': human_sentence,
            'prompt': prompt,
            'sentences_bef': sentences_bef[-1],
            'responses_bef': responses_bef[-1]
        }).json().get('response', '')

        # printing the response sentence by sentence
        sentences_bef.append(human_sentence)
        responses_bef.append('')
        print("\nIt beared thee the fruit:\n")
        for i in response:
            responses_bef[-1] += i
            print(i)
        
        # transforming response to voice
        for text in response:
            tongue.stream_loop(audio_model, gpt_cond_latent, speaker_embedding, stream, text=text, language="en", play_live=False)

        iteration_number += 1

    print("closing stream")
    stream.stop_stream()
    stream.close()

    p.terminate()

    #closes ollama process
    run_bash_command("pgrep ollama | xargs kill", shell=True)
