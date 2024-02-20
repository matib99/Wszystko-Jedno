from langchain_community.llms import Ollama
import subprocess
import time

#not necessary to import
def run_bash_command(command):
    result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    if result.returncode == 0:
        print("Output:", result.stdout)
    else:
        print("Error:", result.stderr)

def prepare_the_will():
    print("creating higher will...")
    run_bash_command(["ollama","serve"])
    run_bash_command(["ollama","run","mistral","&"])
    time.sleep(5) #to let ollama do initiate, maybe can be omitted

def thrust_thy_words_static(text):
    try:
        llm = Ollama(model="mistral")
        result = llm.invoke(text)
    except Exception as inst:
        print(type(inst))
        print(inst)
    return result

def thrust_and_hear(text, sentences): 
    """
    sentences should be used as chunks in llm.stream(query if possible, not)

    function hasn't been tested yet, this is only first step for near future implementation
    """
    query = text
    sentence = ""

    for chunk in llm.stream(query):  # llm.stream is a placeholder for the streaming API
        sentence += chunk
        if chunk.endswith(('?', '.', '!', '...')):
            print(sentence.strip())
            sentence = ""
         