import fitz  # PyMuPDF
import json
import os
import re

def extract_pdf_data(pdf_path, output_dir):
    """
    PDF에서 문제 텍스트를 추출하고, 
    지문과 보기 사이에 공간이 있을 경우 해당 영역을 '그림'으로 캡처하여 저장합니다.
    """
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    img_dir = os.path.join(output_dir, "images")
    if not os.path.exists(img_dir):
        os.makedirs(img_dir)

    print(f"[Info] PDF 파일 로드 중: {pdf_path}")
    doc = fitz.open(pdf_path)
    questions = []
    
    current_subject = "지적공무원 기출문제"
    
    # 2단 레이아웃 기준 설정 (페이지 절반)
    # 일반적인 A4 2단 편집의 경우
    
    total_processed = 0

    for page_num in range(doc.page_count):
        page = doc[page_num]
        width = page.rect.width
        height = page.rect.height
        mid_x = width / 2
        
        # 1. 텍스트 블록 가져오기 (정렬된 상태)
        # blocks: [(x0, y0, x1, y1, "text", block_no, block_type), ...]
        blocks = page.get_text("blocks")
        
        # 2. 컬럼별로 블록 분리 (좌/우)
        cols = [[], []] # 0: Left, 1: Right
        for b in blocks:
            # block_type=0 (Text)만 처리, type=1 (Image)은 제외할 수도 있으나
            # get_text("blocks")는 이미지는 보통 포함 안 함.
            if b[0] < mid_x:
                cols[0].append(b)
            else:
                cols[1].append(b)
        
        # 컬럼별 처리
        for col_idx, col_blocks in enumerate(cols):
            # Y축 기준으로 정렬 (위 -> 아래)
            col_blocks.sort(key=lambda x: x[1])
            
            # 문제 단위 그룹화 로직
            # "문 1.", "문 2." 등의 패턴으로 시작하는 블록을 찾음
            
            question_groups = []
            current_q_blocks = []
            
            # 정규식 패턴: 문 뒤에 숫자, 그 뒤에 점(.) 혹은 줄바꿈
            qt_pattern = re.compile(r'^\s*문\s*\d+\.')
            
            for b in col_blocks:
                text = b[4]
                # 문항 시작 패턴 발견 시
                if qt_pattern.match(text):
                    # 이전 문제가 있으면 저장
                    if current_q_blocks:
                        question_groups.append(current_q_blocks)
                        current_q_blocks = []
                    current_q_blocks.append(b)
                else:
                    # 문항 시작이 아니면 현재 문제의 일부로 간주 (보기 등)
                    if current_q_blocks:
                        current_q_blocks.append(b)
            
            # 마지막 문제 추가
            if current_q_blocks:
                question_groups.append(current_q_blocks)
                
            # 그룹화된 문제 데이터를 파싱 및 이미지 캡처
            for q_blocks in question_groups:
                q_data = process_question_group(doc, page, page_num, col_idx, q_blocks, img_dir, width, mid_x)
                if q_data:
                    # 고유 ID 부여
                    q_data['id'] = f"p{page_num+1}_c{col_idx}_{len(questions)}"
                    q_data['subject'] = current_subject # 과목 구분 로직이 있다면 여기서 업데이트
                    questions.append(q_data)
                    total_processed += 1

    # 결과 저장
    out_file = os.path.join(output_dir, "questions.js")
    # JS 파일 형태로 저장 (const questionData = [...])
    with open(out_file, "w", encoding="utf-8") as f:
        json_str = json.dumps(questions, ensure_ascii=False, indent=2)
        f.write(f"const questionData = {json_str};")
        
    # 호환성을 위해 json 파일도 저장
    with open(os.path.join(output_dir, "official_survey.json"), "w", encoding="utf-8") as f:
        json.dump(questions, f, ensure_ascii=False, indent=2)

    print(f"[Success] 추출 완료: 총 {len(questions)} 문제")
    return len(questions)

def process_question_group(doc, page, page_num, col_idx, blocks, img_dir, page_width, mid_x):
    """
    하나의 문제에 속한 텍스트 블록들을 분석하여
    지문, 보기, 그리고 '지문과 보기 사이의 빈 공간(이미지 영역)'을 추출함.
    """
    if not blocks:
        return None
        
    # 1. 텍스트 합치기 및 보기 분리
    full_text = ""
    
    # 지문 영역과 보기 영역을 구분하기 위한 좌표
    question_text_bottom = 0
    options_top = 99999
    
    # 보기(①, ②...)가 시작되는 블록 찾기
    opt_pattern = re.compile(r'[①②③④]')
    
    text_blocks = []
    option_blocks = []
    
    found_option = False
    
    for b in blocks:
        txt = b[4]
        # 보기가 포함된 블록인지 확인
        if opt_pattern.search(txt):
            found_option = True
            option_blocks.append(b)
            # 가장 위의 보기 블록 y0 좌표
            if b[1] < options_top:
                options_top = b[1]
        else:
            if not found_option:
                text_blocks.append(b)
                # 지문 블록 중 가장 아래 y1 좌표
                if b[3] > question_text_bottom:
                    question_text_bottom = b[3]
            else:
                # 보기가 나온 후의 텍스트도 보기 블록으로 간주 (긴 보기 등)
                option_blocks.append(b)

    # 텍스트 재구성
    question_text = ""
    for tb in text_blocks:
        question_text += tb[4].strip() + "\n"
        
    # 문제 번호 분리 (문 1. ...)
    num_match = re.match(r'(문\s*\d+\.)', question_text)
    num_str = num_match.group(1) if num_match else ""
    if num_str:
        question_text = question_text.replace(num_str, "").strip()
    
    # 보기 텍스트 추출
    options_text_combined = ""
    for ob in option_blocks:
        options_text_combined += ob[4].strip() + " "
    
    # 보기 리스트화
    options = []
    # ①, ② 등으로 자르기
    splits = re.split(r'[①②③④]', options_text_combined)
    # 첫 번째는 빈 문자열일 가능성 높음 (① 앞에 내용이 없다면)
    for s in splits:
        if s.strip():
            options.append(s.strip())
            
    # 정답 찾기 (단순히 4지선다 기본값 1로 설정, 별도 정답 파일 없으므로)
    # 실제 정답을 알려면 별도의 정답표 매핑이 필요함.
    answer = 1 
    
    # 2. ★ 이미지 영역(Gap) 캡처 로직 ★
    image_path = None
    
    # 지문 끝(question_text_bottom)과 보기 시작(options_top) 사이의 간격 계산
    # 보기가 없는 주관식이나, 보기가 바로 붙어있는 경우 제외
    
    has_gap_image = False
    
    if found_option and options_top > question_text_bottom:
        gap = options_top - question_text_bottom
        
        # 간격이 특정 임계값(예: 10픽셀) 이상이면 그림/표가 있다고 간주
        GAP_THRESHOLD = 10
        
        if gap > GAP_THRESHOLD:
            # 캡처할 영역 정의 (Rect)
            # x좌표는 해당 컬럼의 전체 너비 사용
            x0 = 0 if col_idx == 0 else mid_x
            x1 = mid_x if col_idx == 0 else page_width
            
            # 조금 여유를 두고 캡처 (위아래 2px)
            rect = fitz.Rect(x0 + 5, question_text_bottom + 1, x1 - 5, options_top - 1)
            
            # 유효성 검사 (높이가 양수인지)
            if rect.height > 5:
                # 이미지 파일명 생성
                # 특수문자 제거한 텍스트 일부 사용하거나 랜덤 ID
                safe_num = re.sub(r'\D', '', num_str) if num_str else f"Unknown_{page_num}"
                img_filename = f"q_{page_num+1}_{col_idx}_{safe_num}.png"
                full_img_path = os.path.join(img_dir, img_filename)
                
                # 캡처 (줌 2배)
                mat = fitz.Matrix(2, 2)
                pix = page.get_pixmap(matrix=mat, clip=rect)
                
                # 파일 크기가 너무 작으면(흰색 공백일 확률) 삭제
                # PNG 저장은 다소 느릴 수 있으므로, 일단 저장하고 사이즈 체크
                pix.save(full_img_path)
                
                if os.path.getsize(full_img_path) < 1500: # 1.5KB 미만은 삭제 (노이즈)
                     try:
                        os.remove(full_img_path)
                     except: pass
                else:
                    image_path = f"images/{img_filename}"
                    has_gap_image = True
                    print(f"  [Image] 그림 추출됨: {img_filename} ({gap:.1f}px)")

    return {
        "num": num_str.strip(),
        "text": question_text,
        "options": options[:4] if len(options) >= 4 else options,
        "image": image_path,
        "answer": answer,
        "explanation": "기출문제 드래그 캡처 방식 추출" if has_gap_image else ""
    }

if __name__ == "__main__":
    pdf_path = r"D:\AI_Class\지적공무원기출문제\지적공무원_기출문제.pdf"
    output_dir = r"D:\AI_Class\지적공무원기출문제"
    extract_pdf_data(pdf_path, output_dir)
