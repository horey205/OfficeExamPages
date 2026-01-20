import json
import os

p = r'c:\AI_Class\LicesneExam\quiz_app\questions.json'
with open(p, 'r', encoding='utf-8') as f:
    questions = json.load(f)

official = [q for q in questions if q.get('source') == '기출' or 'source' not in q]
custom = [q for q in questions if q.get('source') != '기출' and 'source' in q]

official_path = r'c:\AI_Class\LicesneExam\quiz_app\official_questions.json'
custom_path = r'c:\AI_Class\LicesneExam\quiz_app\custom_questions.json'

with open(official_path, 'w', encoding='utf-8') as f:
    json.dump(official, f, ensure_ascii=False, indent=2)

with open(custom_path, 'w', encoding='utf-8') as f:
    json.dump(custom, f, ensure_ascii=False, indent=2)

print(f"분리 완료: 기출({len(official)}문항), 신규/예상({len(custom)}문항)")
