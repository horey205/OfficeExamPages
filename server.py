from http.server import HTTPServer, SimpleHTTPRequestHandler
import json
import os
import sys

# Constants
PORT = 8000
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
QUIZ_APP_DIR = BASE_DIR

class QuizHandler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=BASE_DIR, **kwargs)

    def do_POST(self):
        if self.path == '/save_questions':
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            
            try:
                data = json.loads(post_data.decode('utf-8'))
                mode = data.get('mode')
                questions = data.get('questions')
                
                if not mode or not questions:
                    self._send_response(400, {'error': 'Invalid data format'})
                    return

                # Map mode to filename
                filename_map = {
                    'off_survey': 'official_survey.json',
                    'off_cs': 'official_cs.json',
                    'cust_survey': 'custom_survey.json',
                    'cust_cs': 'custom_cs.json'
                }
                
                target_file = filename_map.get(mode)
                if not target_file:
                    self._send_response(400, {'error': 'Invalid mode'})
                    return

                # 1. Save JSON file
                file_path = os.path.join(QUIZ_APP_DIR, target_file)
                with open(file_path, 'w', encoding='utf-8') as f:
                    json.dump(questions, f, indent=2, ensure_ascii=False)
                
                # 2. Run convert_to_js.py logic immediately
                self.convert_to_js()
                
                self._send_response(200, {'success': True, 'message': f'{target_file} updated and questions.js regenerated.'})
                
            except Exception as e:
                self._send_response(500, {'error': str(e)})
        else:
            self.send_error(404, "File not found")

    def _send_response(self, code, data):
        self.send_response(code)
        self.send_header('Content-Type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps(data).encode('utf-8'))

    def convert_to_js(self):
        # Re-implement conversion logic here to avoid subprocess overhead/complexity
        files = {
            'official_survey.json': '기출',
            'official_cs.json': '기출',
            'custom_survey.json': 'AI/예상',
            'custom_cs.json': 'AI/예상'
        }
        all_data = []
        for filename, default_source in files.items():
            p = os.path.join(QUIZ_APP_DIR, filename)
            if os.path.exists(p):
                with open(p, 'r', encoding='utf-8') as f:
                    try:
                        data = json.load(f)
                        all_data.extend(data)
                    except:
                        pass
        
        js_content = f"const questionData = {json.dumps(all_data, ensure_ascii=False, indent=2)};"
        with open(os.path.join(QUIZ_APP_DIR, 'questions.js'), 'w', encoding='utf-8') as f:
            f.write(js_content)
        print("questions.js regenerated from server.")

if __name__ == '__main__':
    print(f"Starting Admin Server on port {PORT}...")
    print(f"Open http://localhost:{PORT}/admin.html to manage questions.")
    try:
        httpd = HTTPServer(('localhost', PORT), QuizHandler)
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nServer stopped.")
