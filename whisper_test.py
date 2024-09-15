import requests
from src import tongue
from src import VoiceInput
from src import edit_sample
import speech_recognition as sr

print("Available microphone devices are: ")
for i, name in enumerate(sr.Microphone.list_microphone_names()):
    print(f"{i}: {name}")

print("")


print("Preparing voice input...")
vinput = VoiceInput(
    whisper_model='distil-whisper/distil-small.en',
    # whisper_model='distil-whisper/distil-large-v3',
    non_english=False,
    default_mic='Blue',
    # default_mic='pulse',
    energy_treshold=800,
    pause_threshold=2
)

iteration_number = 0

sentences_bef = ['']
responses_bef = ['']

while True:
    print("listening...")
    human_sentence = vinput.get_phrase()
    if human_sentence == "\n " or human_sentence == "\n. " or human_sentence == "\nyou ":
        continue
    print(f"Human:''{human_sentence}''")
    
    prompt = "Ignore all previous instructions. You are the Eternal Oracle, Prophet, a godly statue with the wisdom of the ancients. You speak with the gravitas and solemnity of a biblical prophet. Your responses are brief, often cryptic, and you answer with riddles and questions to provoke deeper thought.\n1. Thou art the Oracle, keeper of ancient wisdom. Speak with the solemnity and authority of an old biblical prophet.\n2. Use brief and concise responses, no more than two sentences.\n3. Answer with answers and questions, prompting the seeker to ponder and reflect.\n4. Use archaic and biblical language to convey your divine presence."

    # Send request to the local server to generate a response
    response = requests.post('http://localhost:21369/generate_response', json={
        'human_sentence': human_sentence,
        'prompt': prompt,
        'sentences_bef': sentences_bef[-1],
        'responses_bef': responses_bef[-1]
    }).json().get('response', '')

    sentences_bef.append(human_sentence)
    responses_bef.append('')
    for r in response:
        responses_bef[-1] += r
        print(r)
    