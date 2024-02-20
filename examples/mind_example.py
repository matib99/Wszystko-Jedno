from langchain_community.llms import Ollama
import subprocess

run_bash_command(["ollama","serve"])
run_bash_command(["ollama","run","mistral","&"])
time.sleep(5) #to let ollama do initiate, maybe can be omitted

llm = Ollama(model="mistral")

#instant resp.
resp = llm.invoke("Tell me a joke")
print(resp)

def thrust_and_hear(text):
    query = text
    sentence = ""

    for chunk in llm.stream(query):  # llm.stream is a placeholder for the streaming API
        sentence += chunk
        if chunk.endswith(('?', '.', '!', '...')):
            print(sentence.strip())
            sentence = ""

#stream (sentece by sentence) resp.
thrust_and_hear("Tell me a joke")
