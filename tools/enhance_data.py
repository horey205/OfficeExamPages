import json
import os
import re

def enhance_questions(json_path):
    with open(json_path, 'r', encoding='utf-8') as f:
        questions = json.load(f)

    # 난이도 분류 기준 (키워드 기반)
    hard_keywords = ['계산', '좌표', '면적', '공식', '사인법칙', '오차', '표준편차', '√']
    medium_keywords = ['법률', '시행령', '규정', '절차', '방법', '기준', '옳지 않은']
    
    for q in questions:
        # 1. 난이도(difficulty) 필드 추가 (이미 있으면 유지)
        if 'difficulty' not in q:
            # 기본 로직: 계산식이 있거나 숫자가 많은 경우 '상'
            text_and_options = q['text'] + "".join(q['options'])
            
            if any(k in text_and_options for k in hard_keywords) or len(re.findall(r'\d+\.?\d*', q['text'])) > 5:
                q['difficulty'] = '상'
            elif any(k in text_and_options for k in medium_keywords) or len(q['text']) > 60:
                q['difficulty'] = '중'
            else:
                q['difficulty'] = '하'
        
        # 2. 태그(tags) 필드 추가
        if 'tags' not in q:
            tags = []
            if any(k in q['text'] for k in ['법', '시행령', '규정']): tags.append('법규')
            if any(k in q['text'] for k in ['계산', '좌표', '면적']): tags.append('계산')
            if 'image' in q and q['image']: tags.append('도면')
            q['tags'] = tags if tags else ['이론']

        # 3. 해설(explanation)이 없는 경우 기본 문구 추가
        if 'explanation' not in q or not q['explanation']:
            q['explanation'] = "이 문제에 대한 상세 해설이 아직 등록되지 않았습니다. 관리자 모드에서 추가해 주세요."

    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(questions, f, ensure_ascii=False, indent=2)

    return len(questions)

if __name__ == "__main__":
    path = r"C:\AI_Class\LicesneExam\quiz_app\questions.json"
    count = enhance_questions(path)
    print(f"Successfully enhanced {count} questions with difficulty and tags.")
