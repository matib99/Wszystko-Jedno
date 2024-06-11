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
    subprocess.Popen(["ollama", "run", "mistral-openorca"])
    print("Ollama runs model...")
    llm = Ollama(model="mistral-openorca")
    #time.sleep(5)
    return llm

def thrust_thy_words_static(llm, text, prompt, previous_sentence, previous_response):

    # Construct the conversation history with the most recent previous sentence and response
    if previous_sentence and previous_response:
        conversation_history = f"{previous_sentence}\n{previous_response}\n"
    else:
        conversation_history = ""

    # Add the current user input
    conversation_history += f"{text}\n"

    # Combine the prompt with the conversation history
    combined_prompt = f"{prompt}\n\n{conversation_history}"

    try:
        result = llm.invoke(combined_prompt)
    except Exception as inst:
        print(type(inst))
        print(inst)
        result = None

    return result

def thrust_and_hear(llm, text, prompt, previous_sentence, previous_response):

    # Construct the conversation history with the most recent previous sentence and response
    if previous_sentence and previous_response:
        conversation_history = f"User: {previous_sentence}\nProphet: {previous_response}\n"
    else:
        conversation_history = ""

    # Add the current user input
    query = f"{prompt}\n\n{conversation_history}User: {text}\nProphet: "
    sentences = []
    sentence = ""
    print("Query reads like following: ", query)
    for chunk in llm.stream(query):  # llm.stream is a placeholder for the streaming API
        sentence += chunk
        #print(chunk, end="")
        if chunk.endswith(('?', '.', '!', '...')):
            sentences.append(sentence)
            sentence = ""
            if len(sentences)==1:
                break
    return sentences
