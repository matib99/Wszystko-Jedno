from langchain_community.llms import Ollama
import subprocess
import time

def run_bash_command(command, shell=False):
    if shell:
        # When using shell=True, command must be a string
        result = subprocess.run(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    else:
        # When not using shell, command is a list
        result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    if result.returncode == 0:
        print("Output:", result.stdout)
    else:
        print("Error:", result.stderr)

def prepare_the_will():
    print("creating higher will...")
    # Ensures closing already running ollama process
    run_bash_command("pgrep ollama | xargs kill", shell=True)
    time.sleep(5)
    # Assuming ollama serve & is meant to run in the background
    subprocess.Popen(["ollama", "serve"])  # Removed &, subprocess.Popen runs it in the background
    time.sleep(5)
    subprocess.Popen(["ollama", "run", "mistral"])  # Same here
    llm = Ollama(model="mistral")
    time.sleep(5)
    return llm

def thrust_thy_words_static(text):
    try:
        result = llm.invoke(text)
    except Exception as inst:
        print(type(inst))
        print(inst)
    return result

def thrust_and_hear(text): 
    query = text
    sentence = ""
    sentences = []

    for chunk in llm.stream(query):  # llm.stream is a placeholder for the streaming API
        sentence += chunk
        if chunk.endswith(('?', '.', '!', '...')):
            sentences.append(sentence)
            sentence = ""
    return sentences

if __name__ == "__main__":

    llm = prepare_the_will()

    print("Higher will created...")

    #instant resp.
    resp = llm.invoke("Tell me a joke")
    print(resp)

    #stream (sentece by sentence) resp.
    response = thrust_and_hear("Tell me a joke")
    for i in response:
        print(i)
    run_bash_command("pgrep ollama | xargs kill", shell=True)
