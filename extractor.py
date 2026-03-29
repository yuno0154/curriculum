import pdfplumber
import re
import pandas as pd
import os
import sys
import json

def log(msg):
    try:
        print(msg)
    except UnicodeEncodeError:
        print(msg.encode('cp949', errors='replace').decode('cp949'))
    sys.stdout.flush()

def clean_statement(text):
    """성취기준 진술문 정제: 해설·고려사항 이후 내용 제거 및 공백 정리"""
    if not text:
        return ""
    text = text.replace('\n', ' ').strip()
    cutoff_markers = [
        '(가) 성취기준 해설', '(나) 성취기준 적용',
        '[학습 요소]', '[성취기준 해설]', '[성취기준 적용',
        '<성취기준 적용 시 고려 사항>',  # 전문교과 형식
        '⦁', '※', '\u2022',
    ]
    for marker in cutoff_markers:
        idx = text.find(marker)
        if idx != -1:
            text = text[:idx]
    text = re.sub(r'\s{2,}', ' ', text)
    return text.strip()

# 성취기준 코드 패턴
# 기존:  [9국01-01], [12전수01-01]  (공백 없음)
# 전문교과: [성직 01-01], [미의 02-03]  (한글2자 + 공백 + 숫자)
CODE_RE = re.compile(r'\[([A-Za-z0-9가-힣() ]+[-]\d+(?:[-]\d+)*)\]')

# 페이지 헤더 (제목·장식 텍스트, 건너뜀)
PAGE_HEADERS = {
    '중학교 교육과정',
    '고등학교 교육과정',
    '초⋅중등학교 교육과정 총론',
    '초·중등학교 교육과정 총론',
}

# 별책20-22 계열 교육과정 페이지 상단 헤더 패턴
TRACK_PAGE_HEADER_RE = re.compile(r'^(?:과학|체육|예술)\s*계열\s*선택\s*과목\s*교육과정$')

# 전문교과 교육과정 페이지 상단 헤더 패턴  (e.g. "미용 전문 교과 교육과정")
VOC_PAGE_HEADER_RE = re.compile(r'^.+\s*전문\s*교과\s*교육과정$')

# 계열 과목 서브헤더 → 과목명 추출
# e.g. "진로 선택 과목 - 전문 수학", "융합 선택 과목 - 음악과 문화"
TRACK_SUBJECT_RE = re.compile(r'^(?:진로|융합)\s*선택\s*과목\s*[-–]\s*(.+)$')

# 전문교과 서브헤더 → 과목명 추출
# e.g. "전문 공통 과목 - 1. 성공적인 직업 생활", "전공 일반 과목 - 1. 미용의 기초"
VOC_SUBJECT_RE = re.compile(
    r'^(?:전문\s*공통|전공\s*일반|전공\s*실무)\s*과목\s*[-–]\s*(?:\d+\.\s*)?(.+)$'
)
# 전문 공통 과목 헤더 감지 (성공적인 직업 생활, 노동 인권과 산업 안전 보건, 디지털과 직업 생활)
VOC_COMMON_SUBJECT_RE = re.compile(r'^전문\s*공통\s*과목')


def get_classification(filename):
    """파일명에서 분류명과 PDF 타입을 반환 (level, pdf_type)"""
    # 별책3, 4 → 학교급
    if '별책3]' in filename:
        return '중학교', 'school'
    if '별책4]' in filename:
        return '고등학교', 'school'
    # 별책20-22 → 계열
    if '별책20]' in filename:
        return '과학 계열', 'track'
    if '별책21]' in filename:
        return '체육 계열', 'track'
    if '별책22]' in filename:
        return '예술 계열', 'track'
    # 별책23 이상 → 전문교과명 추출 (e.g. "미용", "기계", "경영·금융")
    m = re.search(r'\[별책\d+\]\s+(.+?)\s+전문\s+교과\s+교육과정', filename)
    if m:
        return m.group(1), 'vocational'
    # 파일명에 학교급이 직접 명시된 경우 (하위 호환)
    if '중학교' in filename:
        return '중학교', 'school'
    if '고등학교' in filename:
        return '고등학교', 'school'
    return '기타', 'school'


def is_subject_header(line):
    """학교급 PDF용: 페이지 상단의 순수 한글 과목명 헤더 판별"""
    stripped = line.strip()
    if not stripped or stripped in PAGE_HEADERS:
        return False
    return bool(re.match(r'^[가-힣·⋅ ·()]+$', stripped)) and 2 <= len(stripped) <= 15


def is_section_header(line):
    """본문 섹션 구분자인지 확인 (성취기준 외 영역 마커)"""
    stripped = line.strip()
    patterns = [
        r'^\([가-힣]\)',          # (가), (나), (다) ...
        r'^\(\d+\)',              # (1), (2) ...
        r'^[가-힣]\.\s',          # 가., 나., 다. ...
        r'^\d+\.\s',              # 1., 2., 3. ...
        r'^\d+\)\s',              # 1) 일과 직업  (전문교과 형식)
        r'^<[^>]+>',              # <표>, <그림>, <성취기준 적용 시 고려 사항> ...
    ]
    return any(re.match(p, stripped) for p in patterns)


def is_bullet_line(line):
    """설명/해설 용도의 불릿 라인인지 확인"""
    stripped = line.strip()
    return stripped.startswith('•') or stripped.startswith('⦁') or stripped.startswith('\u2022')


def extract_from_pdf(path, level, pdf_type):
    results = []
    seen_codes = set()

    current_subject = None
    current_level = level   # 전문 공통 과목 진입 시 '전문 공통'으로 전환
    in_achievement = False

    pending_code = None
    pending_parts = []

    def flush_pending():
        nonlocal pending_code, pending_parts
        if pending_code and pending_parts:
            stmt = clean_statement(' '.join(pending_parts))
            if len(stmt) > 5 and pending_code not in seen_codes:
                results.append({
                    'level': current_level,
                    'subject': current_subject,
                    'code': f'[{pending_code}]',
                    'statement': stmt,
                })
                seen_codes.add(pending_code)
        pending_code = None
        pending_parts = []

    try:
        with pdfplumber.open(path) as pdf:
            log(f"    총 {len(pdf.pages)}페이지 분석 시작")

            for page_idx, page in enumerate(pdf.pages):
                text = page.extract_text()
                if not text:
                    continue

                lines = text.split('\n')

                for line_idx, raw_line in enumerate(lines):
                    line = raw_line.strip()
                    if not line:
                        continue

                    # ── 페이지 헤더 건너뜀 ──────────────────────────────
                    if line in PAGE_HEADERS:
                        continue

                    # ── 페이지 첫 줄 처리 (과목명 감지) ─────────────────
                    if line_idx == 0:
                        # 계열 교육과정 메인 헤더 (건너뜀)
                        if TRACK_PAGE_HEADER_RE.match(line):
                            continue
                        # 전문교과 메인 헤더 (건너뜀)
                        if VOC_PAGE_HEADER_RE.match(line):
                            continue

                        if pdf_type == 'track':
                            # "진로 선택 과목 - 전문 수학" → subject = "전문 수학"
                            m = TRACK_SUBJECT_RE.match(line)
                            if m:
                                new_subject = m.group(1).strip()
                                if new_subject != current_subject:
                                    flush_pending()
                                    current_subject = new_subject
                                    in_achievement = False
                                    log(f"    [{page_idx+1}p] 과목 전환 → {current_subject}")
                                continue

                        elif pdf_type == 'vocational':
                            # "전문 공통 과목 - 1. 성공적인 직업 생활" → level='전문 공통'
                            # "전공 일반 과목 - 1. 미용의 기초" → level=vocational level
                            m = VOC_SUBJECT_RE.match(line)
                            if m:
                                new_subject = m.group(1).strip()
                                new_level = '전문 공통' if VOC_COMMON_SUBJECT_RE.match(line) else level
                                if new_subject != current_subject or new_level != current_level:
                                    flush_pending()
                                    current_subject = new_subject
                                    current_level = new_level
                                    in_achievement = False
                                    log(f"    [{page_idx+1}p] 과목 전환 → {current_subject} [{current_level}]")
                                continue

                        else:  # school
                            if is_subject_header(line):
                                if line != current_subject:
                                    flush_pending()
                                    current_subject = line
                                    in_achievement = False
                                    log(f"    [{page_idx+1}p] 과목 전환 → {current_subject}")
                                continue

                    # ── 불릿 라인(설명/해설) 건너뜀 ────────────────────
                    if is_bullet_line(line):
                        continue

                    # ── 섹션 진입/종료 감지 ─────────────────────────────
                    if '나. 성취기준' in line and '적용' not in line and '고려' not in line:
                        flush_pending()
                        in_achievement = True
                        continue

                    stop_markers = ['3. 교수', '3. 평가']
                    stop_anywhere = ['교수⋅학습 및 평가', '교수·학습 및 평가']
                    is_stop = (
                        any(line.startswith(m) for m in stop_markers)
                        or any(line == m for m in stop_anywhere)
                    )
                    if is_stop:
                        flush_pending()
                        in_achievement = False
                        continue

                    if not in_achievement or not current_subject:
                        continue

                    # ── 성취기준 코드 라인 처리 ─────────────────────────
                    code_match = CODE_RE.match(line)
                    if code_match:
                        flush_pending()
                        pending_code = code_match.group(1)
                        stmt_tail = line[code_match.end():].strip()
                        pending_parts = [stmt_tail] if stmt_tail else []
                        continue

                    # ── 진술문 연속 라인 처리 ────────────────────────────
                    if pending_code:
                        if is_section_header(line):
                            flush_pending()
                            continue
                        if re.match(r'^\d+$', line):
                            continue
                        pending_parts.append(line)

            flush_pending()

    except Exception as e:
        log(f"    [오류] {os.path.basename(path)}: {e}")
        import traceback
        traceback.print_exc()

    return results


def main():
    log("─" * 60)
    log("  성취기준 추출 엔진 (별책3·4·20·21·22 및 전문교과)")
    log("─" * 60)

    input_dir = 'achivement_files'
    if not os.path.exists(input_dir):
        log(f"[오류] 폴더 없음: {input_dir}")
        return

    # 이미 추출된 별책은 건너뜀 (별책3·4는 기존 data.json에 존재)
    SKIP_BOOKS = {'별책3]', '별책4]'}

    files = sorted(f for f in os.listdir(input_dir) if f.lower().endswith('.pdf'))
    log(f"\n[폴더] {input_dir} ({len(files)}개 파일 발견)\n")

    # 기존 data.json 로드 (별책3·4 데이터 보존)
    # 별책3: 중학교, 선택, 생활 외국어 / 별책4: 고등학교
    SKIP_LEVELS = {'중학교', '고등학교', '선택', '생활 외국어'}
    final_data = []
    if os.path.exists('data.json'):
        with open('data.json', encoding='utf-8') as f:
            existing = json.load(f)
        kept = [r for r in existing if r.get('level') in SKIP_LEVELS]
        final_data.extend(kept)
        by_level = {}
        for r in kept:
            by_level[r['level']] = by_level.get(r['level'], 0) + 1
        log(f"[기존 데이터] {dict(by_level)} 유지\n")

    for idx, filename in enumerate(files):
        # 건너뛸 별책 확인
        if any(skip in filename for skip in SKIP_BOOKS):
            log(f"[{idx+1}/{len(files)}] {filename}  ← 건너뜀 (기존 데이터 사용)")
            continue

        path = os.path.join(input_dir, filename)
        level, pdf_type = get_classification(filename)
        log(f"[{idx+1}/{len(files)}] {filename}")
        log(f"  → 분류: {level}  타입: {pdf_type}")

        res = extract_from_pdf(path, level, pdf_type)
        final_data.extend(res)
        log(f"  └ {len(res)}건 추출\n")

    if not final_data:
        log("[경고] 추출된 데이터 없음. PDF 구조를 확인해 주세요.")
        return

    df = pd.DataFrame(final_data).drop_duplicates(subset=['level', 'code', 'statement'])

    df.to_excel('성취기준_추출결과.xlsx', index=False)

    web_data = df.to_dict(orient='records')
    with open('data.json', 'w', encoding='utf-8') as f:
        json.dump(web_data, f, ensure_ascii=False, indent=2)

    log(f"[완료] 총 {len(df)}건 추출 → 성취기준_추출결과.xlsx / data.json")

    log("\n[분류별·과목별 추출 현황]")
    summary = df.groupby(['level', 'subject']).size().reset_index(name='count')
    for _, row in summary.iterrows():
        log(f"  {row['level']:20s} | {str(row['subject']):25s} | {row['count']}건")


if __name__ == '__main__':
    main()
