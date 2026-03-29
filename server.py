# server.py — 성취기준 편집 저장 서버
# 표준 라이브러리만 사용 (별도 설치 불필요)

from http.server import HTTPServer, SimpleHTTPRequestHandler
import json, os, subprocess, sys, datetime

BASE_DIR   = os.path.dirname(os.path.abspath(__file__))
DATA_FILE  = os.path.join(BASE_DIR, 'data.json')
EDITS_FILE = os.path.join(BASE_DIR, 'edits.json')

# ── 편집 파일 로드/저장 ─────────────────────────────────────
def load_edits():
    if os.path.exists(EDITS_FILE):
        with open(EDITS_FILE, encoding='utf-8') as f:
            return json.load(f)
    return {}

def save_edits(edits):
    with open(EDITS_FILE, 'w', encoding='utf-8') as f:
        json.dump(edits, f, ensure_ascii=False, indent=2)

# ── Git 커밋 & 푸시 ─────────────────────────────────────────
def git_push(message):
    try:
        r = subprocess.run(
            ['git', 'rev-parse', '--is-inside-work-tree'],
            capture_output=True, cwd=BASE_DIR
        )
        if r.returncode != 0:
            return False, 'git 저장소 아님'
        subprocess.run(['git', 'add', 'edits.json'], cwd=BASE_DIR, check=True, capture_output=True)
        subprocess.run(['git', 'commit', '-m', message], cwd=BASE_DIR, check=True, capture_output=True)
        subprocess.run(['git', 'push'], cwd=BASE_DIR, check=True, capture_output=True)
        return True, 'push 완료'
    except subprocess.CalledProcessError as e:
        return False, str(e)
    except Exception as e:
        return False, str(e)

# ── HTTP 핸들러 ─────────────────────────────────────────────
class Handler(SimpleHTTPRequestHandler):

    def do_OPTIONS(self):
        self.send_response(200)
        self._cors()
        self.end_headers()

    def do_POST(self):
        length = int(self.headers.get('Content-Length', 0))
        body = {}
        if length:
            try:
                body = json.loads(self.rfile.read(length).decode('utf-8'))
            except Exception:
                self._json(400, {'error': '잘못된 JSON'})
                return

        # ── POST /api/edit ──────────────────────────────────
        if self.path == '/api/edit':
            code      = body.get('code', '').strip()
            statement = body.get('statement', '').strip()
            if not code or not statement:
                self._json(400, {'error': '코드 또는 진술문이 비어 있습니다.'}); return

            # data.json에 해당 코드가 있는지 확인
            with open(DATA_FILE, encoding='utf-8') as f:
                data = json.load(f)
            original = next((d['statement'] for d in data if d['code'] == code), None)
            if original is None:
                self._json(404, {'error': '코드를 찾을 수 없습니다.'}); return

            edits = load_edits()
            if statement == original:
                # 원본과 동일하면 편집 제거
                edits.pop(code, None)
            else:
                edits[code] = {
                    'statement': statement,
                    'original':  original,
                    'edited_at': datetime.datetime.now().isoformat(timespec='seconds'),
                }
            save_edits(edits)

            pushed, msg = git_push(f'성취기준 수정: {code}')
            self._json(200, {'ok': True, 'git': msg})

        # ── POST /api/reset ─────────────────────────────────
        elif self.path == '/api/reset':
            code = body.get('code', '').strip()
            if not code:
                self._json(400, {'error': '코드가 없습니다.'}); return

            edits = load_edits()
            edits.pop(code, None)
            save_edits(edits)

            pushed, msg = git_push(f'성취기준 복원: {code}')
            self._json(200, {'ok': True, 'git': msg})

        else:
            self._json(404, {'error': 'not found'})

    def _json(self, status, data):
        body = json.dumps(data, ensure_ascii=False).encode('utf-8')
        self.send_response(status)
        self._cors()
        self.send_header('Content-Type', 'application/json; charset=utf-8')
        self.send_header('Content-Length', len(body))
        self.end_headers()
        self.wfile.write(body)

    def _cors(self):
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')

    def log_message(self, fmt, *args):
        print(f'  {self.address_string()} {fmt % args}')

# ── 진입점 ──────────────────────────────────────────────────
if __name__ == '__main__':
    port = 8000
    print('─' * 50)
    print('  성취기준 검색 서버')
    print('─' * 50)
    print(f'  주소: http://localhost:{port}')
    print(f'  데이터: {DATA_FILE}')
    print(f'  편집본: {EDITS_FILE}')
    print('  Ctrl+C 로 종료\n')
    HTTPServer(('', port), Handler).serve_forever()
