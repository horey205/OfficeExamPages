import json

p = r'c:\AI_Class\LicesneExam\quiz_app\questions.json'
with open(p, 'r', encoding='utf-8') as f:
    questions = json.load(f)

for i, q in enumerate(questions):
    print(f"{i+1}. {q['id']}: {q['text'][:50]}...")
