import os
import json
import tempfile
import streamlit as st
import streamlit.components.v1 as components

# ==========================================
# 1. 페이지 설정 및 초기 데이터 (Single Source of Truth)
# ==========================================
st.set_page_config(page_title="역사적 사건 인과관계 지도", layout="wide")

INITIAL_EVENTS_DATA = {
    "map_size": {"x": 10000, "y": 10000},
    "screen_position": {"x": 5000, "y": 5000},
    "nations": [
        {"id": 1, "name": "고구려", "color": "#27ae60"},
        {"id": 2, "name": "백제", "color": "#f39c12"},
        {"id": 3, "name": "신라", "color": "#2980b9"},
        {"id": 4, "name": "당", "color": "#c0392b"},
        {"id": 5, "name": "수", "color": "#8e44ad"},
        {"id": 6, "name": "대가야", "color": "#7f8c8d"}
    ],
    "nodes": [
        {"id": 1, "name": "성왕의 한강 수복", "position": {"x": 5100, "y": 5150}, "year": 551, "description": "백제 성왕이 신라 진흥왕과 연합하여 고구려를 공격, 한강 하류 유역을 수복한 사건입니다.", "causes": [], "results": [2], "nations": [1, 2, 3]},
        {"id": 2, "name": "진흥왕의 한강 차지", "position": {"x": 5300, "y": 5150}, "year": 553, "description": "신라 진흥왕이 나제동맹을 깨고 기습적으로 백제를 공격하여 한강 유역을 독차지하고 신주를 설치했습니다.", "causes": [1], "results": [3], "nations": [2, 3]},
        {"id": 3, "name": "관산성 전투", "position": {"x": 5500, "y": 5150}, "year": 554, "description": "신라의 배신에 분노한 백제 성왕이 대가야와 연합하여 신라를 공격했으나, 관산성에서 전사하고 대패한 전투입니다.", "causes": [2], "results": [6], "nations": [2, 3, 6]},
        {"id": 4, "name": "살수대첩", "position": {"x": 5100, "y": 5350}, "year": 612, "description": "고구려의 을지문덕이 살수(청천강)에서 수나라의 30만 별동대를 크게 물리친 전투입니다.", "causes": [], "results": [5], "nations": [1, 5]},
        {"id": 5, "name": "안시성 전투", "position": {"x": 5300, "y": 5350}, "year": 645, "description": "고구려 안시성에서 당나라 태종의 대군을 맞아 약 88일간의 치열한 공방전 끝에 당군을 물리친 전투입니다.", "causes": [4], "results": [6], "nations": [1, 4]},
        {"id": 6, "name": "나당 동맹 체결", "position": {"x": 5500, "y": 5250}, "year": 648, "description": "백제의 잦은 공격으로 위기에 처한 신라(김춘추)가 당나라로 건너가 고구려와 백제를 멸망시키기 위한 군사 동맹을 맺은 사건입니다.", "causes": [3, 5], "results": [7, 9], "nations": [3, 4]},
        {"id": 7, "name": "황산벌 전투", "position": {"x": 5700, "y": 5150}, "year": 660, "description": "나당 연합군이 백제를 공격하자, 계백 장군이 이끄는 5천 결사대가 황산벌에서 김유신의 5만 신라군에 맞서 싸운 전투입니다.", "causes": [6], "results": [8], "nations": [2, 3, 4]},
        {"id": 8, "name": "백제 멸망", "position": {"x": 5900, "y": 5150}, "year": 660, "description": "황산벌 전투 패배 후 사비성이 나당 연합군에게 함락되며 의자왕이 항복, 백제가 멸망하게 됩니다.", "causes": [7], "results": [9, 10], "nations": [2, 3, 4]},
        {"id": 9, "name": "고구려 멸망", "position": {"x": 5900, "y": 5350}, "year": 668, "description": "오랜 전쟁과 연개소문 사후의 내분으로 국력이 약해진 고구려가 나당 연합군의 공격을 받고 평양성이 함락되며 멸망했습니다.", "causes": [6, 8], "results": [10], "nations": [1, 3, 4]},
        {"id": 10, "name": "기벌포 해전", "position": {"x": 6100, "y": 5250}, "year": 676, "description": "신라가 한반도 전체를 지배하려는 당나라에 맞서 싸운 나당 전쟁의 마지막 전투. 기벌포에서 당의 수군을 궤멸시켜 삼국통일을 완수했습니다.", "causes": [8, 9], "results": [], "nations": [3, 4]}
    ]
}

# ==========================================
# 2. Python 기반 핵심 비즈니스 로직 & 히스토리 스택
# ==========================================
if 'events_data' not in st.session_state:
    st.session_state.events_data = json.loads(json.dumps(INITIAL_EVENTS_DATA))
if 'history' not in st.session_state:
    st.session_state.history = [json.loads(json.dumps(INITIAL_EVENTS_DATA))]
if 'history_idx' not in st.session_state:
    st.session_state.history_idx = 0
if 'active_nations' not in st.session_state:
    st.session_state.active_nations = {n['id']: True for n in INITIAL_EVENTS_DATA['nations']}

def push_history():
    """상태 변경 시 Python 스택에 Undo 히스토리 저장"""
    st.session_state.history = st.session_state.history[:st.session_state.history_idx + 1]
    st.session_state.history.append(json.loads(json.dumps(st.session_state.events_data)))
    st.session_state.history_idx += 1

def do_undo():
    """실행 취소 (Undo)"""
    if st.session_state.history_idx > 0:
        st.session_state.history_idx -= 1
        st.session_state.events_data = json.loads(json.dumps(st.session_state.history[st.session_state.history_idx]))

def do_redo():
    """다시 실행 (Redo)"""
    if st.session_state.history_idx < len(st.session_state.history) - 1:
        st.session_state.history_idx += 1
        st.session_state.events_data = json.loads(json.dumps(st.session_state.history[st.session_state.history_idx]))

def reset_screen():
    """화면 위치 초기화"""
    st.session_state.events_data['screen_position']['x'] = INITIAL_EVENTS_DATA['screen_position']['x']
    st.session_state.events_data['screen_position']['y'] = INITIAL_EVENTS_DATA['screen_position']['y']
    push_history()

def reset_nodes():
    """노드 위치 초기화"""
    for node in st.session_state.events_data['nodes']:
        init_node = next((n for n in INITIAL_EVENTS_DATA['nodes'] if n['id'] == node['id']), None)
        if init_node:
            node['position']['x'] = init_node['position']['x']
            node['position']['y'] = init_node['position']['y']
    push_history()

def reset_all():
    """전체 초기화"""
    st.session_state.events_data = json.loads(json.dumps(INITIAL_EVENTS_DATA))
    push_history()

# ==========================================
# 3. 기존 커스텀 CSS (디자인 100% 유지)
# ==========================================
st.markdown("""
<style>
#main-container-anchor + div > div[data-testid="stVerticalBlock"] {
    border: 1px solid #000000;
    border-radius: 8px;
    background-color: #ffffff;
    padding: 0 !important;
    gap: 0 !important;
    overflow: hidden;
}
#main-container-anchor + div > div[data-testid="stVerticalBlock"] > div:first-child {
    padding: 10px 20px;
    align-items: center;
    background-color: #ffffff;
}
[data-testid="stPopover"] > button {
    background-color: #f1f2f6 !important;
    border: 1px solid #dfe6e9 !important;
    border-radius: 20px !important;
    font-size: 14px !important;
    font-weight: bold !important;
    color: #2d3436 !important;
    padding: 2px 14px !important;
    margin-top: 6px;
    transition: background-color 0.2s;
}
[data-testid="stPopover"] > button:hover {
    background-color: #dfe6e9 !important;
}
[data-testid="stCheckbox"] {
    background-color: rgba(255, 255, 255, 0.95);
    border: 1px solid #000000 !important;
    border-radius: 25px !important;
    padding: 4px 10px !important;
    display: inline-flex;
    justify-content: center;
    align-items: center;
    margin-top: 6px;
    transition: opacity 0.2s;
}
[data-testid="stCheckbox"] div[role="checkbox"],
[data-testid="stCheckbox"] input[type="checkbox"] {
    display: none !important;
}
[data-testid="stCheckbox"] label p {
    font-size: 14px !important;
    font-weight: bold !important;
    color: #2d3436 !important;
    margin: 0 !important;
    display: flex;
    align-items: center;
    gap: 4px;
}
[data-testid="stCheckbox"]:has(input:not(:checked)) {
    opacity: 0.3;
}
</style>
""", unsafe_allow_html=True)

# ==========================================
# 4. 상단 UI: Python 기반 제어 컨트롤러
# ==========================================
st.markdown('<div id="main-container-anchor"></div>', unsafe_allow_html=True)

with st.container():
    col_title, col_menu, col_filter = st.columns([1.5, 1.5, 3.5], gap="small")
    
    with col_title:
        st.markdown("<h1 style='font-size: 22px; font-weight: 900; color: #2d3436; margin: 10px 0 0 0; white-space: nowrap;'>역사적 사건 인과관계 지도</h1>", unsafe_allow_html=True)
    
    with col_menu:
        m_col1, m_col2, m_col3 = st.columns(3)
        with m_col1:
            with st.popover("파일"):
                # 파이썬 Native 다운로드 & 파일 업로드 연결
                st.download_button(
                    label="저장하기",
                    data=json.dumps(st.session_state.events_data, indent=2, ensure_ascii=False),
                    file_name="history_map.json",
                    mime="application/json",
                    use_container_width=True
                )
                uploaded_file = st.file_uploader("불러오기", type=["json"], label_visibility="collapsed")
                if uploaded_file is not None:
                    try:
                        loaded_data = json.load(uploaded_file)
                        st.session_state.events_data = loaded_data
                        push_history()
                        st.rerun()
                    except Exception:
                        st.error("JSON 파일 형식이 올바르지 않습니다.")
        with m_col2:
            with st.popover("명령"):
                st.button("실행 취소", use_container_width=True, on_click=do_undo, disabled=(st.session_state.history_idx <= 0))
                st.button("다시 실행", use_container_width=True, on_click=do_redo, disabled=(st.session_state.history_idx >= len(st.session_state.history) - 1))
        with m_col3:
            with st.popover("화면"):
                st.button("화면 위치 초기화", use_container_width=True, on_click=reset_screen)
                st.button("노드 위치 초기화", use_container_width=True, on_click=reset_nodes)
                st.button("화면 전체 초기화", use_container_width=True, on_click=reset_all)
                
    with col_filter:
        filter_cols = st.columns(len(st.session_state.events_data["nations"]))
        color_emoji = {"#27ae60": "🟢", "#f39c12": "🟠", "#2980b9": "🔵", "#c0392b": "🔴", "#8e44ad": "🟣", "#7f8c8d": "⚪"}
        
        for i, nation in enumerate(st.session_state.events_data["nations"]):
            with filter_cols[i]:
                emoji = color_emoji.get(nation["color"], "⚫")
                is_checked = st.session_state.active_nations.get(nation['id'], True)
                new_val = st.checkbox(f"{emoji} {nation['name']}", value=is_checked, key=f"filter_{nation['id']}")
                st.session_state.active_nations[nation['id']] = new_val

    st.markdown("<hr style='margin: 0; border: none; border-top: 2px solid #e2e8f0;'>", unsafe_allow_html=True)

# ==========================================
# 5. 하단 지도: Custom Component (JS Pure Renderer)
# ==========================================
COMPONENT_DIR = os.path.join(tempfile.gettempdir(), "streamlit_history_map_comp")
os.makedirs(COMPONENT_DIR, exist_ok=True)
index_html_path = os.path.join(COMPONENT_DIR, "index.html")

html_content = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <script src="https://cdn.jsdelivr.net/npm/streamlit-component-lib@1.4.0/dist/streamlit-component-lib.js"></script>
    <style>
        body { margin: 0; padding: 0; font-family: 'Malgun Gothic', sans-serif; overflow: hidden; background-color: #ffffff; }
        #map-container { display: flex; flex-direction: column; width: 100vw; height: 100vh; background-color: #ffffff; padding: 0; box-sizing: border-box; overflow: hidden; }
        #bordered-box { display: flex; flex-direction: column; width: 100%; height: 100%; position: relative; outline: none; }
        #network-container { flex: 1; position: relative; overflow: hidden; background-color: #ffffff; box-sizing: border-box; }
        svg { width: 100%; height: 100%; cursor: grab; }
        svg:active { cursor: grabbing; }
        .node { cursor: grab; transition: opacity 0.3s; }
        .node:active { cursor: grabbing; }
        .node.dimmed { opacity: 0.15; pointer-events: none; }
        .node .node-border { stroke: #fff; stroke-width: 3px; fill: none; transition: stroke-width 0.2s, stroke 0.2s; }
        .node.hover-active .node-border { stroke-width: 5px; stroke: #333; }
        .node text { font-size: 14px; font-weight: bold; pointer-events: none; text-anchor: middle; fill: #2d3436; }
        .node text.year { font-size: 12px; font-weight: normal; fill: #636e72; }
        .edge { stroke: #b2bec3; stroke-width: 2.5px; transition: opacity 0.3s, stroke 0.3s; }
        .edge.dimmed { opacity: 0.15; }
        #side-panel {
            position: absolute; top: 0; right: -450px; width: 400px; height: 100%; background-color: #ffffff;
            box-shadow: -4px 0 15px rgba(0,0,0,0.1); transition: right 0.3s cubic-bezier(0.4, 0, 0.2, 1);
            padding: 30px 25px 30px 30px; box-sizing: border-box; z-index: 100; overflow-y: auto;
        }
        #side-panel.open { right: 0; }
        #panel-stripe { position: absolute; top: 0; left: 0; width: 6px; height: 100%; }
        #close-btn { position: absolute; top: 15px; right: 15px; background: none; border: none; font-size: 24px; cursor: pointer; color: #636e72; }
        h2 { margin-top: 0; color: #2d3436; font-size: 22px; margin-bottom: 10px; }
        .badge { display: inline-block; background: #dfe6e9; color: #2d3436; padding: 4px 8px; border-radius: 4px; font-size: 14px; margin-bottom: 20px; font-weight: bold; }
        p.desc { line-height: 1.6; color: #4a4a4a; font-size: 15px; margin-bottom: 25px; background-color: #f8f9fa; padding: 15px; border-radius: 8px; }
        .info-group { margin-bottom: 15px; font-size: 14px; }
        .info-label { font-weight: bold; color: #2d3436; margin-bottom: 5px; display: flex; align-items: center; }
        .info-value { color: #2d3436; padding-left: 10px; line-height: 1.5; }
        .event-link { color: #0984e3; text-decoration: none; cursor: pointer; font-weight: bold; transition: color 0.2s; }
        .event-link:hover { color: #74b9ff; text-decoration: underline; }
    </style>
</head>
<body>
<div id="map-container">
    <div id="bordered-box" tabindex="0">
        <div id="network-container">
            <svg id="network">
                <defs>
                    <marker id="arrow" viewBox="0 -5 10 10" refX="28" refY="0" markerWidth="6" markerHeight="6" orient="auto"><path d="M0,-5L10,0L0,5" fill="#b2bec3"></path></marker>
                    <marker id="arrow-cause" viewBox="0 -5 10 10" refX="28" refY="0" markerWidth="6" markerHeight="6" orient="auto"><path d="M0,-5L10,0L0,5" fill="#e74c3c"></path></marker>
                    <marker id="arrow-result" viewBox="0 -5 10 10" refX="28" refY="0" markerWidth="6" markerHeight="6" orient="auto"><path d="M0,-5L10,0L0,5" fill="#0984e3"></path></marker>
                </defs>
                <g id="edges-layer"></g>
                <g id="nodes-layer"></g>
            </svg>
            <div id="side-panel">
                <div id="panel-stripe"></div>
                <button id="close-btn">&times;</button>
                <div class="badge" id="panel-year"></div>
                <h2 id="panel-title"></h2>
                <p class="desc" id="panel-desc"></p>
                <div class="info-group"><div class="info-label">🚩 관련 국가</div><div class="info-value" id="panel-nations"></div></div>
                <div class="info-group"><div class="info-label">🔻 원인 사건 (이전)</div><div class="info-value" id="panel-causes"></div></div>
                <div class="info-group"><div class="info-label">🔹 결과 사건 (이후)</div><div class="info-value" id="panel-results"></div></div>
            </div>
        </div>
    </div>
</div>

<script>
    let appData = null;
    let activeNations = new Set();
    let draggedNode = null, offsetX = 0, offsetY = 0;
    let dragStartX = 0, dragStartY = 0;
    let isSignificantDrag = false; const DRAG_THRESHOLD = 5;
    let isPanning = false, panStartX = 0, panStartY = 0, panStartScreenX = 0, panStartScreenY = 0;

    const svg = document.getElementById('network');
    const edgesLayer = document.getElementById('edges-layer');
    const nodesLayer = document.getElementById('nodes-layer');
    const sidePanel = document.getElementById('side-panel');
    const borderedBox = document.getElementById('bordered-box');

    let nationMap = {};
    let edgeElements = [];
    let nodeElements = {};

    function onRender(event) {
        const data = event.detail.args;
        appData = data.events_data;
        activeNations = new Set(data.active_nations);

        nationMap = {};
        appData.nations.forEach(n => nationMap[n.id] = n);

        renderNetwork();
        updateViewBox();
        Streamlit.setFrameHeight(750);
    }

    Streamlit.events.addEventListener(Streamlit.RENDER_EVENT, onRender);
    Streamlit.init();

    // 단축키 이벤트 (Ctrl+Z, Ctrl+Y) -> Python 이벤트 전달
    window.addEventListener('keydown', (e) => {
        if (e.ctrlKey || e.metaKey) {
            const key = e.key ? e.key.toLowerCase() : '';
            const code = e.code;
            if (key === 'z' || key === 'ㅋ' || code === 'KeyZ') {
                e.preventDefault();
                Streamlit.setComponentValue({ action: 'undo' });
            } else if (key === 'y' || key === 'ㅛ' || code === 'KeyY') {
                e.preventDefault();
                Streamlit.setComponentValue({ action: 'redo' });
            }
        }
    });

    function updateViewBox() {
        if (!appData) return;
        const rect = svg.parentElement.getBoundingClientRect();
        if (rect.width === 0 || rect.height === 0) return;
        let currentX = appData.screen_position.x;
        let currentY = appData.screen_position.y;
        const maxX = appData.map_size.x - rect.width;
        const maxY = appData.map_size.y - rect.height;
        currentX = Math.max(0, Math.min(currentX, maxX));
        currentY = Math.max(0, Math.min(currentY, maxY));
        svg.setAttribute('viewBox', `${currentX} ${currentY} ${rect.width} ${rect.height}`);
    }

    function createPieSlices(g, nationIds, radius) {
        const sortedIds = [...nationIds].sort((a, b) => a - b);
        const count = sortedIds.length;
        if (count === 1) {
            const circle = document.createElementNS('http://www.w3.org/2000/svg', 'circle');
            circle.setAttribute('r', radius);
            circle.setAttribute('fill', nationMap[sortedIds[0]] ? nationMap[sortedIds[0]].color : '#95a5a6');
            g.appendChild(circle);
        } else {
            let startAngle = -Math.PI / 2;
            const angleStep = (2 * Math.PI) / count;
            for (let i = 0; i < count; i++) {
                const endAngle = startAngle + angleStep;
                const x1 = radius * Math.cos(startAngle);
                const y1 = radius * Math.sin(startAngle);
                const x2 = radius * Math.cos(endAngle);
                const y2 = radius * Math.sin(endAngle);
                const largeArcFlag = angleStep > Math.PI ? 1 : 0;
                const pathData = `M 0 0 L ${x1} ${y1} A ${radius} ${radius} 0 ${largeArcFlag} 1 ${x2} ${y2} Z`;
                const path = document.createElementNS('http://www.w3.org/2000/svg', 'path');
                path.setAttribute('d', pathData);
                path.setAttribute('fill', nationMap[sortedIds[i]] ? nationMap[sortedIds[i]].color : '#95a5a6');
                g.appendChild(path);
                startAngle = endAngle;
            }
        }
        const borderCircle = document.createElementNS('http://www.w3.org/2000/svg', 'circle');
        borderCircle.setAttribute('r', radius);
        borderCircle.setAttribute('class', 'node-border');
        g.appendChild(borderCircle);
    }

    function renderNetwork() {
        edgesLayer.innerHTML = ''; nodesLayer.innerHTML = '';
        edgeElements = []; nodeElements = {};

        const parsedEdges = [];
        appData.nodes.forEach(node => {
            (node.results || []).forEach(targetId => parsedEdges.push({ source: node.id, target: targetId }));
        });

        parsedEdges.forEach(edge => {
            const sourceNode = appData.nodes.find(n => n.id === edge.source);
            const targetNode = appData.nodes.find(n => n.id === edge.target);
            if (sourceNode && targetNode) {
                const line = document.createElementNS('http://www.w3.org/2000/svg', 'line');
                line.setAttribute('class', 'edge');
                line.setAttribute('marker-end', 'url(#arrow)');
                line.setAttribute('x1', sourceNode.position.x);
                line.setAttribute('y1', sourceNode.position.y);
                line.setAttribute('x2', targetNode.position.x);
                line.setAttribute('y2', targetNode.position.y);
                edgesLayer.appendChild(line);
                edgeElements.push({ line, source: sourceNode, target: targetNode });
            }
        });

        appData.nodes.forEach(node => {
            const g = document.createElementNS('http://www.w3.org/2000/svg', 'g');
            g.setAttribute('class', 'node');
            g.setAttribute('transform', `translate(${node.position.x}, ${node.position.y})`);
            createPieSlices(g, node.nations, 20);

            const textTitle = document.createElementNS('http://www.w3.org/2000/svg', 'text');
            textTitle.setAttribute('y', 38);
            textTitle.textContent = node.name;
            const textYear = document.createElementNS('http://www.w3.org/2000/svg', 'text');
            textYear.setAttribute('class', 'year');
            textYear.setAttribute('y', 53);
            textYear.textContent = node.year;

            g.appendChild(textTitle);
            g.appendChild(textYear);
            nodesLayer.appendChild(g);
            nodeElements[node.id] = g;

            g.addEventListener('mousedown', (e) => startDrag(e, node));
        });

        updateFilters();
    }

    function updateFilters() {
        appData.nodes.forEach(node => {
            const isActive = node.nations.some(id => activeNations.has(id));
            const g = nodeElements[node.id];
            if (isActive) {
                g.classList.remove('dimmed');
            } else {
                g.classList.add('dimmed');
                if (sidePanel.classList.contains('open') && document.getElementById('panel-title').textContent === node.name) {
                    closeSidebar();
                }
            }
        });
        edgeElements.forEach(e => {
            const sourceDimmed = nodeElements[e.source.id].classList.contains('dimmed');
            const targetDimmed = nodeElements[e.target.id].classList.contains('dimmed');
            if (!sourceDimmed && !targetDimmed) e.line.classList.remove('dimmed');
            else e.line.classList.add('dimmed');
        });
    }

    function getSVGPoint(evt) {
        const pt = svg.createSVGPoint();
        pt.x = evt.clientX; pt.y = evt.clientY;
        return pt.matrixTransform(svg.getScreenCTM().inverse());
    }

    svg.addEventListener('mousedown', (e) => {
        if (e.button !== 0) return;
        if (!e.target.closest('.node')) {
            isPanning = true;
            panStartX = e.clientX; panStartY = e.clientY;
            panStartScreenX = appData.screen_position.x;
            panStartScreenY = appData.screen_position.y;
            e.preventDefault();
        }
    });

    function startDrag(e, node) {
        e.preventDefault();
        const pt = getSVGPoint(e);
        draggedNode = node;
        isSignificantDrag = false;
        dragStartX = pt.x; dragStartY = pt.y;
        offsetX = pt.x - node.position.x; offsetY = pt.y - node.position.y;
        e.stopPropagation();
    }

    borderedBox.addEventListener('mousemove', (e) => {
        if (draggedNode) {
            const pt = getSVGPoint(e);
            const dx = pt.x - dragStartX; const dy = pt.y - dragStartY;
            if (!isSignificantDrag && Math.sqrt(dx * dx + dy * dy) > DRAG_THRESHOLD) {
                isSignificantDrag = true;
            }
            if (isSignificantDrag) {
                let newX = pt.x - offsetX; let newY = pt.y - offsetY;
                const limit = 50;
                newX = Math.max(limit, Math.min(newX, appData.map_size.x - limit));
                newY = Math.max(limit, Math.min(newY, appData.map_size.y - limit));
                draggedNode.position.x = newX; draggedNode.position.y = newY;
                nodeElements[draggedNode.id].setAttribute('transform', `translate(${newX}, ${newY})`);
                edgeElements.forEach(edge => {
                    if (edge.source.id === draggedNode.id || edge.target.id === draggedNode.id) {
                        edge.line.setAttribute('x1', edge.source.position.x); edge.line.setAttribute('y1', edge.source.position.y);
                        edge.line.setAttribute('x2', edge.target.position.x); edge.line.setAttribute('y2', edge.target.position.y);
                    }
                });
            }
        } else if (isPanning) {
            const dx = e.clientX - panStartX; const dy = e.clientY - panStartY;
            appData.screen_position.x = panStartScreenX - dx;
            appData.screen_position.y = panStartScreenY - dy;
            updateViewBox();
        }
    });

    borderedBox.addEventListener('mouseup', () => {
        if (draggedNode) {
            if (isSignificantDrag) {
                // 노드 이동 완료 시 Python으로 결과 좌표 송신
                Streamlit.setComponentValue({
                    action: 'node_move',
                    node_id: draggedNode.id,
                    x: draggedNode.position.x,
                    y: draggedNode.position.y
                });
            } else {
                openSidebar(draggedNode);
            }
            draggedNode = null;
        }
        if (isPanning) {
            isPanning = false;
            Streamlit.setComponentValue({
                action: 'pan',
                x: appData.screen_position.x,
                y: appData.screen_position.y
            });
        }
    });

    svg.addEventListener('click', (e) => { if (!e.target.closest('.node')) closeSidebar(); });

    function openSidebar(node) {
        document.getElementById('panel-title').textContent = node.name;
        document.getElementById('panel-year').textContent = node.year;
        document.getElementById('panel-desc').textContent = node.description;
        const sortedIds = [...node.nations].sort((a,b) => a-b);
        document.getElementById('panel-nations').textContent = sortedIds.map(id => nationMap[id].name).join(', ');

        const causesHTML = (node.causes && node.causes.length > 0)
            ? node.causes.map(id => { const n = appData.nodes.find(x => x.id === id); return `• <a href="#" class="event-link" onclick="openSidebarById('${n.id}'); return false;">${n.name}</a>`; }).join('<br>')
            : '<span style="color:#b2bec3;">없음 (시작 사건)</span>';
        document.getElementById('panel-causes').innerHTML = causesHTML;

        const resultsHTML = (node.results && node.results.length > 0)
            ? node.results.map(id => { const n = appData.nodes.find(x => x.id === id); return `• <a href="#" class="event-link" onclick="openSidebarById('${n.id}'); return false;">${n.name}</a>`; }).join('<br>')
            : '<span style="color:#b2bec3;">없음 (마지막 사건)</span>';
        document.getElementById('panel-results').innerHTML = resultsHTML;

        const stripe = document.getElementById('panel-stripe');
        if (sortedIds.length === 1) { stripe.style.background = nationMap[sortedIds[0]].color; }
        else {
            const step = 100 / sortedIds.length;
            const colorStops = sortedIds.map((id, idx) => `${nationMap[id].color} ${(idx * step).toFixed(2)}% ${((idx + 1) * step).toFixed(2)}%`);
            stripe.style.background = `linear-gradient(to bottom, ${colorStops.join(', ')})`;
        }

        sidePanel.classList.add('open');
        edgeElements.forEach(e => {
            if (e.target.id === node.id) { e.line.style.stroke = '#e74c3c'; e.line.setAttribute('marker-end', 'url(#arrow-cause)'); }
            else if (e.source.id === node.id) { e.line.style.stroke = '#0984e3'; e.line.setAttribute('marker-end', 'url(#arrow-result)'); }
            else { e.line.style.stroke = '#b2bec3'; e.line.setAttribute('marker-end', 'url(#arrow)'); }
        });
    }

    window.openSidebarById = function(nodeId) {
        const targetNode = appData.nodes.find(n => n.id === parseInt(nodeId));
        if (targetNode) openSidebar(targetNode);
    };

    function closeSidebar() {
        sidePanel.classList.remove('open');
        edgeElements.forEach(e => { e.line.style.stroke = '#b2bec3'; e.line.setAttribute('marker-end', 'url(#arrow)'); });
    }
    document.getElementById('close-btn').addEventListener('click', closeSidebar);
</script>
</body>
</html>
"""

with open(index_html_path, "w", encoding="utf-8") as f:
    f.write(html_content)

history_map_component = components.declare_component("history_map_component", path=COMPONENT_DIR)

active_ids = [k for k, v in st.session_state.active_nations.items() if v]

# JS 렌더러 호출 및 수신 데이터 획득
event = history_map_component(
    events_data=st.session_state.events_data,
    active_nations=active_ids,
    key="network_map"
)

# ==========================================
# 6. JavaScript 이벤트 ➔ Python 로직 실행 처리
# ==========================================
if event:
    action = event.get("action")
    if action == "node_move":
        node_id = event.get("node_id")
        for node in st.session_state.events_data["nodes"]:
            if node["id"] == node_id:
                node["position"]["x"] = event.get("x")
                node["position"]["y"] = event.get("y")
                break
        push_history()
        st.rerun()

    elif action == "pan":
        st.session_state.events_data["screen_position"]["x"] = event.get("x")
        st.session_state.events_data["screen_position"]["y"] = event.get("y")
        st.rerun()

    elif action == "undo":
        do_undo()
        st.rerun()

    elif action == "redo":
        do_redo()
        st.rerun()
