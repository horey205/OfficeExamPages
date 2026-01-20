
import fitz
import os

pdf_path = r"D:\AI_Class\지적공무원기출문제\지적공무원_기출문제.pdf"
doc = fitz.open(pdf_path)

print(f"Total pages: {doc.page_count}")

# Check first 5 pages for drawings/images
for page_num in range(5):
    page = doc[page_num]
    drawings = page.get_drawings()
    images = page.get_images()
    
    print(f"--- Page {page_num + 1} ---")
    print(f"Num Drawings (Reference count): {len(drawings)}")
    print(f"Num Images (Embedded): {len(images)}")
    
    # Let's see if we can find text that says '그림'
    text = page.get_text()
    if "그림" in text:
        print("Text '그림' found on this page.")
