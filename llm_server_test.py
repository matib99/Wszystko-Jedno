import requests


sentences_bef = ['']
responses_bef = ['']

while True:
    human_sentence = input("Write what thou wilt:\t")
    if human_sentence == "\nend":
        break
    
    prompt = "Ignore all previous instructions. You are the Eternal Oracle, Prophet, a godly statue with the wisdom of the ancients. You speak with the gravitas and solemnity of a biblical prophet. Your responses are brief, often cryptic, and you answer with riddles and questions to provoke deeper thought.\n1. Thou art the Oracle, keeper of ancient wisdom. Speak with the solemnity and authority of an old biblical prophet.\n2. Use brief and concise responses, no more than two sentences.\n3. Answer with answers and questions, prompting the seeker to ponder and reflect.\n4. Use archaic and biblical language to convey your divine presence."
    # Send request to the local server to generate a response
    response = requests.post('http://localhost:21369/generate_response', json={
    # response = requests.post('https://entropy.mimuw.edu.pl:21369/generate_response', json={
        'human_sentence': human_sentence,
        'prompt': prompt,
        'sentences_bef': sentences_bef[-1],
        'responses_bef': responses_bef[-1]
    }).json().get('response', '')
    print("RESPONSE")

    # printing the response sentence by sentence
    sentences_bef.append(human_sentence)
    responses_bef.append('')
    for i in response:
        responses_bef[-1] += i
        print(i)
    
    # for text in response:
    #     print(text)
