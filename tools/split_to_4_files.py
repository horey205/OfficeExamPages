import json
import os

base = r'c:\AI_Class\LicesneExam\quiz_app'
off_p = os.path.join(base, 'official_questions.json')

if os.path.exists(off_p):
    with open(off_p, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    survey = [q for q in data if q.get('subject') == '지적측량']
    cs = [q for q in data if q.get('subject') == '지적전산학개론']
    
    with open(os.path.join(base, 'official_survey.json'), 'w', encoding='utf-8') as f:
        json.dump(survey, f, ensure_ascii=False, indent=2)
    with open(os.path.join(base, 'official_cs.json'), 'w', encoding='utf-8') as f:
        json.dump(cs, f, ensure_ascii=False, indent=2)
    
    os.remove(off_p)
    print(f"기출 분리 완료: 측량({len(survey)}), 전산({len(cs)})")

# Create custom files if not exist
for name in ['custom_survey.json', 'custom_cs.json']:
    p = os.path.join(base, name)
    if not os.path.exists(p):
        with open(p, 'w', encoding='utf-8') as f:
            f.write('[]')

# Clean up custom_questions.json
old_custom = os.path.join(base, 'custom_questions.json')
if os.path.exists(old_custom):
    os.remove(old_custom)
