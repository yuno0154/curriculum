"""
streamlit_app.py — 성취기준 검색 & 편집 (Streamlit Cloud 버전)
편집 내용은 GitHub API를 통해 edits.json 파일로 저장됩니다.
"""

import streamlit as st
import json, re, requests, base64
from datetime import datetime

# ─────────────────────────────────────────────────────────
#  1. 과목명 매핑
# ─────────────────────────────────────────────────────────
SUBJECT_MAP = {
    '10공국1':'공통국어1','10공국2':'공통국어2',
    '10공수1':'공통수학1','10공수2':'공통수학2',
    '10기수1':'기본수학1','10기수2':'기본수학2',
    '10공영1':'공통영어1','10공영2':'공통영어2',
    '10기영1':'기본영어1','10기영2':'기본영어2',
    '10통사1':'통합사회1','10통사2':'통합사회2',
    '10한사1':'한국사1','10한사2':'한국사2',
    '10통과1':'통합과학1','10통과2':'통합과학2',
    '10과탐1':'과학탐구실험1','10과탐2':'과학탐구실험2',
    '12화언':'화법과 언어','12독작':'독서와 작문','12문학':'문학',
    '12독토':'독서 토론과 글쓰기','12매의':'매체 의사소통',
    '12언탐':'언어생활 탐구','12직의':'직무 의사소통',
    '12문영':'문학과 영상','12주탐':'주제 탐구 독서',
    '12대수':'대수','12기하':'기하','12확통':'확률과 통계',
    '12수과':'수학과제 탐구','12경수':'경제 수학','12인수':'인공지능 수학',
    '12직수':'직무 수학','12실통':'실용 통계','12수문':'수학과 문화',
    '12영독':'영어 독해와 작문','12영발':'영어 발표와 토론',
    '12세영':'세계 문화와 영어','12미영':'미디어 영어',
    '12직영':'직무 영어','12실영':'실용 영어',
    '12심영':'심화 영어','12영문':'영어문학읽기',
    '12독어':'독일어','12독회':'독일어 회화','12독문':'독일어 독해와 작문','12심독':'심화 독일어',
    '12프어':'프랑스어','12프회':'프랑스어 회화','12프문':'프랑스어 독해와 작문','12심프':'심화 프랑스어',
    '12스어':'스페인어','12스회':'스페인어 회화','12심스':'심화 스페인어',
    '12중어':'중국어','12중회':'중국어 회화','12중문':'중국어 독해와 작문','12심중':'심화 중국어',
    '12일어':'일본어','12일회':'일본어 회화','12일문':'일본어 독해와 작문','12심일':'심화 일본어',
    '12러어':'러시아어','12러회':'러시아어 회화','12러문':'러시아어 독해와 작문','12심러':'심화 러시아어',
    '12아어':'아랍어','12아회':'아랍어 회화','12아문':'아랍어 독해와 작문','12심아':'심화 아랍어',
    '12베어':'베트남어','12베회':'베트남어 회화','12베문':'베트남어 독해와 작문','12심베':'심화 베트남어',
    '12한탐':'한국사 탐구','12동역':'동아시아 역사 기행','12세사':'세계사',
    '12역현':'역사로 탐구하는 현대 세계','12법사':'법과 사회','12정치':'정치',
    '12경제':'경제','12사문':'사회문제 탐구','12사탐':'사회과학 탐구',
    '12기지':'기후변화와 지속가능한 세계','12금융':'금융과 경제생활',
    '12국관':'국제 관계의 이해','12세지':'세계지리','12여지':'여행지리',
    '12도탐':'도시의 미래 탐구',
    '12물리':'물리학','12화학':'화학','12생과':'생명과학','12지구':'지구과학',
    '12역학':'역학과 에너지','12전자':'전자기와 양자','12물에':'물질과 에너지',
    '12반응':'화학 반응의 세계','12세포':'세포와 물질대사','12유전':'생물의 유전',
    '12행우':'행성우주과학','12지시':'지구시스템과학','12기환':'기후변화와 환경생태',
    '12과사':'과학의 역사와 문화','12융탐':'융합과학탐구',
    '12윤사':'윤리와 사상','12윤탐':'윤리 문제 탐구','12인윤':'인간과 윤리','12현윤':'현대사회와 윤리',
    '12기가':'기술·가정','12로봇':'로봇과 공학세계','12생활':'생활과학 탐구',
    '12아동':'아동발달과 부모','12자립':'생애 설계와 자립','12지재':'지식재산 일반','12창공':'창의 공학 설계',
    '12정':'정보','12데과':'데이터 과학','12소생':'소프트웨어와 생활','12인기':'인공지능 기초',
    '12음':'음악','12감비':'음악 감상과 비평','12연창':'음악 연주와 창작','12음미':'음악과 미디어',
    '12미':'미술','12미감':'미술 감상과 비평','12미매':'미술과 매체','12미창':'미술 창작',
    '12체육1':'체육1','12체육2':'체육2',
    '12스과':'스포츠 과학','12스생1':'스포츠 생활1','12스생2':'스포츠 생활2','12운건':'운동과 건강',
    '12연극':'연극',
    '12논리':'논리와 사고','12논술':'논술','12보건':'보건','12삶종':'삶과 종교',
    '12생환':'생태와 환경','12심리':'심리학','12인경':'인간과 경제활동',
    '12인철':'인간과 철학','12진로':'진로와 직업','12교이':'교육의 이해',
    '12한문':'한문','12한고':'한문 고전 읽기','12언한':'언어생활과 한자',
}
AREA_MAP = {
    '체육과': {'12스문': '스포츠 문화'},
    '영어과': {'12스문': '스페인어 독해와 작문'},
}

def get_code_prefix(code):
    prefix = code.strip('[]').split('-')[0]
    return prefix[:-2] if re.match(r'^12[가-힣A-Za-z]+0[1-9]$', prefix) else prefix

def get_subject_name(area, code):
    p = get_code_prefix(code)
    return AREA_MAP.get(area, {}).get(p) or SUBJECT_MAP.get(p) or p

# ─────────────────────────────────────────────────────────
#  2. 데이터 로드
# ─────────────────────────────────────────────────────────
@st.cache_data
def load_data():
    with open('data.json', encoding='utf-8') as f:
        return json.load(f)

def _gh_headers():
    token = st.secrets.get('GITHUB_TOKEN', '')
    return {'Authorization': f'token {token}', 'Accept': 'application/vnd.github.v3+json'} if token else {}

def _gh_repo():
    return st.secrets.get('GITHUB_REPO', 'yuno0154/curriculum')

@st.cache_data(ttl=60)
def load_edits_remote():
    """GitHub API에서 edits.json 읽기 (60초 캐시)"""
    try:
        url = f'https://api.github.com/repos/{_gh_repo()}/contents/edits.json'
        r = requests.get(url, headers=_gh_headers(), timeout=5)
        if r.ok:
            raw = base64.b64decode(r.json()['content']).decode('utf-8')
            return json.loads(raw)
    except Exception:
        pass
    # 로컬 폴백
    try:
        with open('edits.json', encoding='utf-8') as f:
            return json.load(f)
    except Exception:
        return {}

def save_edits_remote(edits: dict, commit_msg: str) -> tuple[bool, str]:
    """GitHub API로 edits.json 커밋"""
    try:
        token = st.secrets.get('GITHUB_TOKEN', '')
        if not token:
            return False, 'GitHub 토큰이 설정되지 않았습니다. (Streamlit Secrets 확인)'
        url = f'https://api.github.com/repos/{_gh_repo()}/contents/edits.json'
        headers = _gh_headers()

        # 현재 SHA 조회 (업데이트 시 필요)
        r = requests.get(url, headers=headers, timeout=5)
        sha = r.json().get('sha') if r.ok else None

        content = base64.b64encode(
            json.dumps(edits, ensure_ascii=False, indent=2).encode('utf-8')
        ).decode()

        payload = {
            'message': commit_msg,
            'content': content,
            'committer': {'name': '성취기준 시스템', 'email': 'noreply@school.kr'},
        }
        if sha:
            payload['sha'] = sha

        r = requests.put(url, headers=headers, json=payload, timeout=10)
        if r.ok:
            load_edits_remote.clear()   # 캐시 무효화
            return True, 'GitHub에 저장됐습니다.'
        else:
            return False, r.json().get('message', '저장 실패')
    except Exception as e:
        return False, str(e)

# ─────────────────────────────────────────────────────────
#  3. 페이지 설정
# ─────────────────────────────────────────────────────────
st.set_page_config(
    page_title='성취기준 검색',
    page_icon='📚',
    layout='wide',
    initial_sidebar_state='collapsed',
)

st.markdown("""
<style>
    .block-container { padding-top: 2rem; max-width: 1100px; }
    .code-cell { font-family: monospace; font-weight: 700; color: #818cf8;
                 font-size: 0.85rem; white-space: nowrap; }
    .stmt-cell { font-size: 0.95rem; line-height: 1.7; }
    .edited-mark { color: #f472b6; font-size: 0.75rem; }
    div[data-testid="stExpander"] summary { font-size: 0.85rem; }
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────
#  4. 세션 상태 초기화
# ─────────────────────────────────────────────────────────
if 'edits' not in st.session_state:
    st.session_state.edits = load_edits_remote()

data = load_data()

def get_stmt(item):
    return st.session_state.edits.get(item['code'], {}).get('statement', item['statement'])

def is_edited(code):
    return code in st.session_state.edits

# ─────────────────────────────────────────────────────────
#  5. 헤더
# ─────────────────────────────────────────────────────────
st.markdown('# 📚 성취기준 검색')
st.caption('2022 개정 교육과정 성취기준 통합 검색 시스템')
st.divider()

# ─────────────────────────────────────────────────────────
#  6. 메인 탭
# ─────────────────────────────────────────────────────────
tab_subject, tab_keyword = st.tabs(['📂  과목별 탐색', '🔍  성취기준 검색'])

# ════════════════════════════════════════════════════════
#  탭 1: 과목별 탐색
# ════════════════════════════════════════════════════════
with tab_subject:
    col_opt, col_info = st.columns([3, 1])

    with col_opt:
        level = st.radio('학교급', ['중학교', '고등학교'], horizontal=True, key='level')

    items_to_show = []
    title = ''

    if level == '중학교':
        subjects = sorted(set(d['subject'] for d in data if d['level'] == '중학교'))
        subject = st.selectbox('과목', subjects, key='ms_subject')
        items_to_show = sorted(
            [d for d in data if d['level'] == '중학교' and d['subject'] == subject],
            key=lambda x: x['code']
        )
        title = subject

    else:  # 고등학교
        areas = sorted(set(d['subject'] for d in data if d['level'] == '고등학교'))
        col_a, col_b = st.columns(2)
        with col_a:
            area = st.selectbox('교과', areas, key='hs_area')
        with col_b:
            sub_names = sorted(set(
                get_subject_name(d['subject'], d['code'])
                for d in data if d['level'] == '고등학교' and d['subject'] == area
            ))
            sub_name = st.selectbox('과목', sub_names, key='hs_sub')

        items_to_show = sorted(
            [d for d in data
             if d['level'] == '고등학교'
             and d['subject'] == area
             and get_subject_name(d['subject'], d['code']) == sub_name],
            key=lambda x: x['code']
        )
        title = f'{area} › {sub_name}'

    if items_to_show:
        with col_info:
            st.metric('성취기준', f'{len(items_to_show)}개')

        st.markdown(f'#### {title}')

        for item in items_to_show:
            stmt   = get_stmt(item)
            edited = is_edited(item['code'])

            c_code, c_stmt, c_edit = st.columns([2, 8, 1])

            with c_code:
                mark = ' 🔵' if edited else ''
                st.markdown(
                    f'<div class="code-cell">{item["code"]}{mark}</div>',
                    unsafe_allow_html=True
                )

            with c_stmt:
                st.markdown(f'<div class="stmt-cell">{stmt}</div>', unsafe_allow_html=True)

            with c_edit:
                if st.button('✏️', key=f'ebtn_{item["code"]}', help='수정'):
                    st.session_state[f'edit_open_{item["code"]}'] = True

            # 편집 패널
            if st.session_state.get(f'edit_open_{item["code"]}'):
                with st.container(border=True):
                    new_val = st.text_area(
                        f'진술문 수정 — {item["code"]}',
                        value=stmt,
                        key=f'ta_{item["code"]}',
                        height=90,
                    )
                    bc1, bc2, bc3 = st.columns([1, 1, 4])
                    with bc1:
                        if st.button('저장', key=f'save_{item["code"]}', type='primary'):
                            new_val = new_val.strip()
                            if new_val and new_val != item['statement']:
                                st.session_state.edits[item['code']] = {
                                    'statement': new_val,
                                    'original':  item['statement'],
                                    'edited_at': datetime.now().isoformat(timespec='seconds'),
                                }
                            else:
                                st.session_state.edits.pop(item['code'], None)

                            ok, msg = save_edits_remote(
                                st.session_state.edits,
                                f'성취기준 수정: {item["code"]}'
                            )
                            st.session_state[f'edit_open_{item["code"]}'] = False
                            if ok:
                                st.success(msg)
                            else:
                                st.warning(f'로컬 저장은 됐으나 GitHub 연동 실패: {msg}')
                            st.rerun()

                    with bc2:
                        if st.button('취소', key=f'cancel_{item["code"]}'):
                            st.session_state[f'edit_open_{item["code"]}'] = False
                            st.rerun()

                    if edited:
                        with bc3:
                            orig = st.session_state.edits[item['code']].get('original', item['statement'])
                            st.caption(f'원본: {orig}')
                        if st.button('↩ 원본 복원', key=f'reset_{item["code"]}'):
                            st.session_state.edits.pop(item['code'], None)
                            ok, msg = save_edits_remote(
                                st.session_state.edits,
                                f'성취기준 복원: {item["code"]}'
                            )
                            st.session_state[f'edit_open_{item["code"]}'] = False
                            st.rerun()

            st.divider()

# ════════════════════════════════════════════════════════
#  탭 2: 성취기준 키워드 검색
# ════════════════════════════════════════════════════════
with tab_keyword:
    query = st.text_input(
        '키워드',
        placeholder='성취기준 키워드를 입력하세요...',
        key='kw_input',
        label_visibility='collapsed',
    )

    if query:
        q = query.lower()
        filtered = sorted(
            [d for d in data
             if q in get_stmt(d).lower() or q in d['code'].lower()],
            key=lambda x: x['code']
        )

        st.caption(f'총 **{len(filtered)}**개 성취기준 검색됨')

        # 과목별 그룹핑
        groups: dict[str, list] = {}
        for d in filtered:
            if d['level'] == '중학교':
                grp = f'[중학교] {d["subject"]}'
            else:
                sn  = get_subject_name(d['subject'], d['code'])
                grp = f'[고등학교] {d["subject"]} › {sn}'
            groups.setdefault(grp, []).append(d)

        for grp_key, items in groups.items():
            with st.expander(f'**{grp_key}** — {len(items)}개', expanded=True):
                for item in items:
                    stmt = get_stmt(item)
                    # 키워드 하이라이트 (마크다운 bold)
                    highlighted = re.sub(
                        f'({re.escape(query)})',
                        r'**\1**',
                        stmt,
                        flags=re.IGNORECASE
                    )
                    c1, c2 = st.columns([2, 8])
                    with c1:
                        mark = ' 🔵' if is_edited(item['code']) else ''
                        st.markdown(
                            f'<div class="code-cell">{item["code"]}{mark}</div>',
                            unsafe_allow_html=True
                        )
                    with c2:
                        st.markdown(highlighted)
    else:
        st.info('성취기준 키워드를 입력하면 결과가 나타납니다.')

# ─────────────────────────────────────────────────────────
#  7. 사이드바: 편집 현황
# ─────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown('### 📝 수정 현황')
    edited_codes = list(st.session_state.edits.keys())
    if edited_codes:
        st.caption(f'총 {len(edited_codes)}건 수정됨')
        for code in edited_codes:
            st.markdown(f'- `{code}`')
        st.divider()
        if st.button('🔄 서버에서 최신 수정본 불러오기'):
            load_edits_remote.clear()
            st.session_state.edits = load_edits_remote()
            st.rerun()
    else:
        st.caption('수정된 성취기준 없음')
