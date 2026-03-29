// ─────────────────────────────────────────
//  app.js — 성취기준 검색 대시보드 v3
// ─────────────────────────────────────────

/* ── 1. 과목명 매핑 ──────────────────────────────────── */
const SUBJECT_MAP = {
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
};
const AREA_MAP = {
  '체육과': { '12스문':'스포츠 문화' },
  '영어과': { '12스문':'스페인어 독해와 작문' },
};

/* ── 2. 헬퍼 ─────────────────────────────────────────── */
function getCodePrefix(code) {
  const prefix = code.replace(/^\[|\]$/g,'').split('-')[0];
  return /^12[가-힣A-Za-z]+0[1-9]$/.test(prefix) ? prefix.slice(0,-2) : prefix;
}
function getSubjectName(area, code) {
  const p = getCodePrefix(code);
  return AREA_MAP[area]?.[p] ?? SUBJECT_MAP[p] ?? p;
}
function escapeHtml(s) {
  return s.replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;').replace(/"/g,'&quot;');
}
function emptyState(emoji, msg) {
  return `<div class="empty-state"><span>${emoji}</span><p>${msg}</p></div>`;
}
function sortByCode(arr) {
  return [...arr].sort((a,b) => a.code.localeCompare(b.code, 'ko'));
}

/* ── 3. 상태 ──────────────────────────────────────────── */
let allData = [];   // data.json
let edits   = {};   // edits.json: { code: { statement, original } }
let kwTimer = null;

/* ── 4. 초기화 ────────────────────────────────────────── */
async function init() {
  try {
    const [dataRes, editsRes] = await Promise.all([
      fetch('data.json'),
      fetch('edits.json').catch(() => null),
    ]);
    if (!dataRes.ok) throw new Error('data.json 로드 실패');
    allData = await dataRes.json();
    if (editsRes && editsRes.ok) edits = await editsRes.json();
  } catch (e) {
    document.getElementById('subjectResults').innerHTML = emptyState('⚠️', e.message);
    return;
  }
  renderMiddleSubjects();
  renderHighSubjects();
  setupListeners();
}

/* ── 5. 과목 목록 ─────────────────────────────────────── */
function renderMiddleSubjects() {
  const wrap = document.getElementById('middleSubjectList');
  wrap.innerHTML = '';
  const subjects = [...new Set(allData.filter(d=>d.level==='중학교').map(d=>d.subject))].sort();
  subjects.forEach(sub => {
    const btn = document.createElement('button');
    btn.className = 'subject-chip';
    btn.textContent = sub;
    btn.addEventListener('click', () => {
      clearChipSelection(); btn.classList.add('active');
      const items = sortByCode(allData.filter(d=>d.level==='중학교'&&d.subject===sub));
      renderSubjectResults(sub, items);
    });
    wrap.appendChild(btn);
  });
}

function renderHighSubjects() {
  const wrap = document.getElementById('highSubjectList');
  const groups = {};
  allData.filter(d=>d.level==='고등학교').forEach(d => {
    const sn = getSubjectName(d.subject, d.code);
    if (!groups[d.subject]) groups[d.subject] = new Set();
    groups[d.subject].add(sn);
  });
  wrap.innerHTML = '';
  Object.keys(groups).sort().forEach(area => {
    const names = [...groups[area]].sort();
    const section = document.createElement('div');
    section.className = 'accordion-section';

    const hdr = document.createElement('button');
    hdr.className = 'accordion-header';
    hdr.innerHTML = `
      <span class="accordion-title">${area}</span>
      <span class="accordion-count">${names.length}개 과목</span>
      <svg class="accordion-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5">
        <polyline points="6 9 12 15 18 9"/>
      </svg>`;

    const body = document.createElement('div');
    body.className = 'accordion-body';
    names.forEach(sn => {
      const btn = document.createElement('button');
      btn.className = 'subject-chip';
      btn.textContent = sn;
      btn.addEventListener('click', () => {
        clearChipSelection(); btn.classList.add('active');
        const items = sortByCode(allData.filter(d =>
          d.level==='고등학교' && d.subject===area && getSubjectName(d.subject,d.code)===sn
        ));
        renderSubjectResults(`${area} › ${sn}`, items);
      });
      body.appendChild(btn);
    });

    hdr.addEventListener('click', () => {
      const open = section.classList.contains('open');
      wrap.querySelectorAll('.accordion-section.open').forEach(s=>s.classList.remove('open'));
      if (!open) section.classList.add('open');
    });
    section.appendChild(hdr); section.appendChild(body);
    wrap.appendChild(section);
  });
}

/* ── 6. 탭 / 학교급 리스너 ───────────────────────────── */
function setupListeners() {
  document.querySelectorAll('.main-tab-btn').forEach(btn => {
    btn.addEventListener('click', () => {
      document.querySelectorAll('.main-tab-btn').forEach(b=>b.classList.toggle('active',b===btn));
      document.getElementById('tabSubject').style.display = btn.dataset.tab==='subject' ? '' : 'none';
      document.getElementById('tabKeyword').style.display  = btn.dataset.tab==='keyword'  ? '' : 'none';
    });
  });
  document.querySelectorAll('.level-btn').forEach(btn => {
    btn.addEventListener('click', () => {
      document.querySelectorAll('.level-btn').forEach(b=>b.classList.toggle('active',b===btn));
      document.getElementById('middleSubjectList').style.display = btn.dataset.level==='middle' ? '' : 'none';
      document.getElementById('highSubjectList').style.display   = btn.dataset.level==='high'   ? '' : 'none';
      clearChipSelection();
      document.getElementById('subjectResults').innerHTML = '';
    });
  });
  document.getElementById('keywordInput').addEventListener('input', e => {
    clearTimeout(kwTimer);
    kwTimer = setTimeout(() => renderKeywordResults(e.target.value.trim()), 250);
  });
}
function clearChipSelection() {
  document.querySelectorAll('.subject-chip.active').forEach(b=>b.classList.remove('active'));
}

/* ── 7. 과목별 성취기준 표시 ──────────────────────────── */
function renderSubjectResults(title, items) {
  const wrap = document.getElementById('subjectResults');
  wrap.innerHTML = '';
  if (!items.length) { wrap.innerHTML = emptyState('😓','성취기준이 없습니다.'); return; }

  const hdr = document.createElement('div');
  hdr.className = 'results-header';
  hdr.innerHTML = `<h2>${title}</h2><span class="count-badge">${items.length}개</span>`;
  wrap.appendChild(hdr);

  wrap.appendChild(buildList(items));
  setTimeout(() => wrap.scrollIntoView({behavior:'smooth',block:'start'}), 80);
}

/* ── 8. 키워드 검색 ───────────────────────────────────── */
function renderKeywordResults(query) {
  const wrap = document.getElementById('keywordResults');
  if (!query) { wrap.innerHTML = emptyState('🔍','성취기준 키워드를 입력해 주세요.'); return; }

  const q = query.toLowerCase();
  const filtered = allData.filter(d => {
    const stmt = (edits[d.code]?.statement ?? d.statement).toLowerCase();
    return stmt.includes(q) || d.code.toLowerCase().includes(q);
  });

  if (!filtered.length) { wrap.innerHTML = emptyState('😓',`'${query}' 검색 결과가 없습니다.`); return; }

  const groups = {};
  sortByCode(filtered).forEach(d => {
    const sn = d.level==='중학교' ? d.subject : `${d.subject} › ${getSubjectName(d.subject,d.code)}`;
    const key = `[${d.level}] ${sn}`;
    if (!groups[key]) groups[key] = [];
    groups[key].push(d);
  });

  wrap.innerHTML = '';
  const total = document.createElement('p');
  total.className = 'search-total';
  total.textContent = `총 ${filtered.length}개 성취기준 검색됨`;
  wrap.appendChild(total);

  Object.entries(groups).forEach(([key, items]) => {
    const sec = document.createElement('div');
    sec.className = 'keyword-group';
    const hdr = document.createElement('div');
    hdr.className = 'results-header';
    hdr.innerHTML = `<h3>${key}</h3><span class="count-badge">${items.length}개</span>`;
    sec.appendChild(hdr);
    sec.appendChild(buildList(items, query));
    wrap.appendChild(sec);
  });
}

/* ── 9. 목록 빌더 (코드 순서 세로 리스트) ─────────────── */
function buildList(items, highlight = '') {
  const list = document.createElement('div');
  list.className = 'result-list';
  items.forEach(item => list.appendChild(createRow(item, highlight)));
  return list;
}

function createRow(item, highlight = '') {
  const edit  = edits[item.code];
  const stmt  = edit?.statement ?? item.statement;
  const isEd  = !!edit;

  let displayStmt = escapeHtml(stmt);
  if (highlight) {
    const re = new RegExp(`(${highlight.replace(/[.*+?^${}()|[\]\\]/g,'\\$&')})`, 'gi');
    displayStmt = displayStmt.replace(re,'<mark class="kw">$1</mark>');
  }

  const row = document.createElement('div');
  row.className = 'result-row' + (isEd ? ' edited' : '');
  row.dataset.code = item.code;
  row.dataset.hl   = highlight;
  row.innerHTML = `
    <span class="row-code">${item.code}${isEd ? '<span class="edited-dot" title="수정됨">●</span>' : ''}</span>
    <div class="row-body">
      <p class="row-stmt">${displayStmt}</p>
      <textarea class="row-input" style="display:none">${escapeHtml(stmt)}</textarea>
      <div class="row-actions" style="display:none">
        <button class="btn-save-edit">저장</button>
        <button class="btn-cancel-edit">취소</button>
        ${isEd ? '<button class="btn-reset-edit">원본 복원</button>' : ''}
      </div>
      <p class="row-save-status"></p>
    </div>
    <button class="btn-edit" title="수정">
      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
        <path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7"/>
        <path d="M18.5 2.5a2.121 2.121 0 0 1 3 3L12 15l-4 1 1-4 9.5-9.5z"/>
      </svg>
    </button>`;

  row.querySelector('.btn-edit').addEventListener('click', () => startRowEdit(row));
  row.querySelector('.btn-save-edit').addEventListener('click', () => saveRowEdit(row, item));
  row.querySelector('.btn-cancel-edit').addEventListener('click', () => cancelRowEdit(row));
  row.querySelector('.btn-reset-edit')?.addEventListener('click', () => resetRowEdit(row, item));
  return row;
}

/* ── 10. 인라인 편집 ──────────────────────────────────── */
function startRowEdit(row) {
  row.querySelector('.row-stmt').style.display  = 'none';
  row.querySelector('.row-input').style.display = 'block';
  row.querySelector('.row-actions').style.display = 'flex';
  row.querySelector('.btn-edit').style.display  = 'none';
  row.classList.add('editing');

  const ta = row.querySelector('.row-input');
  ta.style.height = 'auto';
  ta.style.height = ta.scrollHeight + 'px';
  ta.addEventListener('input', () => { ta.style.height='auto'; ta.style.height=ta.scrollHeight+'px'; });
  ta.focus();
}

function cancelRowEdit(row) {
  row.querySelector('.row-stmt').style.display  = '';
  row.querySelector('.row-input').style.display = 'none';
  row.querySelector('.row-actions').style.display = 'none';
  row.querySelector('.btn-edit').style.display  = '';
  row.classList.remove('editing');
}

async function saveRowEdit(row, item) {
  const newVal  = row.querySelector('.row-input').value.trim();
  const status  = row.querySelector('.row-save-status');
  if (!newVal) return;

  status.textContent = '저장 중...';
  status.className = 'row-save-status saving';

  try {
    const res = await fetch('/api/edit', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ code: item.code, statement: newVal }),
    });
    const json = await res.json();
    if (!res.ok) throw new Error(json.error || '서버 오류');

    // 메모리 반영
    if (newVal !== item.statement) {
      edits[item.code] = {
        statement: newVal,
        original: item.statement,
      };
    } else {
      delete edits[item.code];
    }

    // 행 교체
    row.replaceWith(createRow(item, row.dataset.hl || ''));

    const gitMsg = json.git && json.git !== 'git 저장소 아님'
      ? ` (${json.git})` : '';
    // 저장 완료 토스트
    showToast('저장 완료' + gitMsg);

  } catch (e) {
    status.textContent = '오류: ' + e.message;
    status.className = 'row-save-status error';
  }
}

async function resetRowEdit(row, item) {
  const status = row.querySelector('.row-save-status');
  status.textContent = '복원 중...';
  status.className = 'row-save-status saving';

  try {
    const res = await fetch('/api/reset', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ code: item.code }),
    });
    const json = await res.json();
    if (!res.ok) throw new Error(json.error || '서버 오류');

    delete edits[item.code];
    row.replaceWith(createRow(item, row.dataset.hl || ''));
    showToast('원본으로 복원됐습니다.');
  } catch (e) {
    status.textContent = '오류: ' + e.message;
    status.className = 'row-save-status error';
  }
}

/* ── 11. 토스트 알림 ──────────────────────────────────── */
function showToast(msg) {
  const t = document.createElement('div');
  t.className = 'toast';
  t.textContent = msg;
  document.body.appendChild(t);
  requestAnimationFrame(() => t.classList.add('show'));
  setTimeout(() => {
    t.classList.remove('show');
    t.addEventListener('transitionend', () => t.remove());
  }, 2500);
}

init();
