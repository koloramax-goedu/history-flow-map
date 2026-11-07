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
    "nodes": [
        {"id": "1", "title": "성왕의 한강 수복", "year": "551", "nations": "백제, 신라, 고구려", "desc": "백제 성왕이 신라 진흥왕과 연합하여 고구려를 공격, 한강 하류 유역을 수복한 사건입니다.", "x": 100, "y": 150},
        {"id": "2", "title": "진흥왕의 한강 차지", "year": "553", "nations": "신라, 백제", "desc": "신라 진흥왕이 나제동맹을 깨고 기습적으로 백제를 공격하여 한강 유역을 독차지하고 신주를 설치했습니다.", "x": 300, "y": 150},
        {"id": "3", "title": "관산성 전투", "year": "554", "nations": "백제, 신라, 대가야", "desc": "신라의 배신에 분노한 백제 성왕이 대가야와 연합하여 신라를 공격했으나, 관산성에서 전사하고 대패한 전투입니다.", "x": 500, "y": 150},
        {"id": "4", "title": "살수대첩", "year": "612", "nations": "고구려, 수", "desc": "고구려의 을지문덕이 살수(청천강)에서 수나라의 30만 별동대를 크게 물리친 전투입니다.", "x": 100, "y": 350},
        {"id": "5", "title": "안시성 전투", "year": "645", "nations": "고구려, 당", "desc": "고구려 안시성에서 당나라 태종의 대군을 맞아 약 88일간의 치열한 공방전 끝에 당군을 물리친 전투입니다.", "x": 300, "y": 350},
        {"id": "6", "title": "나당 동맹 체결", "year": "648", "nations": "신라, 당", "desc": "백제의 잦은 공격으로 위기에 처한 신라(김춘추)가 당나라로 건너가 고구려와 백제를 멸망시키기 위한 군사 동맹을 맺은 사건입니다.", "x": 500, "y": 250},
        {"id": "7", "title": "황산벌 전투", "year": "660", "nations": "백제, 신라", "desc": "나당 연합군이 백제를 공격하자, 계백 장군이 이끄는 5천 결사대가 황산벌에서 김유신의 5만 신라군에 맞서 싸운 전투입니다.", "x": 700, "y": 150},
        {"id": "8", "title": "백제 멸망", "year": "660", "nations": "백제, 신라, 당", "desc": "황산벌 전투 패배 후 사비성이 나당 연합군에게 함락되며 의자왕이 항복, 백제가 멸망하게 됩니다.", "x": 900, "y": 150},
        {"id": "9", "title": "고구려 멸망", "year": "668", "nations": "고구려, 신라, 당", "desc": "오랜 전쟁과 연개소문 사후의 내분으로 국력이 약해진 고구려가 나당 연합군의 공격을 받고 평양성이 함락되며 멸망했습니다.", "x": 900, "y": 350},
        {"id": "10", "title": "기벌포 해전", "year": "676", "nations": "신라, 당", "desc": "신라가 한반도 전체를 지배하려는 당나라에 맞서 싸운 나당 전쟁의 마지막 전투. 기벌포에서 당의 수군을 궤멸시켜 삼국통일을 완수했습니다.", "x": 1100, "y": 250}
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
            background-color: #ffffff;
            height: 100vh;
        }}
        #map-container {{
            display: flex;
            flex-direction: column;
            width: 100vw;
            height: 100vh;
            background-color: #ffffff;
            padding: 15px;
            box-sizing: border-box;
            overflow: hidden;
        }}
        
        /* 전체 영역 감싸는 검은색 테두리 상자 */
        #bordered-box {{
            display: flex;
            flex-direction: column;
            width: 100%;
            height: 100%;
            border: 1px solid #000000;
            border-radius: 8px;
            overflow: hidden;
            position: relative;
            background-color: #ffffff;
        }}
        
        /* 1. 제목 및 우측 메뉴 영역 CSS */
        #title-area {{
            flex: 0 0 55px;
            width: 100%;
            background-color: #ffffff;
            display: flex;
            justify-content: space-between; /* 좌측 제목, 우측 메뉴 */
            align-items: center;
            padding: 0 20px;
            box-sizing: border-box;
            z-index: 30;
        }}
        #main-title {{
            font-size: 24px;
            font-weight: 900;
            color: #2d3436;
            margin: 0;
        }}

        /* 캡슐형 메뉴 바 (우측 정렬 배치) */
        #menu-bar {{
            background-color: #f1f2f6;
            border: 1px solid #dfe6e9;
            display: flex;
            align-items: center;
            padding: 0 10px;
            height: 38px;
            border-radius: 20px;
            width: max-content;
        }}
        .menu-item {{
            position: relative;
            margin: 0 2px;
        }}
        .menu-title {{
            padding: 4px 10px;
            cursor: pointer;
            font-size: 14px;
            font-weight: bold;
            color: #2d3436;
            border-radius: 4px;
            user-select: none;
        }}
        .menu-title:hover {{
            background-color: #dfe6e9;
        }}
        .menu-dropdown {{
            display: none;
            position: absolute;
            top: 100%;
            left: 0;
            margin-top: 6px;
            background-color: #ffffff;
            min-width: 130px;
            box-shadow: 0 4px 12px rgba(0,0,0,0.15);
            border: 1px solid #dfe6e9;
            border-radius: 6px;
            padding: 5px 0;
            z-index: 200;
        }}
        .menu-dropdown.show {{
            display: block;
        }}
        .dropdown-item {{
            padding: 8px 15px;
            font-size: 13px;
            color: #2d3436;
            cursor: pointer;
            text-align: left;
        }}
        .dropdown-item:hover {{
            background-color: #f1f2f6;
        }}

        /* 제목/메뉴 하단 구분선 */
        #divider {{
            width: 100%;
            height: 2px;
            background-color: #e2e8f0;
        }}

        /* 2. 네트워크 지도 영역 CSS */
        #network-container {{
            flex: 1;
            position: relative;
            overflow: hidden;
            background-color: #ffffff;
            box-sizing: border-box;
        }}
        svg {{
            width: 100%;
            height: 100%;
            cursor: grab;
        }}
        svg:active {{
            cursor: grabbing;
        }}

        /* 우측 상단 필터 UI (캡슐형) */
        #filter-container {{
            position: absolute;
            top: 15px;
            right: 15px;
            background-color: rgba(255, 255, 255, 0.95);
            border: 1px solid #000000;
            border-radius: 25px;
            padding: 8px 20px;
            display: flex;
            align-items: center;
            gap: 15px;
            z-index: 20;
            box-shadow: 0 2px 6px rgba(0,0,0,0.1);
        }}
        .filter-item {{
            display: flex;
            align-items: center;
            gap: 6px;
            cursor: pointer;
            font-size: 14px;
            font-weight: bold;
            color: #2d3436;
            transition: all 0.2s;
            user-select: none;
        }}
        .filter-item.inactive {{
            opacity: 0.3;
        }}
        .color-circle {{
            width: 14px;
            height: 14px;
            border-radius: 50%;
        }}
        
        /* 노드 및 화살표 CSS */
        .node {{
            cursor: pointer;
            transition: opacity 0.3s;
        }}
        .node.dimmed {{
            opacity: 0.15;
            pointer-events: none;
        }}
        .node .node-border {{
            stroke: #fff;
            stroke-width: 3px;
            fill: none;
            transition: stroke-width 0.2s, stroke 0.2s;
        }}
        .node:hover .node-border {{
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
            transition: opacity 0.3s;
        }}
        .edge.dimmed {{
            opacity: 0.15;
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
            border-left: 5px solid #2d3436;
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
        
        .info-group {{ margin-bottom: 15px; font-size: 14px; }}
        .info-label {{
            font-weight: bold;
            color: #2d3436;
            margin-bottom: 5px;
            display: flex;
            align-items: center;
        }}
        .info-value {{
            color: #2d3436;
            padding-left: 10px;
            line-height: 1.5;
        }}
        .event-link {{
            color: #0984e3;
            text-decoration: none;
            cursor: pointer;
            font-weight: bold;
            transition: color 0.2s;
        }}
        .event-link:hover {{
            color: #74b9ff;
            text-decoration: underline;
        }}
    </style>
</head>
<body>

<div id="map-container">
    <div id="bordered-box">
        <!-- 1. 제목 영역 (우측에 메뉴 통합 배치) -->
        <div id="title-area">
            <h1 id="main-title">역사적 사건 인과관계 지도</h1>
            
            <div id="menu-bar">
                <div class="menu-item">
                    <div class="menu-title">파일</div>
                    <div class="menu-dropdown">
                        <div class="dropdown-item">빈 항목 1</div>
                        <div class="dropdown-item">빈 항목 2</div>
                        <div class="dropdown-item">빈 항목 3</div>
                    </div>
                </div>
                <div class="menu-item">
                    <div class="menu-title">명령</div>
                    <div class="menu-dropdown">
                        <div class="dropdown-item">빈 항목 1</div>
                        <div class="dropdown-item">빈 항목 2</div>
                    </div>
                </div>
                <div class="menu-item">
                    <div class="menu-title">화면</div>
                    <div class="menu-dropdown">
                        <div class="dropdown-item">빈 항목 1</div>
                        <div class="dropdown-item">빈 항목 2</div>
                        <div class="dropdown-item">빈 항목 3</div>
                    </div>
                </div>
                <div class="menu-item">
                    <div class="menu-title">기타</div>
                    <div class="menu-dropdown">
                        <div class="dropdown-item">빈 항목 1</div>
                    </div>
                </div>
            </div>
        </div>

        <!-- 구분선 -->
        <div id="divider"></div>

        <!-- 2. 네트워크 지도 영역 (여백 없이 상단 밀착) -->
        <div id="network-container">
            <!-- 우측 상단 필터 UI (캡슐형) -->
            <div id="filter-container">
                <!-- JS를 통해 동적 생성 -->
            </div>

            <svg id="network">
                <defs>
                    <marker id="arrow" viewBox="0 -5 10 10" refX="28" refY="0" markerWidth="6" markerHeight="6" orient="auto">
                        <path d="M0,-5L10,0L0,5" fill="#b2bec3"></path>
                    </marker>
                </defs>
                <g id="edges-layer"></g>
                <g id="nodes-layer"></g>
            </svg>
            
            <!-- 우측 슬라이드 패널 -->
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
    </div>
</div>

<script>
    // 메뉴 바 상호작용
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
        document.querySelectorAll('.menu-dropdown').forEach(dd => {{
            dd.classList.remove('show');
        }});
    }});

    const data = {json.dumps(events_data)};
    
    const nationColors = {{
        "고구려": "#27ae60",
        "백제": "#f39c12",
        "신라": "#2980b9",
        "당": "#c0392b",
        "수": "#8e44ad",
        "대가야": "#7f8c8d"
    }};

    const activeNations = new Set(Object.keys(nationColors));

    const filterContainer = document.getElementById('filter-container');
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

    // 필터링 UI 생성
    Object.keys(nationColors).forEach(nation => {{
        const item = document.createElement('div');
        item.className = 'filter-item active';
        
        item.innerHTML = `
            <div class="color-circle" style="background-color: ${{nationColors[nation]}};"></div>
            <span>${{nation}}</span>
        `;
        
        item.addEventListener('click', () => {{
            if (activeNations.has(nation)) {{
                activeNations.delete(nation);
                item.classList.add('inactive');
            }} else {{
                activeNations.add(nation);
                item.classList.remove('inactive');
            }}
            updateFilters();
        }});
        
        filterContainer.appendChild(item);
    }});

    function updateFilters() {{
        data.nodes.forEach(node => {{
            const nations = node.nations.split(',').map(s => s.trim());
            const isActive = nations.some(n => activeNations.has(n));
            
            const g = nodeElements[node.id];
            if (isActive) {{
                g.classList.remove('dimmed');
            }} else {{
                g.classList.add('dimmed');
                if (sidePanel.classList.contains('open') && panelTitle.textContent === node.title) {{
                    closeSidebar();
                }}
            }}
        }});
        
        edgeElements.forEach(e => {{
            const sourceDimmed = nodeElements[e.source.id].classList.contains('dimmed');
            const targetDimmed = nodeElements[e.target.id].classList.contains('dimmed');
            
            if (!sourceDimmed && !targetDimmed) {{
                e.line.classList.remove('dimmed');
            }} else {{
                e.line.classList.add('dimmed');
            }}
        }});
    }}

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

    function createPieSlices(g, nationsStr, radius) {{
        const nations = nationsStr.split(',').map(s => s.trim());
        const count = nations.length;

        if (count === 1) {{
            const circle = document.createElementNS('http://www.w3.org/2000/svg', 'circle');
            circle.setAttribute('r', radius);
            circle.setAttribute('fill', nationColors[nations[0]] || '#95a5a6');
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
                path.setAttribute('fill', nationColors[nations[i]] || '#95a5a6');
                
                g.appendChild(path);
                startAngle = endAngle;
            }}
        }}

        const borderCircle = document.createElementNS('http://www.w3.org/2000/svg', 'circle');
        borderCircle.setAttribute('r', radius);
        borderCircle.setAttribute('class', 'node-border');
        g.appendChild(borderCircle);
    }}

    // 노드 그리기
    data.nodes.forEach(node => {{
        const g = document.createElementNS('http://www.w3.org/2000/svg', 'g');
        g.setAttribute('class', 'node');
        g.setAttribute('transform', `translate(${{node.x}}, ${{node.y}})`);
        
        createPieSlices(g, node.nations, 20);
        
        const textTitle = document.createElementNS('http://www.w3.org/2000/svg', 'text');
        textTitle.setAttribute('y', 38);
        textTitle.textContent = node.title;

        const textYear = document.createElementNS('http://www.w3.org/2000/svg', 'text');
        textYear.setAttribute('class', 'year');
        textYear.setAttribute('y', 53);
        textYear.textContent = node.year;
        
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

    function updateEdgesPosition() {{
        edgeElements.forEach(e => {{
            e.line.setAttribute('x1', e.source.x);
            e.line.setAttribute('y1', e.source.y);
            e.line.setAttribute('x2', e.target.x);
            e.line.setAttribute('y2', e.target.y);
        }});
    }}

    svg.addEventListener('mousemove', (e) => {{
        if (draggedNode) {{
            const newX = e.clientX - offsetX;
            const newY = e.clientY - offsetY; 
            draggedNode.x = newX;
            draggedNode.y = newY;
            
            nodeElements[draggedNode.id].setAttribute('transform', `translate(${{newX}}, ${{newY}})`);
            updateEdgesPosition();
        }}
    }});

    svg.addEventListener('mouseup', () => draggedNode = null);
    svg.addEventListener('mouseleave', () => draggedNode = null);

    // 사이드바 로직
    window.openSidebarById = function(nodeId) {{
        const targetNode = data.nodes.find(n => n.id === nodeId);
        if (targetNode) {{
            openSidebar(targetNode);
        }}
    }};

    function openSidebar(node) {{
        panelTitle.textContent = node.title;
        panelYear.textContent = node.year; 
        panelDesc.textContent = node.desc;
        panelNations.textContent = node.nations;

        const causes = data.edges.filter(e => e.target === node.id);
        panelCauses.innerHTML = causes.length > 0 
            ? causes.map(e => {{
                const n = data.nodes.find(x => x.id === e.source);
                return `• <a href="#" class="event-link" onclick="openSidebarById('${{n.id}}'); return false;">${{n.title}}</a>`;
              }}).join('<br>') 
            : '<span style="color:#b2bec3;">없음 (시작 사건)</span>';

        const results = data.edges.filter(e => e.source === node.id);
        panelResults.innerHTML = results.length > 0 
            ? results.map(e => {{
                const n = data.nodes.find(x => x.id === e.target);
                return `• <a href="#" class="event-link" onclick="openSidebarById('${{n.id}}'); return false;">${{n.title}}</a>`;
              }}).join('<br>') 
            : '<span style="color:#b2bec3;">없음 (마지막 사건)</span>';

        const firstNation = node.nations.split(',')[0].trim();
        sidePanel.style.borderLeftColor = nationColors[firstNation] || '#2d3436';
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

components.html(html_code, height=900, scrolling=False)
