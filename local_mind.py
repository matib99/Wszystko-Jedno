from flask import Flask, request, jsonify
from src import mind

app = Flask(__name__)

llm = mind.prepare_the_will()
print("LLM prepared")

@app.route('/generate_response', methods=['POST'])
def generate_response():
    data = request.json
    human_sentence = data.get('human_sentence')
    prompt = data.get('prompt')
    sentences_bef = data.get('sentences_bef')
    responses_bef = data.get('responses_bef')
    
    if not human_sentence or not prompt or sentences_bef is None or responses_bef is None:
        return jsonify({"error": "Invalid input"}), 400
    
    # llm = mind.prepare_the_will()
    response = mind.thrust_and_hear(llm, human_sentence, prompt, sentences_bef, responses_bef)
    
    return jsonify({"response": response})

if __name__ == "__main__":
    app.run(port=5000)