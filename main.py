import streamlit as st
import streamlit.components.v1 as components
import json

# ==========================================
# 1. 스트림릿 페이지 설정
# ==========================================
st.set_page_config(page_title="역사적 사건 인과관계 지도", layout="wide")

# ==========================================
# 2. 역사 사건 데이터 정의
# ==========================================
events_data = {
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
        {
            "id": 1, "name": "성왕의 한강 수복", "position": {"x": 5100, "y": 5150}, "year": 551,
            "description": "백제 성왕이 신라 진흥왕과 연합하여 고구려를 공격, 한강 하류 유역을 수복한 사건입니다.",
            "causes": [], "results": [2], "nations": [1, 2, 3]
        },
        {
            "id": 2, "name": "진흥왕의 한강 차지", "position": {"x": 5300, "y": 5150}, "year": 553,
            "description": "신라 진흥왕이 나제동맹을 깨고 기습적으로 백제를 공격하여 한강 유역을 독차지하고 신주를 설치했습니다.",
            "causes": [1], "results": [3], "nations": [2, 3]
        },
        {
            "id": 3, "name": "관산성 전투", "position": {"x": 5500, "y": 5150}, "year": 554,
            "description": "신라의 배신에 분노한 백제 성왕이 대가야와 연합하여 신라를 공격했으나, 관산성에서 전사하고 대패한 전투입니다.",
            "causes": [2], "results": [6], "nations": [2, 3, 6]
        },
        {
            "id": 4, "name": "살수대첩", "position": {"x": 5100, "y": 5350}, "year": 612,
            "description": "고구려의 을지문덕이 살수(청천강)에서 수나라의 30만 별동대를 크게 물리친 전투입니다.",
            "causes": [], "results": [5], "nations": [1, 5]
        },
        {
            "id": 5, "name": "안시성 전투", "position": {"x": 5300, "y": 5350}, "year": 645,
            "description": "고구려 안시성에서 당나라 태종의 대군을 맞아 약 88일간의 치열한 공방전 끝에 당군을 물리친 전투입니다.",
            "causes": [4], "results": [6], "nations": [1, 4]
        },
        {
            "id": 6, "name": "나당 동맹 체결", "position": {"x": 5500, "y": 5250}, "year": 648,
            "description": "백제의 잦은 공격으로 위기에 처한 신라(김춘추)가 당나라로 건너가 고구려와 백제를 멸망시키기 위한 군사 동맹을 맺은 사건입니다.",
            "causes": [3, 5], "results": [7, 9], "nations": [3, 4]
        },
        {
            "id": 7, "name": "황산벌 전투", "position": {"x": 5700, "y": 5150}, "year": 660,
            "description": "나당 연합군이 백제를 공격하자, 계백 장군이 이끄는 5천 결사대가 황산벌에서 김유신의 5만 신라군에 맞서 싸운 전투입니다.",
            "causes": [6], "results": [8], "nations": [2, 3, 4]
        },
        {
            "id": 8, "name": "백제 멸망", "position": {"x": 5900, "y": 5150}, "year": 660,
            "description": "황산벌 전투 패배 후 사비성이 나당 연합군에게 함락되며 의자왕이 항복, 백제가 멸망하게 됩니다.",
            "causes": [7], "results": [9, 10], "nations": [2, 3, 4]
        },
        {
            "id": 9, "name": "고구려 멸망", "position": {"x": 5900, "y": 5350}, "year": 668,
            "description": "오랜 전쟁과 연개소문 사후의 내분으로 국력이 약해진 고구려가 나당 연합군의 공격을 받고 평양성이 함락되며 멸망했습니다.",
            "causes": [6, 8], "results": [10], "nations": [1, 3, 4]
        },
        {
            "id": 10, "name": "기벌포 해전", "position": {"x": 6100, "y": 5250}, "year": 676,
            "description": "신라가 한반도 전체를 지배하려는 당나라에 맞서 싸운 나당 전쟁의 마지막 전투. 기벌포에서 당의 수군을 궤멸시켜 삼국통일을 완수했습니다.",
            "causes": [8, 9], "results": [], "nations": [3, 4]
        }
    ]
}

# ==========================================
# 3. HTML/CSS/JS 통합 컴포넌트 코드
# ==========================================
html_code = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <style>
        body {{
            margin: 0; padding: 0;
            font-family: 'Malgun Gothic', sans-serif;
            overflow: hidden;
            background-color: #ffffff;
            height: 100vh;
        }}
        #map-container {{
            display: flex; flex-direction: column;
            width: 100vw; height: 100vh;
            background-color: #ffffff;
            padding: 15px; box-sizing: border-box;
            overflow: hidden;
        }}
        #bordered-box {{
            display: flex; flex-direction: column;
            width: 100%; height: 100%;
            border: 1px solid #000000;
            border-radius: 8px; overflow: hidden;
            position: relative; background-color: #ffffff;
            outline: none;
        }}

        #title-area {{
            flex: 0 0 55px; width: 100%;
            background-color: #ffffff;
            display: flex; justify-content: flex-start;
            align-items: center; gap: 20px;
            padding: 0 20px; box-sizing: border-box;
            z-index: 30;
        }}
        #main-title {{
            font-size: 24px; font-weight: 900;
            color: #2d3436; margin: 0; white-space: nowrap;
        }}
        #menu-bar {{
            background-color: #f1f2f6; border: 1px solid #dfe6e9;
            display: flex; align-items: center;
            padding: 0 10px; height: 38px;
            border-radius: 20px; width: max-content;
        }}
        .menu-item {{ position: relative; margin: 0 2px; }}
        .menu-title {{
            padding: 4px 10px; cursor: pointer;
            font-size: 14px; font-weight: bold;
            color: #2d3436; border-radius: 4px;
            user-select: none;
        }}
        .menu-title:hover {{ background-color: #dfe6e9; }}
        .menu-dropdown {{
            display: none; position: absolute;
            top: 100%; left: 0; margin-top: 6px;
            background-color: #ffffff; min-width: 160px;
            box-shadow: 0 4px 12px rgba(0,0,0,0.15);
            border: 1px solid #dfe6e9; border-radius: 6px;
            padding: 5px 0; z-index: 200;
        }}
        .menu-dropdown.show {{ display: block; }}
        
        .dropdown-item {{
            padding: 8px 15px; font-size: 13px;
            color: #2d3436; cursor: pointer; text-align: left;
            display: flex; justify-content: space-between; align-items: center; gap: 20px;
        }}
        .dropdown-item:hover:not(.disabled) {{ background-color: #f1f2f6; }}
        
        .dropdown-item.disabled {{ color: #b2bec3; cursor: default; }}
        .shortcut-text {{ font-size: 11px; color: #a4b0be; user-select: none; pointer-events: none; }}

        #divider {{ width: 100%; height: 2px; background-color: #e2e8f0; }}

        #network-container {{
            flex: 1; position: relative;
            overflow: hidden; background-color: #ffffff;
            box-sizing: border-box;
        }}
        
        svg {{ width: 100%; height: 100%; cursor: grab; }}
        svg:active {{ cursor: grabbing; }}
        
        #filter-container {{
            position: absolute; top: 15px; right: 15px;
            background-color: rgba(255, 255, 255, 0.95);
            border: 1px solid #000000; border-radius: 25px;
            padding: 8px 20px; display: flex;
            align-items: center; gap: 15px; z-index: 20;
            box-shadow: 0 2px 6px rgba(0,0,0,0.1);
        }}
        .filter-item {{
            display: flex; align-items: center; gap: 6px;
            cursor: pointer; font-size: 14px; font-weight: bold;
            color: #2d3436; transition: all 0.2s; user-select: none;
        }}
        .filter-item.inactive {{ opacity: 0.3; }}
        .color-circle {{ width: 14px; height: 14px; border-radius: 50%; }}
        
        .node {{ cursor: grab; transition: opacity 0.3s; }}
        .node:active {{ cursor: grabbing; }}
        .node.dimmed {{ opacity: 0.15; pointer-events: none; }}
        
        .node .node-border {{
            stroke: #fff; stroke-width: 3px; fill: none;
            transition: stroke-width 0.2s, stroke 0.2s;
        }}
        .node.hover-active .node-border {{ stroke-width: 5px; stroke: #333; }}
        
        .node text {{
            font-size: 14px; font-weight: bold;
            pointer-events: none; text-anchor: middle; fill: #2d3436;
        }}
        .node text.year {{ font-size: 12px; font-weight: normal; fill: #636e72; }}
        
        .edge {{
            stroke: #b2bec3; stroke-width: 2.5px;
            transition: opacity 0.3s, stroke 0.3s;
        }}
        .edge.dimmed {{ opacity: 0.15; }}
        
        #side-panel {{
            position: absolute; top: 0; right: -450px;
            width: 400px; height: 100%; background-color: #ffffff;
            box-shadow: -4px 0 15px rgba(0,0,0,0.1);
            transition: right 0.3s cubic-bezier(0.4, 0, 0.2, 1);
            padding: 30px 25px 30px 30px; box-sizing: border-box;
            z-index: 100; overflow-y: auto;
        }}
        #side-panel.open {{ right: 0; }}
        #panel-stripe {{ position: absolute; top: 0; left: 0; width: 6px; height: 100%; }}
        #close-btn {{
            position: absolute; top: 15px; right: 15px;
            background: none; border: none;
            font-size: 24px; cursor: pointer; color: #636e72;
        }}
        h2 {{ margin-top: 0; color: #2d3436; font-size: 22px; margin-bottom: 10px; }}
        .badge {{
            display: inline-block; background: #dfe6e9; color: #2d3436;
            padding: 4px 8px; border-radius: 4px;
            font-size: 14px; margin-bottom: 20px; font-weight: bold;
        }}
        p.desc {{
            line-height: 1.6; color: #4a4a4a; font-size: 15px;
            margin-bottom: 25px; background-color: #f8f9fa;
            padding: 15px; border-radius: 8px;
        }}
        .info-group {{ margin-bottom: 15px; font-size: 14px; }}
        .info-label {{ font-weight: bold; color: #2d3436; margin-bottom: 5px; display: flex; align-items: center; }}
        .info-value {{ color: #2d3436; padding-left: 10px; line-height: 1.5; }}
        .event-link {{
            color: #0984e3; text-decoration: none;
            cursor: pointer; font-weight: bold; transition: color 0.2s;
        }}
        .event-link:hover {{ color: #74b9ff; text-decoration: underline; }}
    </style>
</head>
<body>

<div id="map-container">
    <div id="bordered-box" tabindex="0">
        <div id="title-area">
            <h1 id="main-title">역사적 사건 인과관계 지도</h1>
            <div id="menu-bar">
                <div class="menu-item">
                    <div class="menu-title">파일</div>
                    <div class="menu-dropdown">
                        <div class="dropdown-item" id="menu-save"><span>저장하기</span><span class="shortcut-text">Ctrl+S</span></div>
                        <div class="dropdown-item" id="menu-load"><span>불러오기</span><span class="shortcut-text">Ctrl+L</span></div>
                    </div>
                </div>
                <div class="menu-item">
                    <div class="menu-title">명령</div>
                    <div class="menu-dropdown">
                        <div class="dropdown-item disabled" id="menu-undo"><span>실행 취소</span><span class="shortcut-text">Ctrl+Z</span></div>
                        <div class="dropdown-item disabled" id="menu-redo"><span>다시 실행</span><span class="shortcut-text">Ctrl+Y</span></div>
                    </div>
                </div>
                <div class="menu-item">
                    <div class="menu-title">화면</div>
                    <div class="menu-dropdown">
                        <div class="dropdown-item" id="menu-reset-screen"><span>화면 위치 초기화</span></div>
                        <div class="dropdown-item" id="menu-reset-nodes"><span>노드 위치 초기화</span></div>
                        <div class="dropdown-item" id="menu-reset-all"><span>화면 전체 초기화</span></div>
                    </div>
                </div>
            </div>
        </div>

        <div id="divider"></div>

        <div id="network-container">
            <div id="filter-container"></div>
            
            <svg id="network">
                <defs>
                    <marker id="arrow" viewBox="0 -5 10 10" refX="28" refY="0" markerWidth="6" markerHeight="6" orient="auto">
                        <path d="M0,-5L10,0L0,5" fill="#b2bec3"></path>
                    </marker>
                    <marker id="arrow-cause" viewBox="0 -5 10 10" refX="28" refY="0" markerWidth="6" markerHeight="6" orient="auto">
                        <path d="M0,-5L10,0L0,5" fill="#e74c3c"></path>
                    </marker>
                    <marker id="arrow-result" viewBox="0 -5 10 10" refX="28" refY="0" markerWidth="6" markerHeight="6" orient="auto">
                        <path d="M0,-5L10,0L0,5" fill="#0984e3"></path>
                    </marker>
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
                
                <div class="info-group">
                    <div class="info-label">🚩 관련 국가</div>
                    <div class="info-value" id="panel-nations"></div>
                </div>
                <div class="info-group">
                    <div class="info-label">🔻 원인 사건 (이전)</div>
                    <div class="info-value" id="panel-causes"></div>
                </div>
                <div class="info-group">
                    <div class="info-label">🔹 결과 사건 (이후)</div>
                    <div class="info-value" id="panel-results"></div>
                </div>
            </div>
        </div>
    </div>
</div>

<input type="file" id="file-input" accept=".json" style="display: none;">

<script>
    let appData = {json.dumps(events_data)};
    let initialData = JSON.parse(JSON.stringify(appData));
    let isDirty = false;
    
    let isMapFocused = false;
    const borderedBox = document.getElementById('bordered-box');

    // 노드 드래그 관련 변수
    let draggedNode = null;
    let offsetX = 0, offsetY = 0;
    let nodeMoved = false;
    let dragStartX = 0, dragStartY = 0;
    let origNodeX = 0, origNodeY = 0;
    let isSignificantDrag = false;
    const DRAG_THRESHOLD = 5;
    
    // 화면 드래그(패닝) 관련 변수
    let isPanning = false;
    let panStartX = 0, panStartY = 0;
    let panStartScreenX = 0, panStartScreenY = 0;

    borderedBox.addEventListener('mousedown', () => {{
        isMapFocused = true;
        window.focus();
    }});

    document.addEventListener('mousedown', (e) => {{
        if (!borderedBox.contains(e.target)) {{
            isMapFocused = false;
        }}
    }});

    // 창 전환(blur)이나 영역 이탈 시 드래그를 확정/종료하는 함수
    function handleDragInterrupt() {{
        if (draggedNode) {{
            if (isSignificantDrag) {{
                pushHistory();
                isDirty = true;
            }}
            draggedNode = null;
            nodeMoved = false;
            isSignificantDrag = false;
            checkNodeHover();
        }}
        if (isPanning) {{
            isPanning = false;
            isDirty = true;
            if (historyIndex >= 0) historyStack[historyIndex] = JSON.stringify(appData);
        }}
    }}

    window.addEventListener('blur', () => {{
        isMapFocused = false;
        handleDragInterrupt();
    }});
    
    borderedBox.addEventListener('mouseleave', handleDragInterrupt);

    // 글로벌 마우스 상태 추적
    let globalMouseX = -1;
    let globalMouseY = -1;
    let globalMouseDown = false;

    window.addEventListener('mousemove', (e) => {{
        globalMouseX = e.clientX;
        globalMouseY = e.clientY;
        globalMouseDown = (e.buttons > 0);
        checkNodeHover();
    }});

    window.addEventListener('mousedown', () => {{
        globalMouseDown = true;
        checkNodeHover();
    }});

    window.addEventListener('mouseup', () => {{
        globalMouseDown = false;
        if (isPanning) {{
            isPanning = false;
            isDirty = true;
            if (historyIndex >= 0) {{
                historyStack[historyIndex] = JSON.stringify(appData);
            }}
        }}
        checkNodeHover();
    }});

    window.addEventListener('focus', () => {{
        checkNodeHover();
    }});

    window.addEventListener('mouseout', (e) => {{
        if (e.relatedTarget === null) {{
            document.querySelectorAll('.node').forEach(n => {{
                if (draggedNode && nodeElements[draggedNode.id] === n) return;
                n.classList.remove('hover-active');
            }});
        }}
    }});

    function checkNodeHover() {{
        document.querySelectorAll('.node').forEach(n => {{
            if (draggedNode && nodeElements[draggedNode.id] === n) return;
            n.classList.remove('hover-active');
        }});
        
        if (globalMouseDown || globalMouseX < 0 || globalMouseY < 0) return;
        
        const el = document.elementFromPoint(globalMouseX, globalMouseY);
        if (el) {{
            const node = el.closest('.node');
            if (node && !node.classList.contains('dimmed')) {{
                node.classList.add('hover-active');
            }}
        }}
    }}

    let historyStack = [];
    let historyIndex = -1;

    function pushHistory() {{
        if (historyIndex < historyStack.length - 1) {{
            historyStack = historyStack.slice(0, historyIndex + 1);
        }}
        historyStack.push(JSON.stringify(appData));
        historyIndex++;
        updateUndoRedoMenu();
    }}

    function doUndo() {{
        if (historyIndex > 0) {{
            historyIndex--;
            appData = JSON.parse(historyStack[historyIndex]);
            initData();
            renderNetwork();
            updateViewBox();
            updateUndoRedoMenu();
        }}
    }}

    function doRedo() {{
        if (historyIndex < historyStack.length - 1) {{
            historyIndex++;
            appData = JSON.parse(historyStack[historyIndex]);
            initData();
            renderNetwork();
            updateViewBox();
            updateUndoRedoMenu();
        }}
    }}

    function updateUndoRedoMenu() {{
        const btnUndo = document.getElementById('menu-undo');
        const btnRedo = document.getElementById('menu-redo');
        
        if (historyIndex <= 0) btnUndo.classList.add('disabled');
        else btnUndo.classList.remove('disabled');

        if (historyIndex >= historyStack.length - 1) btnRedo.classList.add('disabled');
        else btnRedo.classList.remove('disabled');
    }}
    
    window.addEventListener('beforeunload', (e) => {{
        if (isDirty) {{
            e.preventDefault();
            e.returnValue = '';
        }}
    }});

    let saveCooldown = false;
    let zKeyActive = false;
    let yKeyActive = false;
    let zTimeout = null, zInterval = null;
    let yTimeout = null, yInterval = null;

    function executeSave() {{
        const dataStr = JSON.stringify(appData, null, 2);
        const blob = new Blob([dataStr], {{ type: "application/json" }});
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = "history_map.json";
        a.click();
        URL.revokeObjectURL(url);
        isDirty = false;
    }}

    window.addEventListener('keydown', (e) => {{
        if (e.ctrlKey || e.metaKey) {{
            const key = e.key ? e.key.toLowerCase() : '';
            const code = e.code;

            const isS = key === 's' || key === 'ㄴ' || code === 'KeyS';
            const isL = key === 'l' || key === 'ㅣ' || code === 'KeyL';
            const isZ = key === 'z' || key === 'ㅋ' || code === 'KeyZ';
            const isY = key === 'y' || key === 'ㅛ' || code === 'KeyY';

            if (isS || isL || isZ || isY) {{
                e.preventDefault();

                if (isS) {{
                    if (!saveCooldown) {{
                        executeSave();
                        saveCooldown = true;
                        setTimeout(() => {{ saveCooldown = false; }}, 2000);
                    }}
                }}
                else if (isL) {{
                    document.getElementById('file-input').click();
                }}
                else if (isZ) {{
                    if (!zKeyActive) {{
                        zKeyActive = true;
                        doUndo();
                        zTimeout = setTimeout(() => {{
                            zInterval = setInterval(doUndo, 100);
                        }}, 300);
                    }}
                }}
                else if (isY) {{
                    if (!yKeyActive) {{
                        yKeyActive = true;
                        doRedo();
                        yTimeout = setTimeout(() => {{
                            yInterval = setInterval(doRedo, 100);
                        }}, 300);
                    }}
                }}
            }}
        }}
    }});

    window.addEventListener('keyup', (e) => {{
        const key = e.key ? e.key.toLowerCase() : '';
        const code = e.code;
        if (key === 'z' || key === 'ㅋ' || code === 'KeyZ') {{
            zKeyActive = false;
            clearTimeout(zTimeout);
            clearInterval(zInterval);
        }}
        if (key === 'y' || key === 'ㅛ' || code === 'KeyY') {{
            yKeyActive = false;
            clearTimeout(yTimeout);
            clearInterval(yInterval);
        }}
    }});

    document.querySelectorAll('.menu-title').forEach(title => {{
        title.addEventListener('click', (e) => {{
            const parent = e.target.closest('.menu-item');
            const dropdown = parent.querySelector('.menu-dropdown');
            
            document.querySelectorAll('.menu-dropdown').forEach(dd => {{
                if (dd !== dropdown) dd.classList.remove('show');
            }});
            
            dropdown.classList.toggle('show');
            e.stopPropagation();
        }});
    }});
    document.addEventListener('click', () => {{
        document.querySelectorAll('.menu-dropdown').forEach(dd => dd.classList.remove('show'));
    }});

    document.getElementById('menu-save').addEventListener('click', executeSave);
    document.getElementById('menu-load').addEventListener('click', () => document.getElementById('file-input').click());
    
    document.getElementById('menu-undo').addEventListener('click', (e) => {{
        if(!e.currentTarget.classList.contains('disabled')) doUndo();
    }});
    document.getElementById('menu-redo').addEventListener('click', (e) => {{
        if(!e.currentTarget.classList.contains('disabled')) doRedo();
    }});

    // 화면 및 노드 초기화 관련 이벤트
    document.getElementById('menu-reset-screen').addEventListener('click', () => {{
        if (appData.screen_position.x !== initialData.screen_position.x || 
            appData.screen_position.y !== initialData.screen_position.y) {{
            appData.screen_position.x = initialData.screen_position.x;
            appData.screen_position.y = initialData.screen_position.y;
            updateViewBox();
            isDirty = true;
            pushHistory();
        }}
    }});

    document.getElementById('menu-reset-nodes').addEventListener('click', () => {{
        let changed = false;
        appData.nodes.forEach(node => {{
            const initNode = initialData.nodes.find(n => n.id === node.id);
            if (initNode && (node.position.x !== initNode.position.x || node.position.y !== initNode.position.y)) {{
                node.position.x = initNode.position.x;
                node.position.y = initNode.position.y;
                changed = true;
            }}
        }});
        if (changed) {{
            renderNetwork();
            isDirty = true;
            pushHistory();
        }}
    }});

    document.getElementById('menu-reset-all').addEventListener('click', () => {{
        let changed = false;
        if (appData.screen_position.x !== initialData.screen_position.x || 
            appData.screen_position.y !== initialData.screen_position.y) {{
            appData.screen_position.x = initialData.screen_position.x;
            appData.screen_position.y = initialData.screen_position.y;
            changed = true;
        }}
        appData.nodes.forEach(node => {{
            const initNode = initialData.nodes.find(n => n.id === node.id);
            if (initNode && (node.position.x !== initNode.position.x || node.position.y !== initNode.position.y)) {{
                node.position.x = initNode.position.x;
                node.position.y = initNode.position.y;
                changed = true;
            }}
        }});
        if (changed) {{
            updateViewBox();
            renderNetwork();
            isDirty = true;
            pushHistory();
        }}
    }});

    document.getElementById('file-input').addEventListener('change', (e) => {{
        const file = e.target.files[0];
        if (!file) return;
        const reader = new FileReader();
        reader.onload = (ev) => {{
            try {{
                appData = JSON.parse(ev.target.result);
                initialData = JSON.parse(JSON.stringify(appData));
                isDirty = false;
                
                historyStack = [];
                historyIndex = -1;
                pushHistory();
                
                initData();
                renderNetwork();
                updateViewBox();
            }} catch(err) {{
                alert('파일을 불러오는데 실패했습니다. 올바른 JSON 파일인지 확인하세요.');
            }}
        }};
        reader.readAsText(file);
        e.target.value = ""; 
    }});

    let nationMap = {{}};
    let activeNations = new Set();
    let edgeElements = [];
    let nodeElements = {{}};
    let parsedEdges = [];

    const svg = document.getElementById('network');
    const edgesLayer = document.getElementById('edges-layer');
    const nodesLayer = document.getElementById('nodes-layer');
    const filterContainer = document.getElementById('filter-container');
    const sidePanel = document.getElementById('side-panel');

    function initData() {{
        nationMap = {{}};
        activeNations = new Set();
        appData.nations.forEach(n => {{
            nationMap[n.id] = n;
            activeNations.add(n.id);
        }});
        
        parsedEdges = [];
        appData.nodes.forEach(node => {{
            (node.results || []).forEach(targetId => {{
                parsedEdges.push({{ source: node.id, target: targetId }});
            }});
        }});
    }}

    function updateViewBox() {{
        const rect = svg.parentElement.getBoundingClientRect();
        if (rect.width === 0 || rect.height === 0) return;
        
        let currentX = appData.screen_position.x;
        let currentY = appData.screen_position.y;
        
        const maxX = appData.map_size.x - rect.width;
        const maxY = appData.map_size.y - rect.height;
        
        currentX = Math.max(0, Math.min(currentX, maxX));
        currentY = Math.max(0, Math.min(currentY, maxY));
        
        appData.screen_position.x = currentX;
        appData.screen_position.y = currentY;
        
        svg.setAttribute('viewBox', `${{appData.screen_position.x}} ${{appData.screen_position.y}} ${{rect.width}} ${{rect.height}}`);
    }}
    window.addEventListener('resize', updateViewBox);

    function createPieSlices(g, nationIds, radius) {{
        const sortedIds = [...nationIds].sort((a, b) => a - b);
        const count = sortedIds.length;

        if (count === 1) {{
            const circle = document.createElementNS('http://www.w3.org/2000/svg', 'circle');
            circle.setAttribute('r', radius);
            circle.setAttribute('fill', nationMap[sortedIds[0]] ? nationMap[sortedIds[0]].color : '#95a5a6');
            g.appendChild(circle);
        }} else {{
            let startAngle = -Math.PI / 2;
            const angleStep = (2 * Math.PI) / count;
            for (let i = 0; i < count; i++) {{
                const endAngle = startAngle + angleStep;
                const x1 = radius * Math.cos(startAngle);
                const y1 = radius * Math.sin(startAngle);
                const x2 = radius * Math.cos(endAngle);
                const y2 = radius * Math.sin(endAngle);

                const largeArcFlag = angleStep > Math.PI ? 1 : 0;
                const pathData = `M 0 0 L ${{x1}} ${{y1}} A ${{radius}} ${{radius}} 0 ${{largeArcFlag}} 1 ${{x2}} ${{y2}} Z`;
                
                const path = document.createElementNS('http://www.w3.org/2000/svg', 'path');
                path.setAttribute('d', pathData);
                path.setAttribute('fill', nationMap[sortedIds[i]] ? nationMap[sortedIds[i]].color : '#95a5a6');
                
                g.appendChild(path);
                startAngle = endAngle;
            }}
        }}

        const borderCircle = document.createElementNS('http://www.w3.org/2000/svg', 'circle');
        borderCircle.setAttribute('r', radius);
        borderCircle.setAttribute('class', 'node-border');
        g.appendChild(borderCircle);
    }}

    function renderNetwork() {{
        filterContainer.innerHTML = '';
        edgesLayer.innerHTML = '';
        nodesLayer.innerHTML = '';
        edgeElements = [];
        nodeElements = {{}};
        
        appData.nations.forEach(nItem => {{
            const item = document.createElement('div');
            item.className = 'filter-item active';
            item.innerHTML = `
                <div class="color-circle" style="background-color: ${{nItem.color}};"></div>
                <span>${{nItem.name}}</span>
            `;
            item.addEventListener('click', () => {{
                if (activeNations.has(nItem.id)) {{
                    activeNations.delete(nItem.id);
                    item.classList.add('inactive');
                }} else {{
                    activeNations.add(nItem.id);
                    item.classList.remove('inactive');
                }}
                updateFilters();
            }});
            filterContainer.appendChild(item);
        }});

        parsedEdges.forEach(edge => {{
            const sourceNode = appData.nodes.find(n => n.id === edge.source);
            const targetNode = appData.nodes.find(n => n.id === edge.target);
            if(sourceNode && targetNode) {{
                const line = document.createElementNS('http://www.w3.org/2000/svg', 'line');
                line.setAttribute('class', 'edge');
                line.setAttribute('marker-end', 'url(#arrow)');
                line.setAttribute('x1', sourceNode.position.x);
                line.setAttribute('y1', sourceNode.position.y);
                line.setAttribute('x2', targetNode.position.x);
                line.setAttribute('y2', targetNode.position.y);
                edgesLayer.appendChild(line);
                edgeElements.push({{ line, source: sourceNode, target: targetNode }});
            }}
        }});

        appData.nodes.forEach(node => {{
            const g = document.createElementNS('http://www.w3.org/2000/svg', 'g');
            g.setAttribute('class', 'node');
            g.setAttribute('transform', `translate(${{node.position.x}}, ${{node.position.y}})`);
            
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
        }});
        updateFilters();
    }}

    function updateFilters() {{
        appData.nodes.forEach(node => {{
            const isActive = node.nations.some(id => activeNations.has(id));
            const g = nodeElements[node.id];
            if (isActive) {{
                g.classList.remove('dimmed');
            }} else {{
                g.classList.add('dimmed');
                if (sidePanel.classList.contains('open') && document.getElementById('panel-title').textContent === node.name) {{
                    closeSidebar();
                }}
            }}
        }});
        
        edgeElements.forEach(e => {{
            const sourceDimmed = nodeElements[e.source.id].classList.contains('dimmed');
            const targetDimmed = nodeElements[e.target.id].classList.contains('dimmed');
            if (!sourceDimmed && !targetDimmed) e.line.classList.remove('dimmed');
            else e.line.classList.add('dimmed');
        }});
    }}

    function getSVGPoint(evt) {{
        const pt = svg.createSVGPoint();
        pt.x = evt.clientX;
        pt.y = evt.clientY;
        return pt.matrixTransform(svg.getScreenCTM().inverse());
    }}
    
    // 배경(화면) 드래그 시작
    svg.addEventListener('mousedown', (e) => {{
        if (e.button !== 0) return;
        if (!e.target.closest('.node')) {{
            isPanning = true;
            panStartX = e.clientX;
            panStartY = e.clientY;
            panStartScreenX = appData.screen_position.x;
            panStartScreenY = appData.screen_position.y;
            e.preventDefault();
        }}
    }});

    function startDrag(e, node) {{
        e.preventDefault();
        const pt = getSVGPoint(e);
        draggedNode = node;
        nodeMoved = false;
        isSignificantDrag = false;
        
        dragStartX = pt.x;
        dragStartY = pt.y;
        origNodeX = node.position.x;
        origNodeY = node.position.y;
        offsetX = pt.x - node.position.x;
        offsetY = pt.y - node.position.y;
        
        nodeElements[node.id].classList.add('hover-active');
        isMapFocused = true;
        window.focus();
        e.stopPropagation();
    }}

    // 마우스 이동 처리 (노드 드래그 및 화면 패닝)
    borderedBox.addEventListener('mousemove', (e) => {{
        if (e.buttons === 0 || !isMapFocused) {{
            if (draggedNode || isPanning) {{
                handleDragInterrupt();
            }}
            return;
        }}

        if (draggedNode) {{
            const pt = getSVGPoint(e);
            
            const dx = pt.x - dragStartX;
            const dy = pt.y - dragStartY;
            
            if (!isSignificantDrag) {{
                if (Math.sqrt(dx * dx + dy * dy) > DRAG_THRESHOLD) {{
                    isSignificantDrag = true;
                    isDirty = true;
                }} else {{
                    return; 
                }}
            }}
            
            nodeMoved = true;
            
            let newX = pt.x - offsetX;
            let newY = pt.y - offsetY;
            
            const limit = 50;
            newX = Math.max(limit, Math.min(newX, appData.map_size.x - limit));
            newY = Math.max(limit, Math.min(newY, appData.map_size.y - limit));
            
            draggedNode.position.x = newX;
            draggedNode.position.y = newY;
            nodeElements[draggedNode.id].setAttribute('transform', `translate(${{draggedNode.position.x}}, ${{draggedNode.position.y}})`);
            
            edgeElements.forEach(edge => {{
                if (edge.source.id === draggedNode.id || edge.target.id === draggedNode.id) {{
                    edge.line.setAttribute('x1', edge.source.position.x);
                    edge.line.setAttribute('y1', edge.source.position.y);
                    edge.line.setAttribute('x2', edge.target.position.x);
                    edge.line.setAttribute('y2', edge.target.position.y);
                }}
            }});
        }} else if (isPanning) {{
            const dx = e.clientX - panStartX;
            const dy = e.clientY - panStartY;
            
            let newX = panStartScreenX - dx;
            let newY = panStartScreenY - dy;
            
            appData.screen_position.x = newX;
            appData.screen_position.y = newY;
            updateViewBox();
        }}
    }});

    function endDrag() {{
        if (draggedNode) {{
            if (isSignificantDrag) {{
                pushHistory();
            }} else {{
                openSidebar(draggedNode);
            }}
            
            draggedNode = null;
            nodeMoved = false;
            isSignificantDrag = false;
            
            checkNodeHover();
        }}
    }}

    borderedBox.addEventListener('mouseup', endDrag);
    
    svg.addEventListener('click', (e) => {{
        if (!e.target.closest('.node')) {{
            closeSidebar();
        }}
    }});

    window.openSidebarById = function(nodeId) {{
        const targetNode = appData.nodes.find(n => n.id === parseInt(nodeId));
        if (targetNode) openSidebar(targetNode);
    }};

    function openSidebar(node) {{
        document.getElementById('panel-title').textContent = node.name;
        document.getElementById('panel-year').textContent = node.year; 
        document.getElementById('panel-desc').textContent = node.description;
        
        const sortedIds = [...node.nations].sort((a,b) => a-b);
        document.getElementById('panel-nations').textContent = sortedIds.map(id => nationMap[id].name).join(', ');

        const causesHTML = (node.causes && node.causes.length > 0) 
            ? node.causes.map(id => {{
                const n = appData.nodes.find(x => x.id === id);
                return `• <a href="#" class="event-link" onclick="openSidebarById('${{n.id}}'); return false;">${{n.name}}</a>`;
              }}).join('<br>') 
            : '<span style="color:#b2bec3;">없음 (시작 사건)</span>';
        document.getElementById('panel-causes').innerHTML = causesHTML;

        const resultsHTML = (node.results && node.results.length > 0) 
            ? node.results.map(id => {{
                const n = appData.nodes.find(x => x.id === id);
                return `• <a href="#" class="event-link" onclick="openSidebarById('${{n.id}}'); return false;">${{n.name}}</a>`;
              }}).join('<br>') 
            : '<span style="color:#b2bec3;">없음 (마지막 사건)</span>';
        document.getElementById('panel-results').innerHTML = resultsHTML;

        const stripe = document.getElementById('panel-stripe');
        if (sortedIds.length === 1) {{
            stripe.style.background = nationMap[sortedIds[0]].color;
        }} else {{
            const step = 100 / sortedIds.length;
            const colorStops = sortedIds.map((id, idx) => {{
                return `${{nationMap[id].color}} ${{(idx * step).toFixed(2)}}% ${{((idx + 1) * step).toFixed(2)}}%`;
            }});
            stripe.style.background = `linear-gradient(to bottom, ${{colorStops.join(', ')}})`;
        }}

        sidePanel.classList.add('open');

        edgeElements.forEach(e => {{
            if (e.target.id === node.id) {{
                e.line.style.stroke = '#e74c3c';
                e.line.setAttribute('marker-end', 'url(#arrow-cause)');
            }} else if (e.source.id === node.id) {{
                e.line.style.stroke = '#0984e3';
                e.line.setAttribute('marker-end', 'url(#arrow-result)');
            }} else {{
                e.line.style.stroke = '#b2bec3';
                e.line.setAttribute('marker-end', 'url(#arrow)');
            }}
        }});
    }}

    function closeSidebar() {{
        sidePanel.classList.remove('open');
        edgeElements.forEach(e => {{
            e.line.style.stroke = '#b2bec3';
            e.line.setAttribute('marker-end', 'url(#arrow)');
        }});
    }}
    document.getElementById('close-btn').addEventListener('click', closeSidebar);

    initData();
    pushHistory();
    renderNetwork();
    updateViewBox();

</script>
</body>
</html>
"""

components.html(html_code, height=900, scrolling=False)
