import json

p = r'c:\AI_Class\LicesneExam\quiz_app\questions.json'
with open(p, 'r', encoding='utf-8') as f:
    questions = json.load(f)

for q in questions:
    if 'source' not in q:
        q['source'] = '기출'

with open(p, 'w', encoding='utf-8') as f:
    json.dump(questions, f, ensure_ascii=False, indent=2)

print(f"총 {len(questions)}개 문항에 '기출' 태그를 추가했습니다.")
