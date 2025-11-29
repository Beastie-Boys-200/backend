import json

with open('chats/chat1.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

print(data['messages'][0]['text'])