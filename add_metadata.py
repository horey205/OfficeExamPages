import json
import os

def main():
    json_path = "official_survey.json"
    js_path = "questions.js"

    if not os.path.exists(json_path):
        print(f"Error: {json_path} not found.")
        return

    with open(json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    print(f"Loaded {len(data)} questions.")

    updated_count = 0
    for q in data:
        # ID format: p{page}_c{col}_{num}
        # Example: p3_c0_1
        try:
            parts = q['id'].split('_')
            page_str = parts[0] # p3
            page_num = int(page_str[1:])
            
            # Subject Logic
            # Assuming pages <= 25 are '지적측량' and > 25 are '지적전산학개론'
            # (Based on update_subjects.py logic seen in repo)
            if page_num <= 25:
                q['subject'] = '지적측량'
            else:
                q['subject'] = '지적전산학개론'
            
            # Difficulty Logic (Default to '중' if missing)
            if 'difficulty' not in q:
                q['difficulty'] = '중'
            
            updated_count += 1
        except Exception as e:
            print(f"Skipping metadata for {q.get('id', 'unknown')}: {e}")
            # Default fallback
            if 'subject' not in q: q['subject'] = '지적측량'
            if 'difficulty' not in q: q['difficulty'] = '중'

    # Save JSON
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"Updated {json_path} with metadata.")

    # Save JS
    with open(js_path, 'w', encoding='utf-8') as f:
        json_str = json.dumps(data, ensure_ascii=False, indent=2)
        f.write(f"const questionData = {json_str};")
    print(f"Regenerated {js_path}.")

if __name__ == "__main__":
    main()
