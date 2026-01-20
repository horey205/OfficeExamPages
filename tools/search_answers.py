import fitz

pdf_path = r'c:\AI_Class\LicesneExam\지적공무원_기출문제.pdf'
doc = fitz.open(pdf_path)

results = []
for i in range(len(doc)):
    text = doc[i].get_text()
    if "정답" in text:
        results.append(i + 1)

print(f"Pages containing '정답': {results}")

# If found, print the text of those pages to see if it's an answer key
if results:
    for page_num in results:
        print(f"\n--- Page {page_num} Content ---\n")
        print(doc[page_num-1].get_text())
else:
    print("No pages found with the word '정답'.")
