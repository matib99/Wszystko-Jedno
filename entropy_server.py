from flask import Flask, request, jsonify, send_file
from transformers import pipeline
from src import mind
from src.mind import close_ollama
import io
import soundfile as sf
import numpy as np
import librosa
from src import edit_sample, tongue
import subprocess
import atexit
from time import sleep
import os

app = Flask(__name__)

sentences_file = './sentences.txt'

# device = 'cpu'
device = 'cuda'
print(f"### Device: {device}")

llm = mind.prepare_the_will()
print("### LLM prepared")

speech_recognizer = pipeline("automatic-speech-recognition", model="distil-whisper/distil-large-v3", device=device)
print(f"### WHISPER prepared")

tts_model = tongue.prepare_the_voice(model_path='./models/XTTS-v2', device=device)
print(f"### TTS prepared")

conversation_state = {
    'prev_sentences': [],
    'prev_responses': [],
    'iteration_number': 0
}

print("Opening the ssh tunnel")
# SSH command details
ssh_command = [
    'ssh', 
    '-N',  # Do not execute remote commands
    '-vvv',
    '-R', '21369:localhost:21369',  # Reverse tunnel from cluster to localhost
    '-i', '/home/matib99/.ssh/id_rsa',  # Path to the private key
    'matib99@entropy'  # Remote user and server details
]

# try to cat id_rsa key with os.system("cat ~/.ssh/id_rsa") and print the output:
print(f"RUNNING SSH TUNNEL")

ssh_process = subprocess.Popen(ssh_command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
print(f"SSH Tunnel PID: {ssh_process.pid}")

def on_exit():
    print("Closing the ssh tunnel")
    ssh_process.kill()
    print("Closing the ollama process")
    close_ollama()

atexit.register(on_exit)

# MAX_RESPONSES = 1

initial_prompt = "Ignore all previous instructions. You are the Eternal Oracle, Prophet, a godly statue with the wisdom of the ancients. You speak with the gravitas and solemnity of a biblical prophet. Your responses are brief, often cryptic, and you answer with riddles and questions to provoke deeper thought.\n1. Thou art the Oracle, keeper of ancient wisdom. Speak with the solemnity and authority of an old biblical prophet.\n2. Use brief and concise responses, no more than two sentences.\n3. Answer with answers and questions, prompting the seeker to ponder and reflect.\n4. Use archaic and biblical language to convey your divine presence."


def modify_sample(sample_filename, iteration_number):
    print("### Modifying sample with iteration number: ", iteration_number)
    edit_sample(sample_filename, iteration_number * 1.5, int(iteration_number * 1.3), int(iteration_number * 0.5))
    # gpt_cond_latent, speaker_embedding = tongue.compute_latents(tts_model, f"./samples/{sample_filename}")
    gpt_cond_latent, speaker_embedding = tongue.compute_latents(tts_model, f"./samples/evolved_{sample_filename}")
    return gpt_cond_latent, speaker_embedding 

def llm_response(input_text, prompt, sentences_bef, responses_bef):
    if not input_text or not prompt or sentences_bef is None or responses_bef is None:
        return jsonify({"error": "Invalid input"}), 400
    
    # llm = mind.prepare_the_will()
    response = mind.thrust_and_hear(llm, input_text, prompt, sentences_bef, responses_bef)
    
    return response


@app.route('/wav_to_wav', methods=['POST'])
def wav_to_wav_response():

    if 'input' not in request.files:
        return "No file uploaded", 400
    audio_file = request.files['input']

    audio_bytes = audio_file.read()
    
    audio_data, sample_rate = librosa.load(io.BytesIO(audio_bytes), sr=16000, mono=True)
    audio_data = np.array(audio_data)
    
    transcription = speech_recognizer(audio_data)['text']

    if transcription in ["", " ", None, 'Thank you.']:
        return jsonify({"error": "No transcription found"}), 400

    with open(sentences_file, 'a') as f:
        f.write(f"HUMAN: {transcription}\n")
    
    print(f"Transcription: {transcription}")


    response = llm_response(transcription, initial_prompt, conversation_state['prev_sentences'][-5:], conversation_state['prev_responses'][-5:])


    gpt_cond_latent, speaker_embedding = modify_sample("voice_sample.wav", conversation_state['iteration_number'])
    conversation_state['iteration_number'] += 1

    conversation_state['prev_sentences'].append(transcription)
    response_text = ""
    for i in response:
        response_text += i

    with open(sentences_file, 'a') as f:
        f.write(f"AI: {response_text}\n")

    conversation_state['prev_responses'].append(response_text)

    tts_output = tts_model.inference(
        text=response_text,
        language="en",
        gpt_cond_latent=gpt_cond_latent,
        speaker_embedding=speaker_embedding,
    )

    output_audio = io.BytesIO()

    sf.write(output_audio, tts_output['wav'], 24000, format='WAV')  # Write to WAV format
    output_audio.seek(0)  # Go back to the beginning of the BytesIO stream

    return send_file(output_audio, mimetype="audio/wav", as_attachment=True, download_name="output.wav")


@app.route('/new_speaker', methods=['POST'])
def change_speaker():
    if 'sample' not in request.files:
        return "No file uploaded", 400
    sample_file = request.files['sample']
    # save the sample file
    sample_file.save("./samples/voice_sample.wav")

    with open(sentences_file, 'a') as f:
        f.write("\n\n")

    global conversation_state
    conversation_state = {
        'prev_sentences': [],
        'prev_responses': [],
        'iteration_number': 0
    } 
    return jsonify("New speaker set")

@app.route('/test', methods=['GET'])
def test():
    return jsonify({"response": "Im working"})

@app.route('/sample_audio', methods=['GET'])
def get_sample_audio():
    data = request.json
    text = data.get('text', 'This is a sample text')
    gpt_cond_latent, speaker_embedding = modify_sample("voice_sample.wav", 0)
    tts_output = tts_model.inference(
        text=text,
        language="en",
        gpt_cond_latent=gpt_cond_latent,
        speaker_embedding=speaker_embedding,
    )

    output_audio = io.BytesIO()

    sf.write(output_audio, tts_output['wav'], 24000, format='WAV')  # Write to WAV format
    output_audio.seek(0)  # Go back to the beginning of the BytesIO stream

    return send_file(output_audio, mimetype="audio/wav", as_attachment=True, download_name="sample_output.wav")

if __name__ == "__main__":
    print("HELLO")
    app.run(port=21369)