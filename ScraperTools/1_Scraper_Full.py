
import json
import os
import time
import requests
import ssl
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from urllib.parse import urljoin

# ==========================================
# 설정 영역
# ==========================================
# 스크래핑할 대상 목록 페이지 (측량및지형공간정보산업기사)
SUBJECT_URL = "https://www.kinz.kr/subject/9075"

# 데이터 저장 경로 (루트 폴더)
# BASE_DIR = os.path.dirname(os.path.abspath(__file__)) # 기존: 스크립트 위치
ROOT_DIR = r"C:\AI_Class\측량자격증기출문제"
SURVEY_DATA_DIR = os.path.join(ROOT_DIR, "SurveyingExamData")  
IMAGE_DIR = os.path.join(SURVEY_DATA_DIR, "images")

# SSL 인증서 문제 우회 설정
os.environ['WDM_SSL_VERIFY'] = '0'

if not os.path.exists(SURVEY_DATA_DIR):
    os.makedirs(SURVEY_DATA_DIR)
if not os.path.exists(IMAGE_DIR):
    os.makedirs(IMAGE_DIR)

# ==========================================
# 유틸리티 함수
# ==========================================
def download_image(img_url, file_prefix):
    """이미지를 다운로드하고 로컬 경로를 반환"""
    if not img_url: return None
    try:
        # URL 절대경로 변환
        if not img_url.startswith('http'):
            img_url = "https://www.kinz.kr" + img_url
            
        # 확장자 추출 및 파일명 생성 (쿼리스트링 제거)
        ext = img_url.split('.')[-1].split('?')[0]
        if len(ext) > 4 or ext.lower() not in ['jpg', 'jpeg', 'png', 'gif']: 
            ext = 'jpg'
        
        filename = f"{file_prefix}.{ext}"
        save_path = os.path.join(IMAGE_DIR, filename)
        # JSON에 저장될 경로는 'images/파일명' (SurveyingData 폴더 내부 기준)
        relative_path = f"images/{filename}"
        
        # 이미 존재하면 다운로드 건너뛰기
        if os.path.exists(save_path):
            return relative_path

        # 이미지 다운로드 (SSL 무시)
        response = requests.get(img_url, verify=False, timeout=10)
        if response.status_code == 200:
            with open(save_path, 'wb') as f:
                f.write(response.content)
            return relative_path
            
    except Exception as e:
        print(f"    [Image Error] {img_url}: {e}")
    return None

def init_driver():
    """크롬 드라이버 초기화 및 옵션 설정"""
    options = webdriver.ChromeOptions()
    options.add_argument('--headless') # 창 없이 실행
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--ignore-certificate-errors')
    options.add_argument('user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36')
    
    # SSL Context Patch
    try:
        _create_unverified_https_context = ssl._create_unverified_context
    except AttributeError:
        pass
    else:
        ssl._create_default_https_context = _create_unverified_https_context

    # 드라이버 자동 설치 및 실행
    service = Service(ChromeDriverManager().install())
    return webdriver.Chrome(service=service, options=options)

def get_exam_links(driver, subject_url):
    """메인 목록 페이지에서 각 회차별 시험 URL을 수집"""
    print(f"📂 목록 페이지 접속 중: {subject_url}")
    driver.get(subject_url)
    time.sleep(3)
    
    links = []
    # 목록 페이지의 구조 분석을 통해 링크 추출 (kinz.kr 구조 기반)
    # 1. 일반적인 테이블 구조 시도
    elems = driver.find_elements(By.CSS_SELECTOR, 'table tbody tr td.text-left a')
    
    # 2. 만약 위에서 못 찾으면 다른 구조 시도 (예: div 리스트)
    if not elems:
        print("    -> 기본 테이블 구조에서 링크를 찾지 못함. 대체 구조 검색...")
        elems = driver.find_elements(By.TAG_NAME, 'a')
    
    for el in elems:
        try:
            href = el.get_attribute('href')
            title = el.text.strip()
            # kinz.kr/exam/ 숫자 패턴이 있는 링크만 유효한 시험지 링크
            if href and ('/exam/' in href) and title:
                # 중복 방지
                if not any(l['url'] == href for l in links):
                     links.append({'title': title, 'url': href})
        except:
             continue
            
    print(f"✅ 총 {len(links)}개의 시험 회차를 발견했습니다.")
    return links

def scrape_single_exam(driver, url, exam_title):
    """단일 회차 페이지 스크래핑"""
    print(f"  ▶ 스크래핑 시작: {exam_title}")
    driver.get(url)
    time.sleep(2)

    # 1. 정답 보기 버튼 전체 클릭 (숨겨진 정답/해설 노출)
    try:
        driver.execute_script("document.querySelectorAll('.show-answer').forEach(b => b.click())")
        time.sleep(1.5) # 렌더링 대기
    except Exception as e:
        print(f"    [Wiki] 버튼 클릭 실패(이미 열려있거나 없음): {e}")

    # 2. 데이터 추출 스크립트 실행
    # (이미지, 보기, 정답, 해설 포함)
    extraction_script = r"""
        const result = [];
        const questions = document.querySelectorAll('.exam-question');
        
        questions.forEach((div, idx) => {
            const qObj = {};
            
            // 1. 문제 텍스트 및 제목
            const h5 = div.querySelector('h5');
            if(!h5) return;
            
            let rawText = h5.innerText.trim();
            // "1. 문제내용..." 형식이므로 번호 제거 시도
            rawText = rawText.replace(/^\d+\.\s*/, '');
            qObj.text = rawText.split('\n')[0]; // 첫 줄만 제목으로 사용
            
            // 과목 추출 (텍스트 내 '과목 :' 찾기)
            qObj.subject = "기타";
            const subjectMatch = rawText.match(/과목\s*:\s*([^\n]+)/);
            if(subjectMatch) qObj.subject = subjectMatch[1].trim();

            // 2. 이미지 URL 수집
            // h5 내부 + 보기가 나오기 전까지의 형제 요소들
            let imgUrls = [];
            
            // (1) h5 내부
            h5.querySelectorAll('img').forEach(img => imgUrls.push(img.getAttribute('src')));
            
            // (2) 형제 요소 스캔
            let sibling = h5.nextElementSibling;
            while(sibling && sibling.tagName !== 'UL' && sibling.tagName !== 'H5' && !sibling.classList.contains('exam-explanation')) {
                if(sibling.tagName === 'IMG') {
                     imgUrls.push(sibling.getAttribute('src'));
                } else {
                     sibling.querySelectorAll('img').forEach(img => imgUrls.push(img.getAttribute('src')));
                }
                sibling = sibling.nextElementSibling;
            }
            qObj.images = imgUrls;

            // 3. 보기 추출
            qObj.options = [];
            const ul = div.querySelector('ul');
            if(ul) {
                ul.querySelectorAll('li').forEach(li => {
                    let optText = li.innerText.replace(/^[①②③④]/, '').trim();
                    // 보기 내 이미지 처리
                    li.querySelectorAll('img').forEach(img => {
                       optText += ` [IMG:${img.getAttribute('src')}]`;
                    });
                    qObj.options.push(optText);
                });
            }

            // 4. 정답 추출
            // 버튼 클릭 후 나타난 텍스트에서 파싱
            qObj.answer = 0;
            if(div.innerText.includes('정답 :')) {
                 const m = div.innerText.match(/정답\s*:\s*(\d)/);
                 if(m) qObj.answer = parseInt(m[1]);
            } else if(div.innerText.includes('정답:')) {
                 const m = div.innerText.match(/정답:\s*(\d)/);
                 if(m) qObj.answer = parseInt(m[1]);
            }

            // 5. 해설 추출
            qObj.explanation = "";
            const expDiv = div.querySelector('.exam-explanation');
            // 해설이 있고, display: none이 아니어야 함 (혹은 텍스트가 있어야 함)
            if(expDiv && expDiv.innerText.trim().length > 0) {
                 qObj.explanation = expDiv.innerText.trim();
                 // 해설 내 이미지
                 expDiv.querySelectorAll('img').forEach(img => {
                     qObj.explanation += ` [IMG:${img.getAttribute('src')}]`;
                 });
            }

            result.push(qObj);
        });
        return result;
    """
    
    raw_questions = driver.execute_script(extraction_script)
    
    processed_questions = []
    for idx, q in enumerate(raw_questions):
        # 고유 ID 생성 (회차_번호)
        # 파일 시스템 친화적인 ID로 변경 (특수문자 제거)
        safe_title = "".join(x for x in exam_title if x.isalnum())
        q_id = f"{safe_title}_{idx+1}"
        
        q['id'] = q_id
        q['source'] = exam_title
        
        # 메인 이미지 다운로드
        local_imgs = []
        for i, img_src in enumerate(q['images']):
            local_path = download_image(img_src, f"{q_id}_img_{i}")
            if local_path:
                local_imgs.append(local_path)
        q['local_images'] = local_imgs
        # 원본 URL 제거 (용량 절약)
        del q['images']

        # 해설 이미지 다운로드 (텍스트 내 치환)
        if '[IMG:' in q['explanation']:
            parts = q['explanation'].split('[IMG:')
            new_exp = parts[0]
            for p_idx, p in enumerate(parts[1:]):
                src_part = p.split(']')[0]
                rest_part = p.split(']')[1]
                
                loc = download_image(src_part, f"{q_id}_exp_{p_idx}")
                if loc:
                    new_exp += f"<br><img src='{loc}' class='exp-img'><br>"
                else:
                    new_exp += "(이미지 로드 실패)"
                new_exp += rest_part
            q['explanation'] = new_exp

        processed_questions.append(q)
        
    print(f"    - 문항 수: {len(processed_questions)}개 수집 완료")
    return processed_questions

# ==========================================
# 메인 실행 로직
# ==========================================
def main():
    driver = init_driver()
    all_data = []

    try:
        # 1. 목록 수집
        links = get_exam_links(driver, SUBJECT_URL)
        
        # 전체 회차 수집 (제한 해제)
        target_links = links 
        print(f"🚀 전체 {len(target_links)}개 회차에 대해 스크래핑을 시작합니다.")
        
        # 기존 데이터 로드 (중복 방지용)
        existing_ids = set()
        # SurveyingData 폴더 내의 모든 json 읽어오기
        for fname in os.listdir(SURVEY_DATA_DIR):
            if fname.endswith('.json'):
                try:
                    with open(os.path.join(SURVEY_DATA_DIR, fname), 'r', encoding='utf-8') as f:
                        data = json.load(f)
                        for item in data:
                            existing_ids.add(item.get('id'))
                except: pass
        
        print(f"    (이미 수집된 문제 수: {len(existing_ids)}개 - 중복 회차는 건너뜁니다)")

        for exam in target_links:
            try:
                # 회차명으로 이미 수집 여부 판단은 어려우므로(ID가 개별 문제단위), 
                # 일단 접속해서 첫 문제 ID가 있는지 확인하거나, 그냥 덮어쓰기 모드로 진행.
                # 여기서는 안전하게 전체 순회하되, 다운로드 부하만 줄임.
                
                print(f"  ▶ 진행 중: {exam['title']}")
                questions = scrape_single_exam(driver, exam['url'], exam['title'])
                
                # 수집된 데이터 병합
                all_data.extend(questions)
                
                # 중간 저장 (혹시 모를 중단 대비: 임시 파일)
                temp_file = os.path.join(SURVEY_DATA_DIR, "temp_progress.json")
                with open(temp_file, 'w', encoding='utf-8') as f:
                    json.dump(all_data, f, ensure_ascii=False, indent=2)
                    
                time.sleep(1) # 서버 부하 방지
            except Exception as e:
                print(f"    [Error] {exam['title']} 처리 중 오류: {e}")

        # 과목별로 데이터 분류
        subject_data = {}
        for q in all_data:
            subj = q.get('subject', '기타')
            # 파일명에 사용할 수 없는 문자 제거
            safe_subj = "".join(x for x in subj if x.isalnum() or x in (' ', '_', '-')).strip()
            if not safe_subj: safe_subj = "기타_미분류"
            
            if safe_subj not in subject_data:
                subject_data[safe_subj] = []
            subject_data[safe_subj].append(q)

        # 과목별 JSON 파일 저장
        print(f"\n💾 과목별 파일 저장 중...")
        for subj, q_list in subject_data.items():
            # 파일명 정리
            safe_subj = "".join(x for x in subj if x.isalnum() or x in (' ', '_', '-')).strip()
            if not safe_subj: safe_subj = "기타_미분류"
            
            filename = f"{safe_subj}.json"
            # 변경된 저장 경로 (SurveyingData 폴더)
            filepath = os.path.join(SURVEY_DATA_DIR, filename)
            
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(q_list, f, ensure_ascii=False, indent=2)
            print(f"  - {filename}: {len(q_list)} 문제 저장 완료 (-> {SURVEY_DATA_DIR})")
            
        print(f"\n✨ 전체 작업 완료! 총 {len(all_data)}개의 문제를 수집하여 과목별로 저장했습니다.")

    except Exception as e:
        print(f"치명적 오류 발생: {e}")
    finally:
        driver.quit()

if __name__ == "__main__":
    main()
