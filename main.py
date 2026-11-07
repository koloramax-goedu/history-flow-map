import streamlit as st
import streamlit.components.v1 as components
import json

# ==========================================
# 1. 스트림릿 페이지 설정 (기본 제목 및 설명 제거)
# ==========================================
st.set_page_config(page_title="역사적 사건 인과관계 지도", layout="wide")

# ==========================================
# 2. 역사 사건 데이터 정의 ('년' 제거, nations 추가)
# ==========================================
events_data = {
    "nodes": [
        {"id": "1", "title": "성왕의 한강 수복", "year": "551", "nations": "백제, 신라, 고구려", "desc": "백제 성왕이 신라 진흥왕과 연합하여 고구려를 공격, 한강 하류 유역을 수복한 사건입니다.", "x": 100, "y": 150, "color": "#f8b400"},
        {"id": "2", "title": "진흥왕의 한강 차지", "year": "553", "nations": "신라, 백제", "desc": "신라 진흥왕이 나제동맹을 깨고 기습적으로 백제를 공격하여 한강 유역을 독차지하고 신주를 설치했습니다.", "x": 300, "y": 150, "color": "#4a69bd"},
        {"id": "3", "title": "관산성 전투", "year": "554", "nations": "백제, 신라, 대가야", "desc": "신라의 배신에 분노한 백제 성왕이 대가야와 연합하여 신라를 공격했으나, 관산성에서 전사하고 대패한 전투입니다.", "x": 500, "y": 150, "color": "#e55039"},
        {"id": "4", "title": "살수대첩", "year": "612", "nations": "고구려, 수", "desc": "고구려의 을지문덕이 살수(청천강)에서 수나라의 30만 별동대를 크게 물리친 전투입니다.", "x": 100, "y": 350, "color": "#78e08f"},
        {"id": "5", "title": "안시성 전투", "year": "645", "nations": "고구려, 당", "desc": "고구려 안시성에서 당나라 태종의 대군을 맞아 약 88일간의 치열한 공방전 끝에 당군을 물리친 전투입니다.", "x": 300, "y": 350, "color": "#78e08f"},
        {"id": "6", "title": "나당 동맹 체결", "year": "648", "nations": "신라, 당", "desc": "백제의 잦은 공격으로 위기에 처한 신라(김춘추)가 당나라로 건너가 고구려와 백제를 멸망시키기 위한 군사 동맹을 맺은 사건입니다.", "x": 500, "y": 250, "color": "#4a69bd"},
        {"id": "7", "title": "황산벌 전투", "year": "660", "nations": "백제, 신라", "desc": "나당 연합군이 백제를 공격하자, 계백 장군이 이끄는 5천 결사대가 황산벌에서 김유신의 5만 신라군에 맞서 싸운 전투입니다.", "x": 700, "y": 150, "color": "#e55039"},
        {"id": "8", "title": "백제 멸망", "year": "660", "nations": "백제, 신라, 당", "desc": "황산벌 전투 패배 후 사비성이 나당 연합군에게 함락되며 의자왕이 항복, 백제가 멸망하게 됩니다.", "x": 900, "y": 150, "color": "#f8b400"},
        {"id": "9", "title": "고구려 멸망", "year": "668", "nations": "고구려, 신라, 당", "desc": "오랜 전쟁과 연개소문 사후의 내분으로 국력이 약해진 고구려가 나당 연합군의 공격을 받고 평양성이 함락되며 멸망했습니다.", "x": 900, "y": 350, "color": "#78e08f"},
        {"id": "10", "title": "기벌포 해전", "year": "676", "nations": "신라, 당", "desc": "신라가 한반도 전체를 지배하려는 당나라에 맞서 싸운 나당 전쟁의 마지막 전투. 기벌포에서 당의 수군을 궤멸시켜 삼국통일을 완수했습니다.", "x": 1100, "y": 250, "color": "#4a69bd"}
    ],
    "edges": [
        {"source": "1", "target": "2"},
        {"source": "2", "target": "3"},
        {"source": "3", "target": "6"},
        {"source": "4", "target": "5"},
        {"source": "5", "target": "6"},
        {"source": "6", "target": "7"},
        {"source": "7", "target": "8"},
        {"source": "6", "target": "9"},
        {"source": "8", "target": "9"},
        {"source": "8", "target": "10"},
        {"source": "9", "target": "10"}
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
            margin: 0;
            padding: 0;
            font-family: 'Malgun Gothic', sans-serif;
            overflow: hidden;
            background-color: #f7f9fc;
        }}
        #map-container {{
            position: relative;
            width: 100vw;
            height: 95vh;
            background-color: #ffffff;
            border: 1px solid #e2e8f0;
            border-radius: 8px;
            overflow: hidden;
        }}
        /* 지도 내 최상단 제목 CSS */
        #map-title {{
            position: absolute;
            top: 20px;
            left: 20px;
            z-index: 10;
            font-size: 26px;
            font-weight: 900;
            color: #2d3436;
            background: rgba(255, 255, 255, 0.85);
            padding: 10px 20px;
            border-radius: 8px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.05);
            pointer-events: none; /* 드래그 방해 안 함 */
        }}

        svg {{
            width: 100%;
            height: 100%;
            cursor: grab;
        }}
        svg:active {{
            cursor: grabbing;
        }}
        .node {{
            cursor: pointer;
        }}
        .node circle {{
            stroke: #fff;
            stroke-width: 3px;
            box-shadow: 2px 2px 5px rgba(0,0,0,0.3);
            transition: stroke-width 0.2s;
        }}
        .node:hover circle {{
            stroke-width: 5px;
            stroke: #333;
        }}
        .node text {{
            font-size: 14px;
            font-weight: bold;
            pointer-events: none;
            text-anchor: middle;
            fill: #2d3436;
        }}
        .node text.year {{
            font-size: 12px;
            font-weight: normal;
            fill: #636e72;
        }}
        .edge {{
            stroke: #b2bec3;
            stroke-width: 2.5px;
        }}
        
        /* 오른쪽 슬라이드 패널 CSS */
        #side-panel {{
            position: absolute;
            top: 0;
            right: -450px;
            width: 400px;
            height: 100%;
            background-color: #ffffff;
            box-shadow: -4px 0 15px rgba(0,0,0,0.1);
            transition: right 0.3s cubic-bezier(0.4, 0, 0.2, 1);
            padding: 30px 25px;
            box-sizing: border-box;
            z-index: 100;
            border-left: 5px solid #4a69bd;
            overflow-y: auto;
        }}
        #side-panel.open {{
            right: 0;
        }}
        #close-btn {{
            position: absolute;
            top: 15px;
            right: 15px;
            background: none;
            border: none;
            font-size: 24px;
            cursor: pointer;
            color: #636e72;
        }}
        h2 {{
            margin-top: 0;
            color: #2d3436;
            font-size: 22px;
            margin-bottom: 10px;
        }}
        .badge {{
            display: inline-block;
            background: #dfe6e9;
            color: #2d3436;
            padding: 4px 8px;
            border-radius: 4px;
            font-size: 14px;
            margin-bottom: 20px;
            font-weight: bold;
        }}
        p.desc {{
            line-height: 1.6;
            color: #4a4a4a;
            font-size: 15px;
            margin-bottom: 25px;
            background-color: #f8f9fa;
            padding: 15px;
            border-radius: 8px;
        }}
        
        /* 세부 정보 (관련 국가, 원인, 결과) CSS */
        .info-group {{
            margin-bottom: 15px;
            font-size: 14px;
        }}
        .info-label {{
            font-weight: bold;
            color: #0984e3;
            margin-bottom: 5px;
            display: flex;
            align-items: center;
        }}
        .info-value {{
            color: #2d3436;
            padding-left: 10px;
            line-height: 1.5;
        }}
    </style>
</head>
<body>

<div id="map-container">
    <!-- 지도 안으로 들어온 타이틀 -->
    <div id="map-title">역사적 사건 인과관계 지도</div>

    <svg id="network">
        <defs>
            <marker id="arrow" viewBox="0 -5 10 10" refX="28" refY="0" markerWidth="6" markerHeight="6" orient="auto">
                <path d="M0,-5L10,0L0,5" fill="#b2bec3"></path>
            </marker>
        </defs>
        <g id="edges-layer"></g>
        <g id="nodes-layer"></g>
    </svg>
    
    <div id="side-panel">
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

<script>
    const data = {json.dumps(events_data)};
    
    const svg = document.getElementById('network');
    const edgesLayer = document.getElementById('edges-layer');
    const nodesLayer = document.getElementById('nodes-layer');
    
    const sidePanel = document.getElementById('side-panel');
    const panelTitle = document.getElementById('panel-title');
    const panelYear = document.getElementById('panel-year');
    const panelDesc = document.getElementById('panel-desc');
    const panelNations = document.getElementById('panel-nations');
    const panelCauses = document.getElementById('panel-causes');
    const panelResults = document.getElementById('panel-results');
    const closeBtn = document.getElementById('close-btn');

    let draggedNode = null;
    let offsetX = 0;
    let offsetY = 0;

    const nodeElements = {{}};
    const edgeElements = [];

    // 간선(화살표) 그리기
    data.edges.forEach(edge => {{
        const sourceNode = data.nodes.find(n => n.id === edge.source);
        const targetNode = data.nodes.find(n => n.id === edge.target);
        
        if(sourceNode && targetNode) {{
            const line = document.createElementNS('http://www.w3.org/2000/svg', 'line');
            line.setAttribute('class', 'edge');
            line.setAttribute('marker-end', 'url(#arrow)');
            
            line.setAttribute('x1', sourceNode.x);
            line.setAttribute('y1', sourceNode.y);
            line.setAttribute('x2', targetNode.x);
            line.setAttribute('y2', targetNode.y);
            
            edgesLayer.appendChild(line);
            edgeElements.push({{ line, source: sourceNode, target: targetNode }});
        }}
    }});

    // 노드 그리기
    data.nodes.forEach(node => {{
        const g = document.createElementNS('http://www.w3.org/2000/svg', 'g');
        g.setAttribute('class', 'node');
        g.setAttribute('transform', `translate(${{node.x}}, ${{node.y}})`);
        
        const circle = document.createElementNS('http://www.w3.org/2000/svg', 'circle');
        circle.setAttribute('r', 20);
        circle.setAttribute('fill', node.color);
        
        const textTitle = document.createElementNS('http://www.w3.org/2000/svg', 'text');
        textTitle.setAttribute('y', 35);
        textTitle.textContent = node.title;

        // 연도 표기 ('년' 제외)
        const textYear = document.createElementNS('http://www.w3.org/2000/svg', 'text');
        textYear.setAttribute('class', 'year');
        textYear.setAttribute('y', 50);
        textYear.textContent = node.year;
        
        g.appendChild(circle);
        g.appendChild(textTitle);
        g.appendChild(textYear);
        nodesLayer.appendChild(g);
        
        nodeElements[node.id] = g;

        g.addEventListener('mousedown', (e) => {{
            draggedNode = node;
            offsetX = e.clientX - node.x;
            offsetY = e.clientY - node.y;
            e.stopPropagation();
        }});

        g.addEventListener('click', (e) => {{
            openSidebar(node);
            e.stopPropagation();
        }});
    }});

    function updateEdges() {{
        edgeElements.forEach(e => {{
            e.line.setAttribute('x1', e.source.x);
            e.line.setAttribute('y1', e.source.y);
            e.line.setAttribute('x2', e.target.x);
            e.line.setAttribute('y2', e.target.y);
        }});
    }}

    // 마우스 드래그 이벤트
    svg.addEventListener('mousemove', (e) => {{
        if (draggedNode) {{
            const newX = e.clientX - offsetX;
            const newY = e.clientY - offsetY;
            draggedNode.x = newX;
            draggedNode.y = newY;
            
            nodeElements[draggedNode.id].setAttribute('transform', `translate(${{newX}}, ${{newY}})`);
            updateEdges();
        }}
    }});

    svg.addEventListener('mouseup', () => draggedNode = null);
    svg.addEventListener('mouseleave', () => draggedNode = null);

    // 사이드바 로직
    function openSidebar(node) {{
        panelTitle.textContent = node.title;
        panelYear.textContent = node.year; // '년' 없는 순수 연도
        panelDesc.textContent = node.desc;
        panelNations.textContent = node.nations;

        // 원인 사건 추적 (해당 노드가 target인 edge들 검색)
        const causes = data.edges.filter(e => e.target === node.id);
        const causeTitles = causes.map(e => data.nodes.find(n => n.id === e.source).title);
        panelCauses.innerHTML = causeTitles.length > 0 
            ? causeTitles.map(t => `• ${{t}}`).join('<br>') 
            : '<span style="color:#b2bec3;">없음 (시작 사건)</span>';

        // 결과 사건 추적 (해당 노드가 source인 edge들 검색)
        const results = data.edges.filter(e => e.source === node.id);
        const resultTitles = results.map(e => data.nodes.find(n => n.id === e.target).title);
        panelResults.innerHTML = resultTitles.length > 0 
            ? resultTitles.map(t => `• ${{t}}`).join('<br>') 
            : '<span style="color:#b2bec3;">없음 (마지막 사건)</span>';

        sidePanel.style.borderLeftColor = node.color;
        sidePanel.classList.add('open');
    }}

    function closeSidebar() {{
        sidePanel.classList.remove('open');
    }}

    svg.addEventListener('click', closeSidebar);
    closeBtn.addEventListener('click', closeSidebar);

</script>
</body>
</html>
"""

# Streamlit 화면 여백 최소화 및 높이 최대로 할당
components.html(html_code, height=900, scrolling=False)
