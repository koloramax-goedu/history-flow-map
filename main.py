import streamlit as st
import streamlit.components.v1 as components
import json

# ==========================================
# 1. 스트림릿 페이지 설정
# ==========================================
st.set_page_config(page_title="6~7세기 한국사 인과관계 지도", layout="wide")
st.title("📜 6~7세기 한국사 주요 사건 인과관계 지도")
st.markdown("노드를 **드래그**하여 자유롭게 배치할 수 있으며, 노드를 **클릭**하면 우측에 세부 정보가 나타납니다. 빈 공간을 클릭하면 정보 창이 닫힙니다. (물리 효과 제거)")

# ==========================================
# 2. 역사 사건 데이터 정의 (네이버 지식백과 기반)
# ==========================================
events_data = {
    "nodes": [
        {"id": "1", "title": "성왕의 한강 수복", "year": "551년", "desc": "백제 성왕이 신라 진흥왕과 연합하여 고구려를 공격, 한강 하류 유역을 수복한 사건입니다.", "x": 100, "y": 150, "color": "#f8b400"},
        {"id": "2", "title": "진흥왕의 한강 차지", "year": "553년", "desc": "신라 진흥왕이 나제동맹을 깨고 기습적으로 백제를 공격하여 한강 유역을 독차지하고 신주를 설치했습니다.", "x": 300, "y": 150, "color": "#4a69bd"},
        {"id": "3", "title": "관산성 전투", "year": "554년", "desc": "신라의 배신에 분노한 백제 성왕이 대가야와 연합하여 신라를 공격했으나, 관산성에서 전사하고 대패한 전투입니다.", "x": 500, "y": 150, "color": "#e55039"},
        {"id": "4", "title": "살수대첩", "year": "612년", "desc": "고구려의 을지문덕이 살수(청천강)에서 수나라의 30만 별동대를 크게 물리친 전투입니다.", "x": 100, "y": 350, "color": "#78e08f"},
        {"id": "5", "title": "안시성 전투", "year": "645년", "desc": "고구려 안시성에서 당나라 태종의 대군을 맞아 약 88일간의 치열한 공방전 끝에 당군을 물리친 전투입니다.", "x": 300, "y": 350, "color": "#78e08f"},
        {"id": "6", "title": "나당 동맹 체결", "year": "648년", "desc": "백제의 잦은 공격으로 위기에 처한 신라(김춘추)가 당나라로 건너가 고구려와 백제를 멸망시키기 위한 군사 동맹을 맺은 사건입니다.", "x": 500, "y": 250, "color": "#4a69bd"},
        {"id": "7", "title": "황산벌 전투", "year": "660년", "desc": "나당 연합군이 백제를 공격하자, 계백 장군이 이끄는 5천 결사대가 황산벌에서 김유신의 5만 신라군에 맞서 싸운 전투입니다.", "x": 700, "y": 150, "color": "#e55039"},
        {"id": "8", "title": "백제 멸망", "year": "660년", "desc": "황산벌 전투 패배 후 사비성이 나당 연합군에게 함락되며 의자왕이 항복, 백제가 멸망하게 됩니다.", "x": 900, "y": 150, "color": "#f8b400"},
        {"id": "9", "title": "고구려 멸망", "year": "668년", "desc": "오랜 전쟁과 연개소문 사후의 내분으로 국력이 약해진 고구려가 나당 연합군의 공격을 받고 평양성이 함락되며 멸망했습니다.", "x": 900, "y": 350, "color": "#78e08f"},
        {"id": "10", "title": "기벌포 해전", "year": "676년", "desc": "신라가 한반도 전체를 지배하려는 당나라에 맞서 싸운 나당 전쟁의 마지막 전투. 기벌포에서 당의 수군을 궤멸시켜 삼국통일을 완수했습니다.", "x": 1100, "y": 250, "color": "#4a69bd"}
    ],
    "edges": [
        {"source": "1", "target": "2"}, # 한강 수복 -> 신라의 배신
        {"source": "2", "target": "3"}, # 한강 차지 -> 관산성 전투 복수전
        {"source": "3", "target": "6"}, # 관산성 이후 백제의 압박 -> 나당동맹
        {"source": "4", "target": "5"}, # 수나라 격퇴 -> 당나라 침략 방어 (고구려 방어선)
        {"source": "5", "target": "6"}, # 고구려의 견고함 -> 당나라가 신라와 연합
        {"source": "6", "target": "7"}, # 나당동맹 -> 백제 공격(황산벌)
        {"source": "7", "target": "8"}, # 황산벌 패배 -> 백제 멸망
        {"source": "6", "target": "9"}, # 나당동맹 -> 고구려 공격
        {"source": "8", "target": "9"}, # 백제 멸망으로 고구려 고립 -> 고구려 멸망
        {"source": "8", "target": "10"}, # 한반도 장악 야욕 -> 나당전쟁
        {"source": "9", "target": "10"}  # 고구려 멸망 후 당나라 야욕 -> 기벌포에서 최종 격퇴
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
            height: 80vh;
            background-color: #ffffff;
            border: 1px solid #e2e8f0;
            border-radius: 8px;
            overflow: hidden;
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
            font-size: 11px;
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
            right: -400px;
            width: 350px;
            height: 100%;
            background-color: #ffffff;
            box-shadow: -4px 0 15px rgba(0,0,0,0.1);
            transition: right 0.3s cubic-bezier(0.4, 0, 0.2, 1);
            padding: 30px 20px;
            box-sizing: border-box;
            z-index: 100;
            border-left: 4px solid #4a69bd;
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
            font-size: 20px;
            cursor: pointer;
            color: #636e72;
        }}
        h2 {{
            margin-top: 0;
            color: #2d3436;
            font-size: 22px;
        }}
        .badge {{
            display: inline-block;
            background: #dfe6e9;
            color: #2d3436;
            padding: 4px 8px;
            border-radius: 4px;
            font-size: 12px;
            margin-bottom: 15px;
            font-weight: bold;
        }}
        p.desc {{
            line-height: 1.6;
            color: #4a4a4a;
            font-size: 15px;
        }}
    </style>
</head>
<body>

<div id="map-container">
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
    </div>
</div>

<script>
    // Python에서 주입된 데이터
    const data = {json.dumps(events_data)};
    
    const svg = document.getElementById('network');
    const edgesLayer = document.getElementById('edges-layer');
    const nodesLayer = document.getElementById('nodes-layer');
    
    const sidePanel = document.getElementById('side-panel');
    const panelTitle = document.getElementById('panel-title');
    const panelYear = document.getElementById('panel-year');
    const panelDesc = document.getElementById('panel-desc');
    const closeBtn = document.getElementById('close-btn');

    let draggedNode = null;
    let offsetX = 0;
    let offsetY = 0;

    // DOM 요소 매핑용 딕셔너리
    const nodeElements = {{}};
    const edgeElements = [];

    // 1. 간선(화살표) 그리기
    data.edges.forEach(edge => {{
        const sourceNode = data.nodes.find(n => n.id === edge.source);
        const targetNode = data.nodes.find(n => n.id === edge.target);
        
        if(sourceNode && targetNode) {{
            const line = document.createElementNS('http://www.w3.org/2000/svg', 'line');
            line.setAttribute('class', 'edge');
            line.setAttribute('marker-end', 'url(#arrow)');
            
            // 좌표 초기화
            line.setAttribute('x1', sourceNode.x);
            line.setAttribute('y1', sourceNode.y);
            line.setAttribute('x2', targetNode.x);
            line.setAttribute('y2', targetNode.y);
            
            edgesLayer.appendChild(line);
            edgeElements.push({{ line, source: sourceNode, target: targetNode }});
        }}
    }});

    // 2. 노드 그리기
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

        const textYear = document.createElementNS('http://www.w3.org/2000/svg', 'text');
        textYear.setAttribute('class', 'year');
        textYear.setAttribute('y', 50);
        textYear.textContent = node.year;
        
        g.appendChild(circle);
        g.appendChild(textTitle);
        g.appendChild(textYear);
        nodesLayer.appendChild(g);
        
        nodeElements[node.id] = g;

        // 노드 이벤트 처리
        g.addEventListener('mousedown', (e) => {{
            draggedNode = node;
            offsetX = e.clientX - node.x;
            offsetY = e.clientY - node.y;
            e.stopPropagation(); // 배경 클릭 방지
        }});

        g.addEventListener('click', (e) => {{
            openSidebar(node);
            e.stopPropagation();
        }});
    }});

    // 3. 선 업데이트 함수
    function updateEdges() {{
        edgeElements.forEach(e => {{
            e.line.setAttribute('x1', e.source.x);
            e.line.setAttribute('y1', e.source.y);
            e.line.setAttribute('x2', e.target.x);
            e.line.setAttribute('y2', e.target.y);
        }});
    }}

    // 4. 드래그 로직 (물리엔진 없이 순수 마우스 이동만 반영)
    svg.addEventListener('mousemove', (e) => {{
        if (draggedNode) {{
            const newX = e.clientX - offsetX;
            const newY = e.clientY - offsetY;
            
            draggedNode.x = newX;
            draggedNode.y = newY;
            
            // 그룹 이동
            nodeElements[draggedNode.id].setAttribute('transform', `translate(${{newX}}, ${{newY}})`);
            
            // 연결된 선 업데이트
            updateEdges();
        }}
    }});

    svg.addEventListener('mouseup', () => {{
        draggedNode = null;
    }});

    svg.addEventListener('mouseleave', () => {{
        draggedNode = null;
    }});

    // 5. 사이드바(세부정보 탭) 로직
    function openSidebar(node) {{
        panelTitle.textContent = node.title;
        panelYear.textContent = node.year;
        panelDesc.textContent = node.desc;
        sidePanel.style.borderLeftColor = node.color;
        sidePanel.classList.add('open');
    }}

    function closeSidebar() {{
        sidePanel.classList.remove('open');
    }}

    // 배경(SVG 빈 공간) 클릭 시 탭 닫기
    svg.addEventListener('click', () => {{
        closeSidebar();
    }});
    
    // 닫기 버튼 클릭
    closeBtn.addEventListener('click', () => {{
        closeSidebar();
    }});

</script>
</body>
</html>
"""

# Streamlit Components를 사용하여 HTML 렌더링 (높이 지정)
components.html(html_code, height=850, scrolling=False)
