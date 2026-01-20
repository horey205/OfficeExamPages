import json
import os

base_path = r'c:\AI_Class\LicesneExam\quiz_app'
files = {
    'official_survey.json': '기출',
    'official_cs.json': '기출',
    'custom_survey.json': 'AI/예상',
    'custom_cs.json': 'AI/예상'
}

all_data = []

for filename, default_source in files.items():
    p = os.path.join(base_path, filename)
    if os.path.exists(p):
        with open(p, 'r', encoding='utf-8') as f:
            try:
                data = json.load(f)
                for q in data:
                    if default_source == '기출': q['source'] = '기출'
                    # subject is already in the q object
                all_data.extend(data)
            except:
                pass

js_content = f"const questionData = {json.dumps(all_data, ensure_ascii=False, indent=2)};"
with open(os.path.join(base_path, 'questions.js'), 'w', encoding='utf-8') as f:
    f.write(js_content)

print(f"Successfully integrated {len(all_data)} questions from 4 files into questions.js")
