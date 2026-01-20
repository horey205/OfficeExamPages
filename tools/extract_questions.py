import fitz  # PyMuPDF
import json
import os
import re

def extract_pdf_data(pdf_path, output_dir):
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    img_dir = os.path.join(output_dir, "images")
    if not os.path.exists(img_dir):
        os.makedirs(img_dir)

    doc = fitz.open(pdf_path)
    questions = []
    
    current_subject = "지적공무원 기출문제"
    
    for page_num in range(doc.page_count):
        page = doc[page_num]
        mid_x = page.rect.width / 2
        
        # Get blocks with location
        blocks = page.get_text("blocks")
        
        # Extract Images with locations
        page_images = []
        image_list = page.get_images(full=True)
        for img_index, img in enumerate(image_list):
            xref = img[0]
            try:
                base_image = doc.extract_image(xref)
                image_bytes = base_image["image"]
                image_ext = base_image["ext"]
                img_filename = f"page_{page_num+1}_img_{img_index}.{image_ext}"
                img_path = os.path.join(img_dir, img_filename)
                with open(img_path, "wb") as f:
                    f.write(image_bytes)
                
                # Image location info
                img_info = page.get_image_info(xrefs=True)
                for info in img_info:
                    if info['xref'] == xref:
                        page_images.append({
                            "path": f"images/{img_filename}",
                            "bbox": info['bbox'],
                            "x": info['bbox'][0],
                            "y": info['bbox'][1]
                        })
            except Exception as e:
                print(f"Error extracting image {img_index} on page {page_num+1}: {e}")

        # Process each column separately for better logic
        for col_idx in [0, 1]: # 0 = Left, 1 = Right
            col_blocks = [b for b in blocks if (b[0] < mid_x if col_idx == 0 else b[0] >= mid_x)]
            col_blocks.sort(key=lambda x: x[1]) # Sort by Y
            
            col_questions = []
            
            # Group blocks by question
            current_q = None
            for b in col_blocks:
                text = b[4].strip()
                # Check for "문 1." etc.
                match = re.match(r'(문\s*\d+\.)', text)
                if match:
                    if current_q:
                        col_questions.append(current_q)
                    current_q = {
                        "num_text": match.group(0),
                        "full_text": text,
                        "ymin": b[1],
                        "ymax": b[3],
                        "blocks": [b]
                    }
                elif current_q:
                    current_q["full_text"] += "\n" + text
                    current_q["ymax"] = b[3]
                    current_q["blocks"].append(b)
            
            if current_q:
                col_questions.append(current_q)
                
            # Process each question in column
            for q in col_questions:
                q_body = q["full_text"]
                opt_pattern = r'①|②|③|④'
                opt_splits = re.split(opt_pattern, q_body)
                
                main_text = opt_splits[0].replace(q["num_text"], "").strip()
                options = [o.strip() for o in opt_splits[1:] if o.strip()]
                
                # Association: Find images in this column and within Y-range
                q_image = None
                for img in page_images:
                    # Check if image is in same column
                    img_in_col = (img["x"] < mid_x if col_idx == 0 else img["x"] >= mid_x)
                    # Check if image Y is within question Y range (with some buffer)
                    if img_in_col and (q["ymin"] - 10 <= img["y"] <= q["ymax"] + 10):
                        q_image = img["path"]
                        break
                
                questions.append({
                    "id": f"p{page_num+1}_c{col_idx}_q{len(questions)}",
                    "num": q["num_text"],
                    "text": main_text,
                    "options": options[:4],
                    "image": q_image,
                    "answer": 1,
                    "subject": current_subject
                })

    # Save to JSON
    with open(os.path.join(output_dir, "questions.json"), "w", encoding="utf-8") as f:
        json.dump(questions, f, ensure_ascii=False, indent=2)

    return len(questions)

    # Save to JSON
    with open(os.path.join(output_dir, "questions.json"), "w", encoding="utf-8") as f:
        json.dump(questions, f, ensure_ascii=False, indent=2)

    return len(questions)

if __name__ == "__main__":
    pdf_path = r"C:\AI_Class\LicesneExam\지적공무원_기출문제.pdf"
    output_dir = r"C:\AI_Class\LicesneExam\quiz_app"
    count = extract_pdf_data(pdf_path, output_dir)
    print(f"Extracted {count} questions.")
