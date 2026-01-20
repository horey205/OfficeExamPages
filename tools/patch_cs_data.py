import json

p = r'c:\AI_Class\LicesneExam\quiz_app\questions.json'
with open(p, 'r', encoding='utf-8') as f:
    questions = json.load(f)

# 보강할 지적전산학개론 문제들 (예시 정답 및 해설 업데이트)
updates = {
    "p26_c0_q160": {
        "answer": 2,
        "explanation": "메타데이터(Metadata)는 '데이터에 관한 데이터'로 정의되며, 데이터의 내용, 품질, 조건 및 그 밖의 특성을 설명하는 정보를 말합니다."
    },
    "p26_c0_q161": {
        "answer": 3,
        "explanation": "래스터(Raster) 데이터는 그리드(격자) 형태의 픽셀로 구성되며, 사진 이미지나 위성 영상이 대표적입니다. 점, 선, 면으로 표현되는 것은 벡터(Vector) 데이터입니다."
    },
    "p26_c0_q162": {
        "answer": 4,
        "explanation": "수치지적도의 장점은 전산화를 통해 관리가 용이하고 정밀한 계산이 가능하다는 점입니다. 종이 도면의 신축 오차를 근본적으로 해결할 수 있습니다."
    },
    "p26_c1_q163": {
        "answer": 1,
        "explanation": "관계형 데이터베이스(RDBMS)의 표준 질의 언어는 SQL(Structured Query Language)입니다."
    },
    "p26_c1_q164": {
        "answer": 4,
        "explanation": "GIS의 5대 구성 요소는 하드웨어, 소프트웨어, 데이터, 사용자(인적자원), 방법론(절차)입니다."
    },
    "p27_c0_q170": {
        "answer": 2,
        "explanation": "스파게티 모델은 위상 관계(Topology) 정보가 없는 단순한 기하학적 데이터 구조를 말합니다."
    }
}

for q in questions:
    if q['id'] in updates:
        q.update(updates[q['id']])
        q['difficulty'] = '중' # 보강된 문제는 보통 난이도로 재배정

# 저장
with open(p, 'w', encoding='utf-8') as f:
    json.dump(questions, f, ensure_ascii=False, indent=2)

print("지적전산학개론 주요 문항의 정답과 해설이 보강되었습니다.")
