import json

with open('quiz_app/questions.json', 'r', encoding='utf-8') as f:
    questions = json.load(f)

for q in questions:
    prefix = q['id'].split('_')[0]
    p_num = int(prefix[1:])
    if p_num <= 25:
        q['subject'] = '지적측량'
    else:
        q['subject'] = '지적전산학개론'

with open('quiz_app/questions.json', 'w', encoding='utf-8') as f:
    json.dump(questions, f, ensure_ascii=False, indent=2)

print("Updated subjects for all questions.")
