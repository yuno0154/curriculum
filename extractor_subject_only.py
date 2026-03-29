import pdfplumber
import re
import os
import sys

# Windows 터미널 한글 깨짐 방지
if sys.stdout.encoding != 'utf-8':
    try:
        import io
        sys.stdout = io.TextIOWrapper(sys.stdout.detach(), encoding='utf-8')
    except: pass

def log(msg):
    print(msg)
    sys.stdout.flush()

def clean_subject_name(name):
    if not name: return None
    name = name.strip()
    
    # 명칭 정규화: '가정' -> '기술·가정'
    if name == "가정":
        name = "기술·가정"
        
    # "선택:" 과 같은 구문 처리 (예: "선택: 심화 국어" -> "심화 국어")
    if name.startswith("선택:"):
        name = name.replace("선택:", "").strip()
    
    if len(name) > 25 or len(name) < 2: return None
    if any(char in name for char in "-?!)"): return None 
    
    # 제외 키워드 목록 (과목명이 아닌 명칭들)
    stop_words = [
        "요소", "방법", "제시", "내용", "체계", "설계", "개요", "목표", "범주", "총론", "개정", "설계의",
        "어야 할 태도로 구성되었다.", "창의적 체험활동", "선택:", "선택", "교양", "사회"
    ]
    if any(word in name for word in stop_words): return None
    if name.isdigit(): return None
    return name

def extract_subject_only(path, is_highschool=False):
    subject_candidates = []
    group_candidates = []
    
    try:
        with pdfplumber.open(path) as pdf:
            # 1. 차례 분석 (7~20p)
            for i in range(6, 20):
                if i >= len(pdf.pages): break
                text = pdf.pages[i].extract_text()
                if not text: continue
                matches = re.findall(r'(?:[○●\d-]*)\s*([가-힣\s\dⅠ-Ⅻ.·]+?)\s*[·.]{3,}\s*(\d+)', text)
                for m in matches:
                    raw_name = m[0].strip()
                    if is_highschool:
                        if raw_name in ["교양", "사회"]:
                            group_candidates.append(raw_name)
                            continue
                        if raw_name.endswith("과") and len(raw_name) <= 10:
                            if raw_name != "가정과":
                                group_candidates.append(raw_name)
                                continue
                    cleaned = clean_subject_name(raw_name)
                    if not cleaned: continue
                    subject_candidates.append(cleaned)
                        
            # 2. 본문 앵커 분석: "교육과정 설계의 개요" 또는 "1. 성격 및 목표" 윗줄을 과목명으로 인식
            for page in pdf.pages:
                text = page.extract_text()
                if not text: continue
                # 목차 앵커 발견
                anchors = ["교육과정 설계의 개요", "1. 성격 및 목표"]
                if any(anchor in text for anchor in anchors):
                    lines = text.split('\n')
                    for i, line in enumerate(lines):
                        if any(anchor in line for anchor in anchors) and i > 0:
                            raw_name = lines[i-1].strip()
                            if is_highschool:
                                if raw_name in ["교양", "사회"] or (raw_name.endswith("과") and raw_name != "가정과"):
                                    group_candidates.append(raw_name)
                                    continue
                            cleaned = clean_subject_name(raw_name)
                            if not cleaned: continue
                            subject_candidates.append(cleaned)
    except: pass
    
    return sorted(list(set(subject_candidates))), sorted(list(set(group_candidates)))

def main():
    log("--- 🕵️ 최종 과목명 추출 결과 ---")
    input_dir = "achivement_files"
    if not os.path.exists(input_dir):
        log(f"❌ {input_dir} 폴더를 찾을 수 없습니다.")
        return

    for f in os.listdir(input_dir):
        if any(x in f for x in ["별책3", "별책4"]):
            log(f"\n📂 {f}")
            is_hs = "별책4" in f
            subs, groups = extract_subject_only(os.path.join(input_dir, f), is_highschool=is_hs)
            
            if is_hs and groups:
                log(f"📦 탐지 과목군: {', '.join(groups)}")
            
            log(f"📖 탐지 과목: {', '.join(subs)}")

if __name__ == "__main__":
    main()
