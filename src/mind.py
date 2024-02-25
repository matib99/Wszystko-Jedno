from langchain_community.llms import Ollama
import subprocess
import time

#not necessary to import
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
    # Ensures closing already running ollama process
    run_bash_command("pgrep ollama | xargs kill", shell=True)
    time.sleep(5)
    # Assuming ollama serve & is meant to run in the background
    subprocess.Popen(["ollama", "serve"])
    print("Ollama serves...")
    time.sleep(5)
    subprocess.Popen(["ollama", "run", "mistral"])
    print("Ollama runs model...")
    llm = Ollama(model="mistral")
    #time.sleep(5)
    return llm

def thrust_thy_words_static(llm, text):
    try:
        result = llm.invoke(text)
    except Exception as inst:
        print(type(inst))
        print(inst)
    return result

def thrust_and_hear(llm, text): 
    query = text
    sentence = ""
    sentences = []

    for chunk in llm.stream(query):  # llm.stream is a placeholder for the streaming API
        sentence += chunk
        #print(chunk, end="")
        if chunk.endswith(('?', '.', '!', '...')):
            sentences.append(sentence)
            sentence = ""
            if len(sentences)==1:
                break
    return sentences