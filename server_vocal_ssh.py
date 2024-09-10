import paramiko
import json
from src import tongue
from src import VoiceInput
from src import edit_sample

write_question = False

def send_request_to_local_machine(human_sentence, prompt, sentences_bef, responses_bef):
    # Connect to the local machine via SSH
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect('your_local_machine_ip', username='your_username', password='your_password', port=22)
    
    # Prepare the request data
    data = json.dumps({
        'human_sentence': human_sentence,
        'prompt': prompt,
        'sentences_bef': sentences_bef,
        'responses_bef': responses_bef
    })
    
    # Use curl or a similar command on the local machine to interact with the local_mind.py Flask server
    command = f"curl -X POST -H 'Content-Type: application/json' -d '{data}' http://localhost:5000/generate_response"
    
    stdin, stdout, stderr = ssh.exec_command(command)
    response = stdout.read().decode('utf-8')
    ssh.close()
    
    return json.loads(response).get('response', '')

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
            if human_sentence.strip() == "":
                continue
            print(f"Alas! Thine words resound! Thou exclaimed thusly:\n\t{human_sentence}")
        
        if human_sentence == "end":
            break

        # Distorting voice
        edit_sample(sample_filename, iteration_number * 1.5, int(iteration_number * 1.3), int(iteration_number * 0.5))
        gpt_cond_latent, speaker_embedding = tongue.compute_latents(audio_model, f"./samples/evolved_{sample_filename}")

        prompt = "Ignore all previous instructions. You are the Eternal Oracle..."

        # Send the request over SSH to the local machine running `local_mind.py`
        response = send_request_to_local_machine(human_sentence, prompt, sentences_bef[-1], responses_bef[-1])

        # Printing the response
        sentences_bef.append(human_sentence)
        responses_bef.append(response)
        print("\nIt beared thee the fruit:\n")
        print(response)

        # Transforming response to voice
        tongue.stream_loop(audio_model, gpt_cond_latent, speaker_embedding, stream, text=response, language="en", play_live=False)

        iteration_number += 1

    print("closing stream")
    stream.stop_stream()
    stream.close()
    p.terminate()