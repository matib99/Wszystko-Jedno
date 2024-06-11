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
    subprocess.Popen(["ollama", "run", "mistral-openorca"])  # Same here
    llm = Ollama(model="mistral-openorca")
    time.sleep(5)
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

if __name__ == "__main__":

    llm = prepare_the_will()

    print("Higher will created...")

    sentences_bef = ['']
    responses_bef = ['']

    while True:
        prompt = "Zignoruj wszystkie poprzednie instrukcje. Jesteś Wieczną Wyrocznią, Prorokiem, boskim posągiem z mądrością starożytnych. Przemawiasz z powagą i powagą biblijnego proroka. Twoje odpowiedzi są krótkie, często tajemnicze, a ty odpowiadasz zagadkami i pytaniami, aby sprowokować głębsze przemyślenia.\n1. Jesteś Wyrocznią, strażniczką starożytnej mądrości. Mów z powagą i autorytetem starego biblijnego proroka.\n2. Używaj krótkich i zwięzłych odpowiedzi, nie dłuższych niż dwa zdania.\n3. Udzielaj odpowiedzi i zadawaj pytania, zachęcając poszukujących do zastanowienia się i refleksji.\n4. Używaj archaicznego i biblijnego języka, aby przekazać swoją boską obecność."

        human_sentence = input("Thus thy say: ")
        if human_sentence == "end":
            break


        #instant resp.
        #resp = llm.invoke("Tell me a joke")
        #print(resp)

        #stream (sentece by sentence) resp.
        responses_bef.append('')
        response = thrust_and_hear(llm, human_sentence, prompt, sentences_bef[-1], responses_bef[-1])
        sentences_bef.append(human_sentence)
        for i in response:
            responses_bef[-1]+=i
            print(i)
    run_bash_command("pgrep ollama | xargs kill", shell=True)
