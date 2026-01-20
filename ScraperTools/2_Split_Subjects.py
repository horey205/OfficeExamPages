
import json
import os
import re

# 경로 설정
# BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = r"C:\AI_Class\측량자격증기출문제"
SURVEY_DATA_DIR = os.path.join(ROOT_DIR, "SurveyingExamData")
INPUT_FILE = os.path.join(SURVEY_DATA_DIR, "기타.json")

# 과목 정의 (측량및지형공간정보산업기사 일반적 기준)
# 1과목: 측량학 (1~20)
# 2과목: 사진측량 및 원격탐사 (21~40)
# 3과목: 지리정보시스템 (41~60)
# 4과목: 응용측량 (61~80)
SUBJECT_MAP = {
    0: "측량학",
    1: "사진측량및원격탐사",
    2: "지리정보시스템",
    3: "응용측량"
}

def split_by_subject():
    if not os.path.exists(INPUT_FILE):
        print(f"❌ '{INPUT_FILE}' 파일이 없습니다. 스크래핑을 먼저 수행하세요.")
        return

    print("📂 데이터 분류 시작...")
    
    with open(INPUT_FILE, 'r', encoding='utf-8') as f:
        data = json.load(f)

    categorized_data = {v: [] for v in SUBJECT_MAP.values()}
    
    for q in data:
        # ID에서 문제 번호 추출 (예: ...2020822_1 -> 1)
        try:
            q_num = int(q['id'].split('_')[-1])
            
            # 80문제 기준 인덱스 (0~3)
            # 1~20 -> 0, 21~40 -> 1, ...
            # 100문제일 경우 5과목까지 확장 가능하나 산업기사는 보통 4과목(80문제)
            # 순환 구조 처리 (81번은 다시 1번처럼 취급될 수도 있으므로 % 20 로직보다는 범위 로직 사용)
            
            # 회차별 번호 리셋 가정 (각 회차는 1번부터 시작)
            # 하지만 JSON에는 모든 회차가 섞여있으므로 ID를 신뢰해야 함
            
            # 안전한 인덱스 계산 (문항수가 100개인 경우 대비)
            idx = (q_num - 1) // 20
            
            if idx in SUBJECT_MAP:
                subj_name = SUBJECT_MAP[idx]
                q['subject'] = subj_name # JSON 내부 과목명도 업데이트
                categorized_data[subj_name].append(q)
            else:
                # 80번 넘어가는 경우 (혹시 모를 오류 대비)
                q['subject'] = "기타_미분류"
                if "기타_미분류" not in categorized_data:
                    categorized_data["기타_미분류"] = []
                categorized_data["기타_미분류"].append(q)
                
        except Exception as e:
            print(f"⚠️ 문제 분류 실패 (ID: {q.get('id')}): {e}")

    # 파일 저장
    for subj, q_list in categorized_data.items():
        if not q_list: continue
        
        filename = f"{subj}.json"
        filepath = os.path.join(SURVEY_DATA_DIR, filename)
        
        # 기존 파일이 있다면 병합, 없으면 새로 생성
        if os.path.exists(filepath):
            with open(filepath, 'r', encoding='utf-8') as f:
                existing = json.load(f)
                # 중복 ID 체크하며 병합
                existing_ids = {item['id'] for item in existing}
                for new_q in q_list:
                    if new_q['id'] not in existing_ids:
                        existing.append(new_q)
                q_list = existing

        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(q_list, f, ensure_ascii=False, indent=2)
        print(f"  💾 {filename}: {len(q_list)} 문제 저장 완료")

    # 원본(기타.json)은 백업 후 삭제? 일단 유지하거나 삭제
    # os.remove(INPUT_FILE)
    print("✨ 모든 데이터가 과목별로 분류되었습니다.")

if __name__ == "__main__":
    split_by_subject()
