import fitz  # PyMuPDF
import json
import os
import sys
if sys.platform.startswith('win'):
    sys.stdout.reconfigure(encoding='utf-8')
    sys.stderr.reconfigure(encoding='utf-8')

import re
import shutil

def main():
    pdf_path = r"D:\AI_Class\지적공무원기출문제\지적공무원_기출문제.pdf"
    output_dir = r"D:\AI_Class\지적공무원기출문제"
    img_dir = os.path.join(output_dir, "images")

    # 1. 이미지 폴더 초기화
    if os.path.exists(img_dir):
        print(f"[Info] 기존 이미지 폴더 정리 중: {img_dir}")
        shutil.rmtree(img_dir)
    os.makedirs(img_dir)

    print(f"[Info] PDF 로드 중: {pdf_path}")
    doc = fitz.open(pdf_path)
    questions = []
    
    total_q_count = 0

    for page_num in range(doc.page_count):
        page = doc[page_num]
        width = page.rect.width
        height = page.rect.height
        mid_x = width / 2
        
        print(f"[Info] Processing Page {page_num + 1}/{doc.page_count}...")
        
        # 텍스트 블록 가져오기 (세로 위치 정렬)
        blocks = page.get_text("blocks")
        
         # 컬럼별 분리 (0:좌, 1:우)
        cols = [[], []] 
        for b in blocks:
            if b[0] < mid_x: cols[0].append(b)
            else: cols[1].append(b)
            
        # 컬럼별 순회
        for col_idx, col_blocks in enumerate(cols):
            # y값 기준 정렬
            col_blocks.sort(key=lambda x: x[1])
            
            # 문제별 그룹핑
            question_indices = []
            qt_pattern = re.compile(r'^\s*(?:문)?\s*\d+\.')
            
            for i, b in enumerate(col_blocks):
                if qt_pattern.match(b[4]):
                    question_indices.append(i)
            
            # 각 문제 처리
            for i in range(len(question_indices)):
                start_idx = question_indices[i]
                end_idx = question_indices[i+1] if i + 1 < len(question_indices) else len(col_blocks)
                
                # 해당 문제의 블록들
                q_blocks = col_blocks[start_idx:end_idx]
                if not q_blocks: continue
                
                # 영역 계산 (y_min ~ y_max)
                y_min = q_blocks[0][1]
                
                # y_max: 마지막 블록의 바닥
                y_max = q_blocks[-1][3]
                
                # 조금 더 여유를 둠 (글자가 잘리지 않게)
                y_min = max(0, y_min - 5)
                y_max = min(height, y_max + 10)
                
                # x 영역 (컬럼 전체 너비 사용)
                x0 = 0 if col_idx == 0 else mid_x
                x1 = mid_x if col_idx == 0 else width
                
                # -----------------------------
                # 1. 이미지 캡처 (드로잉/이미지가 있는 경우만)
                # -----------------------------
                # y_max 재계산: 이 문제의 끝부터 다음 문제의 시작(또는 페이지 끝)까지 포함하도록
                # 이렇게 하면 텍스트 블록 사이에 있는 그림(Drawings)도 캡처됨
                
                if i + 1 < len(question_indices):
                    # 다음 문제가 있으면, 다음 문제의 시작 y값 바로 위까지
                    next_q_idx = question_indices[i+1]
                    next_y = col_blocks[next_q_idx][1]
                    y_max = max(y_max, next_y - 5)
                else:
                    # 마지막 문제면, 마지막 텍스트 블록 아래로 여유 공간 추가
                    # 너무 많이 잡으면 페이지 번호가 나올 수 있으므로 적당히
                    y_max = min(height - 20, q_blocks[-1][3] + 60)

                rect = fitz.Rect(x0, y_min, x1, y_max)
                
                # 문제 번호 추출
                first_text = q_blocks[0][4].strip()
                num_match = qt_pattern.match(first_text)
                num_str = num_match.group(0) if num_match else f"Q{total_q_count+1}"
                
                print(f"  - Processing Question: {num_str} (Page {page_num+1}, Col {col_idx})")
                
                # 파일명 생성
                safe_num = re.sub(r'\D', '', num_str)
                if not safe_num: safe_num = str(total_q_count)
                
                img_filename = f"q_{page_num+1}_{col_idx}_{safe_num}.png"
                full_img_path = os.path.join(img_dir, img_filename)
                image_rel_path = None

                # 그래픽/이미지 포함 여부 확인
                has_graphics = False
                
                # 1) Drawings 확인
                drawings = page.get_drawings()
                for d in drawings:
                    d_rect = d["rect"]
                    if rect.intersects(d_rect):
                        has_graphics = True
                        break
                
                # 2) Embedded Images 확인
                if not has_graphics:
                    img_infos = page.get_image_info()
                    for img in img_infos:
                        i_rect = fitz.Rect(img["bbox"])
                        if rect.intersects(i_rect):
                            has_graphics = True
                            break

                # 캡처 진행
                if has_graphics:
                    mat = fitz.Matrix(2, 2)
                    try:
                        pix = page.get_pixmap(matrix=mat, clip=rect)
                        pix.save(full_img_path)
                        image_rel_path = f"images/{img_filename}"
                    except Exception as e:
                        print(f"[Error] 이미지 저장 실패: {e}")
                
                # -----------------------------
                # 2. 텍스트 데이터 추출
                # -----------------------------
                full_text = "\n".join([b[4].strip() for b in q_blocks])
                
                # 제목에서 문제 번호 제거
                if num_match:
                    title_dirty = full_text.split('\n')[0] # 첫 줄
                    text_body = full_text.replace(num_match.group(0), "", 1).strip()
                else:
                    text_body = full_text

                # 보기 분리 (간단히)
                options = []
                # ①, ② 등으로 스플릿 시도
                split_opts = re.split(r'[①②③④]', text_body)
                if len(split_opts) > 1:
                    q_text_only = split_opts[0].strip()
                    options = [o.strip() for o in split_opts[1:] if o.strip()]
                else:
                    q_text_only = text_body
                    
                # -----------------------------
                # 3. 데이터 저장
                # -----------------------------
                q_data = {
                    "id": f"p{page_num+1}_c{col_idx}_{safe_num}",
                    "num": num_str,
                    "text": q_text_only, # 텍스트 질문
                    "options": options[:4], # 보기 텍스트
                    "image": image_rel_path, # ★ 캡처된 통이미지 경로 (없으면 None)
                    "answer": 1, 
                    "explanation": "이미지 참고" if image_rel_path else "해설 없음"
                }
                
                questions.append(q_data)
                total_q_count += 1
        
        # 진행 상황 출력 (10페이지마다)
        if (page_num + 1) % 10 == 0:
            print(f"[Progress] {page_num + 1}/{doc.page_count} 페이지 처리 완료... (현재까지 {total_q_count}문제)")
                
    # JSON 출력
    out_js = os.path.join(output_dir, "questions.js")
    with open(out_js, "w", encoding="utf-8") as f:
        json_str = json.dumps(questions, ensure_ascii=False, indent=2)
        f.write(f"const questionData = {json_str};")
        
    out_json = os.path.join(output_dir, "official_survey.json")
    with open(out_json, "w", encoding="utf-8") as f:
        json.dump(questions, f, ensure_ascii=False, indent=2)
        
    print(f"[Success] 총 {total_q_count}개 문제 추출 및 캡처 완료.")

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"FATAL ERROR: {e}")
        import traceback
        traceback.print_exc()
