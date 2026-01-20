import json

p = r'c:\AI_Class\LicesneExam\quiz_app\questions.json'
with open(p, 'r', encoding='utf-8') as f:
    questions = json.load(f)

subject = '지적전산학개론'
filtered = [q for q in questions if q['subject'] == subject]

total = len(filtered)
default_answer = len([q for q in filtered if q['answer'] == 1])
missing_explanation = len([q for q in filtered if '아직 등록되지 않았습니다' in q.get('explanation', '') or not q.get('explanation')])

print(f"과목: {subject}")
print(f"전체 문항 수: {total}")
print(f"정답이 1번(기본값)인 문항 수: {default_answer}")
print(f"해설이 없는 문항 수: {missing_explanation}")

# Sample check
if filtered:
    print("\n[첫 번째 문항 샘플]")
    print(json.dumps(filtered[0], ensure_ascii=False, indent=2))
