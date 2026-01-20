
import json
import os
import shutil
import re

# ==========================================
# 1. 경로 설정 (루트 기준)
# ==========================================
ROOT_DIR = r"C:\AI_Class\측량자격증기출문제"

# 소스 (데이터)
DATA_SOURCE_DIR = os.path.join(ROOT_DIR, "SurveyingExamData")

# 소스 (웹 앱 템플릿 - 참고자료에서 복사)
TEMPLATE_DIR = os.path.join(ROOT_DIR, "참고자료_자격증기출문제", "CadaSurveyingExam")

# 타겟 (새로운 앱)
TARGET_APP_DIR = os.path.join(ROOT_DIR, "SurveyApp")
TARGET_IMAGES_DIR = os.path.join(TARGET_APP_DIR, "images")
TARGET_JS_PATH = os.path.join(TARGET_APP_DIR, "questions.js")

# ==========================================
# 2. 초기화 (폴더 생성)
# ==========================================
print(f"🚀 SurveyApp 구축 시작: {TARGET_APP_DIR}")

if not os.path.exists(TARGET_APP_DIR):
    os.makedirs(TARGET_APP_DIR)
    print("  ✅ 앱 폴더 생성 완료")

if not os.path.exists(TARGET_IMAGES_DIR):
    os.makedirs(TARGET_IMAGES_DIR)
    print("  ✅ 이미지 폴더 생성 완료")

# ==========================================
# 3. 템플릿 파일 복사 (HTML, CSS, JS)
# ==========================================
files_to_copy = ["index.html", "style.css", "script.js"]
for fname in files_to_copy:
    src = os.path.join(TEMPLATE_DIR, fname)
    dst = os.path.join(TARGET_APP_DIR, fname)
    if os.path.exists(src):
        shutil.copy2(src, dst)
        print(f"  📄 템플릿 복사: {fname}")
    else:
        print(f"  ⚠️ 원본 파일 없음: {fname}")

# ==========================================
# 4. 데이터 병합 및 questions.js 생성
# ==========================================
all_questions = []

print("  📂 데이터 처리 중...")
if os.path.exists(DATA_SOURCE_DIR):
    for fname in os.listdir(DATA_SOURCE_DIR):
        if fname.endswith(".json") and "backup" not in fname and "temp" not in fname:
            fpath = os.path.join(DATA_SOURCE_DIR, fname)
            try:
                with open(fpath, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    
                for item in data:
                    # 데이터 구조 변환
                    # Scraper answer: 0-based index -> App answer: 1-based index (needs verification, default +1)
                    # Note: 기타.json sample had answer:3 for 4 options. So 0-based.
                    try:
                        ans = int(item.get('answer', 0)) + 1
                    except:
                        ans = 1
                    
                    q_num_str = item.get('id', '0').split('_')[-1]
                    
                    new_q = {
                        "id": item.get('id'),
                        "num": f"문.\n{q_num_str}",
                        "text": item.get('text'),
                        "options": item.get('options'),
                        "answer": ans,
                        "explanation": item.get('explanation') or "해설이 없습니다.",
                        "subject": item.get('subject'),
                        "source": item.get('source'),
                        "image": None,
                        "difficulty": "중"
                    }
                    
                    # 이미지 처리
                    local_imgs = item.get('local_images', [])
                    if local_imgs:
                        src_rel = local_imgs[0] # images/filename.gif
                        # 원본 데이터 폴더 기준 경로
                        src_full = os.path.join(DATA_SOURCE_DIR, src_rel)
                        
                        if os.path.exists(src_full):
                            fname_img = os.path.basename(src_full)
                            dst_full = os.path.join(TARGET_IMAGES_DIR, fname_img)
                            
                            # 이미지 복사 (없으면 복사)
                            if not os.path.exists(dst_full):
                                shutil.copy2(src_full, dst_full)
                            
                            new_q['image'] = f"images/{fname_img}"
                    
                    all_questions.append(new_q)
                    
            except Exception as e:
                print(f"    ❌ 오류 ({fname}): {e}")

# Questions.js 쓰기
js_content = f"const questionData = {json.dumps(all_questions, ensure_ascii=False, indent=2)};"
with open(TARGET_JS_PATH, 'w', encoding='utf-8') as f:
    f.write(js_content)

print(f"  ✨ questions.js 생성 완료: 총 {len(all_questions)} 문제")
print("🎉 SurveyApp 구축 완료! (폴더: SurveyApp)")
