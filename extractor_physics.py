import pdfplumber
import re
import pandas as pd
import os
import sys
import json

def log(msg):
    print(msg)
    sys.stdout.flush()

def clean_statement(text):
    if not text: return ""
    text = text.replace('\n', ' ').strip()
    
    patterns = [
        r'서·논술형', r'구술·발표', r'실험·실습', r'프로젝트', r'포트폴리오', r'토의·토론', r'실기 평가',
        r'', r'⦁', r'※', r'\*', 
        r'<탐구 활동>', r'\[학습 요소\]', r'\[성취기준 해설\]', r'\[성길 기준 해설\]'
    ]
    for p in patterns:
        text = re.split(p, text)[0]
    
    text = re.sub(r'\s{2,}', ' ', text)
    return text.strip()

def extract_physics_from_pdf(path, default_subject):
    results = []
    code_pattern = re.compile(r'\[[A-Za-z0-9가-힣ⅠⅡⅢⅣⅤ-]+-\d+\]')
    
    try:
        with pdfplumber.open(path) as pdf:
            # 1. 차례 페이지(7~18p)에서 과목명 목록 미리 만들기 (중학/고교 통합 대응)
            subject_list = []
            for i in range(6, 18):
                if i >= len(pdf.pages): break
                text = pdf.pages[i].extract_text()
                if not text: continue
                # '1. 과목명 53' 형태 추출 (앞뒤 공백 허용)
                matches = re.findall(r'^\s*\d+\.\s*(.+?)\s+\d+$', text, re.MULTILINE)
                subject_list.extend([m.strip() for m in matches])
            
            if subject_list:
                log(f"    - 목차에서 {len(set(subject_list))}개 과목 식별됨")

            # 2. 본문 분석 및 과목명 실시간 갱신
            current_subject = default_subject
            # 중복 방지를 위한 셋(Set)
            seen_codes = set()

            for page_idx, page in enumerate(pdf.pages):
                # 7페이지 이전은 보통 서문이므로 스킵 (필요시 조정)
                if page_idx < 6: continue
                
                page_text = page.extract_text()
                if not page_text: continue
                
                lines = page_text.split('\n')
                
                # 과목명 갱신 로직: '1. 성격 및 목표' 직전 줄 확인
                for idx, line in enumerate(lines):
                    if "1. 성격 및 목표" in line and idx > 0:
                        potential = lines[idx-1].strip()
                        # 목차에 있거나 '물리' 키워드가 포함된 경우 과목명으로 인정
                        if any(s in potential for s in subject_list) or "물리" in potential:
                            current_subject = potential
                            log(f"    - [{page_idx + 1}p] 과목 전환: {current_subject}")
                
                # 물리 관련 과목 섹션이 아니면 데이터 추출 스킵
                if not current_subject or '물리' not in current_subject:
                    continue

                # 3. 데이터 추출 (테이블 우선)
                tables = page.extract_tables()
                found_in_table = False
                
                if tables:
                    for table in tables:
                        for row in table:
                            if not row: continue
                            for col_idx, cell in enumerate(row):
                                if not cell: continue
                                cell_text = str(cell).replace('\n', ' ')
                                matches = list(code_pattern.finditer(cell_text))
                                
                                if matches:
                                    found_in_table = True
                                    for i, m in enumerate(matches):
                                        code = m.group()
                                        if code in seen_codes: continue
                                        
                                        start = m.end()
                                        end = matches[i+1].start() if i+1 < len(matches) else len(cell_text)
                                        stmt_raw = cell_text[start:end].strip()
                                        
                                        if len(stmt_raw) < 5 and col_idx + 1 < len(row) and row[col_idx+1]:
                                            stmt_raw += " " + str(row[col_idx+1]).replace('\n', ' ')
                                            
                                        stmt = clean_statement(stmt_raw)
                                        if len(stmt) > 5:
                                            results.append({
                                                'subject': current_subject, 'code': code, 
                                                'statement': stmt, 'page': page_idx + 1
                                            })
                                            seen_codes.add(code)
                
                # 테이블이 없는 경우 텍스트에서 직접 추출
                if not found_in_table:
                    text_all = page_text.replace('\n', ' ')
                    t_matches = list(code_pattern.finditer(text_all))
                    for i, tm in enumerate(t_matches):
                        code = tm.group()
                        if code in seen_codes: continue
                        
                        stmt = clean_statement(text_all[tm.end() : (t_matches[i+1].start() if i+1 < len(t_matches) else len(text_all))])
                        if len(stmt) > 5:
                            results.append({
                                'subject': current_subject, 'code': code, 
                                'statement': stmt, 'page': page_idx + 1
                            })
                            seen_codes.add(code)
                                    
    except Exception as e:
        log(f"    - ❌ {os.path.basename(path)} Error: {e}")
    return results

def main():
    log("--- 🚀 성취기준 통합 추출 엔진 (물리학 전용) ---")
    log("안내: 파일명이 아닌 문서 본문(7p~20p) 내 텍스트와 앵커를 통해서만 과목명을 식별합니다.")
    
    input_dirs = ["achivement_files"]
    final_data = []

    for input_dir in input_dirs:
        if not os.path.exists(input_dir): continue
        files = [f for f in os.listdir(input_dir) if f.lower().endswith('.pdf')]
        log(f"\n📁 폴더 탐색: {input_dir} ({len(files)}개 파일 발견)")

        for idx, filename in enumerate(files):
            path = os.path.join(input_dir, filename)
            log(f"  [{idx+1}/{len(files)}] {filename} 분석 중...")
            
            # 파일명을 전달하되, extract 함수 내부에서 본문 탐지 결과에만 의존함
            res = extract_physics_from_pdf(path, default_subject=filename)
            if res:
                final_data.extend(res)
                log(f"    ㄴ {len(res)}건 추출 완료")
            else:
                log(f"    ㄴ 물리과 데이터 없음 (본문 내 과목명 탐지 실패 또는 불일치)")

    if final_data:
        df = pd.DataFrame(final_data).drop_duplicates(subset=['code', 'statement'])
        
        # 물리학 전용 파일로 결과 저장
        df.to_excel("성취기준_추출결과_물리학.xlsx", index=False)
        
        web_data = df.to_dict(orient='records')
        with open("data_physics.json", "w", encoding="utf-8") as f:
            json.dump(web_data, f, ensure_ascii=False, indent=2)
            
        log(f"\n✅ 물리과 추출 완료! (최종 {len(df)}건 확보)")
        log("1. '성취기준_추출결과_물리학.xlsx' 에서 내용을 확인할 수 있습니다.")
    else:
        log("\n⚠️ 물리과 추출된 데이터가 없습니다. 물리 관련 PDF 파일 형식을 확인해 주세요.")

if __name__ == "__main__":
    main()
