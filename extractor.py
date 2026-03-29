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
    # 성취기준 본문이 아닌 부가 설명 부분 이후 잘라내기
    cutoff_markers = [
        '(가) 성취기준 해설', '(나) 성취기준 적용',
        '[학습 요소]', '[성취기준 해설]', '[성취기준 적용',
        '⦁', '※', '\u2022',  # bullet points
    ]
    for marker in cutoff_markers:
        idx = text.find(marker)
        if idx != -1:
            text = text[:idx]
    text = re.sub(r'\s{2,}', ' ', text)
    return text.strip()

# 성취기준 코드 패턴
# 예: [9국01-01], [9사(지리)01-01], [12수학-01-01], [10과학01-01]
# 조건: 대괄호 안이 영숫자·한글·괄호·하이픈으로 이루어지고, 반드시 하이픈+숫자로 끝남
CODE_RE = re.compile(r'\[([A-Za-z0-9가-힣()]+[-]\d+(?:[-]\d+)*)\]')

# 페이지 헤더 문자열 (내용이 아닌 머리글)
PAGE_HEADERS = {
    '중학교 교육과정',
    '고등학교 교육과정',
    '초⋅중등학교 교육과정 총론',
    '초·중등학교 교육과정 총론',
}

def is_subject_header(line):
    """페이지 상단에 등장하는 과목명 헤더 여부 판별"""
    stripped = line.strip()
    if not stripped or stripped in PAGE_HEADERS:
        return False
    # 2~15자 한글(·⋅ 포함) 과목명
    return bool(re.match(r'^[가-힣·⋅ ·()]+$', stripped)) and 2 <= len(stripped) <= 15

def is_section_header(line):
    """본문 섹션 구분자인지 확인 (성취기준 외 영역 마커)"""
    stripped = line.strip()
    patterns = [
        r'^\([가-힣]\)',          # (가), (나), (다) ...
        r'^\(\d+\)',              # (1), (2) ...
        r'^[가-힣]\.\s',          # 가., 나., 다. ...
        r'^\d+\.\s',              # 1., 2., 3. ...
        r'^<[^>]+>',              # <표>, <그림> ...
    ]
    return any(re.match(p, stripped) for p in patterns)

def is_bullet_line(line):
    """설명/해설 용도의 불릿 라인인지 확인"""
    stripped = line.strip()
    return stripped.startswith('•') or stripped.startswith('⦁') or stripped.startswith('\u2022')

def get_school_level(filename):
    if '별책3' in filename:
        return '중학교'
    if '별책4' in filename:
        return '고등학교'
    if '중학교' in filename:
        return '중학교'
    if '고등학교' in filename:
        return '고등학교'
    return '기타'

def extract_from_pdf(path, school_level):
    results = []
    seen_codes = set()

    current_subject = None
    in_achievement = False   # "나. 성취기준" 섹션 진입 여부

    # 현재 수집 중인 코드와 진술문 조각
    pending_code = None
    pending_parts = []

    def flush_pending():
        """보류 중인 코드+진술문을 results에 추가"""
        nonlocal pending_code, pending_parts
        if pending_code and pending_parts:
            stmt = clean_statement(' '.join(pending_parts))
            if len(stmt) > 5 and pending_code not in seen_codes:
                results.append({
                    'level': school_level,
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

                    # ── 과목명 감지 (페이지 첫 유효 라인) ───────────────
                    if line_idx == 0 and is_subject_header(line):
                        if line != current_subject:
                            flush_pending()
                            current_subject = line
                            in_achievement = False
                            log(f"    [{page_idx+1}p] 과목 전환 → {current_subject}")
                        continue  # 헤더 라인 자체는 본문 처리 제외

                    # ── 불릿 라인(설명/해설) 건너뜀 ────────────────────
                    # 종료 조건보다 먼저 처리해야 설명문 안의 "교수⋅학습" 오탐을 방지
                    if is_bullet_line(line):
                        continue

                    # ── 섹션 진입/종료 감지 ─────────────────────────────
                    # "나. 성취기준" → 수집 시작 (단, "적용 시 고려 사항"은 제외)
                    if '나. 성취기준' in line and '적용' not in line and '고려' not in line:
                        flush_pending()
                        in_achievement = True
                        continue

                    # "3. 교수·학습" 계열 → 수집 종료
                    # 줄 시작 기준으로만 검사해 설명문 내 "교수⋅학습" 오탐 방지
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
                        if stmt_tail:
                            pending_parts = [stmt_tail]
                        else:
                            pending_parts = []
                        continue

                    # ── 진술문 연속 라인 처리 ────────────────────────────
                    if pending_code:
                        # 섹션 구분자면 연속 중단
                        if is_section_header(line):
                            # 섹션 구분자가 새 소주제 시작이면 현재 코드 확정
                            flush_pending()
                            continue
                        # 페이지 숫자(단독 숫자)는 제외
                        if re.match(r'^\d+$', line):
                            continue
                        pending_parts.append(line)

            # 마지막 페이지 잔여 처리
            flush_pending()

    except Exception as e:
        log(f"    [오류] {os.path.basename(path)}: {e}")
        import traceback
        traceback.print_exc()

    return results


def main():
    log("─" * 60)
    log("  성취기준 추출 엔진 (별책3·4 전용)")
    log("─" * 60)

    input_dir = 'achivement_files'
    if not os.path.exists(input_dir):
        log(f"[오류] 폴더 없음: {input_dir}")
        return

    files = [f for f in os.listdir(input_dir) if f.lower().endswith('.pdf')]
    log(f"\n[폴더] {input_dir} ({len(files)}개 파일 발견)\n")

    final_data = []

    for idx, filename in enumerate(files):
        path = os.path.join(input_dir, filename)
        school_level = get_school_level(filename)
        log(f"[{idx+1}/{len(files)}] {filename}  ({school_level})")

        res = extract_from_pdf(path, school_level)
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

    log(f"[완료] 총 {len(df)}건 추출 -> 성취기준_추출결과.xlsx / data.json")

    # 과목별 요약
    log("\n[과목별 추출 현황]")
    summary = df.groupby(['level', 'subject']).size().reset_index(name='count')
    for _, row in summary.iterrows():
        log(f"  {row['level']} | {row['subject']:15s} | {row['count']}건")


if __name__ == '__main__':
    main()
