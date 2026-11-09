import streamlit as st
import streamlit.components.v1 as components
import json
import copy
import math

# ==========================================
# 1. 파이썬 기반 로직 컨트롤러 클래스
# ==========================================
class NodeMapController:
    def __init__(self, initial_data):
        self.app_data = copy.deepcopy(initial_data)
        self.initial_data = copy.deepcopy(initial_data)
        self.is_dirty = False
        self.history_stack = []
        self.history_index = -1
        
        # 드래그/클릭 상태 변수
        self.dragged_node = None
        self.drag_start_x = 0
        self.drag_start_y = 0
        self.orig_node_x = 0
        self.orig_node_y = 0
        self.offset_x = 0
        self.offset_y = 0
        self.max_drag_distance = 0
        self.DRAG_THRESHOLD = 5.0
        self.is_dragging = False
        
        self.push_history()

    def push_history(self):
        if self.history_index < len(self.history_stack) - 1:
            self.history_stack = self.history_stack[:self.history_index + 1]
        self.history_stack.append(copy.deepcopy(self.app_data))
        self.history_index += 1

    def undo(self):
        if self.history_index > 0:
            self.history_index -= 1
            self.app_data = copy.deepcopy(self.history_stack[self.history_index])

    def redo(self):
        if self.history_index < len(self.history_stack) - 1:
            self.history_index += 1
            self.app_data = copy.deepcopy(self.history_stack[self.history_index])

    def on_mouse_down(self, cursor_x, cursor_y, node):
        self.dragged_node = node
        self.is_dragging = False
        self.max_drag_distance = 0
        self.drag_start_x = cursor_x
        self.drag_start_y = cursor_y
        self.orig_node_x = node["position"]["x"]
        self.orig_node_y = node["position"]["y"]
        self.offset_x = cursor_x - node["position"]["x"]
        self.offset_y = cursor_y - node["position"]["y"]

    def on_mouse_move(self, cursor_x, cursor_y):
        if not self.dragged_node:
            return None

        dx = cursor_x - self.drag_start_x
        dy = cursor_y - self.drag_start_y
        current_distance = math.sqrt(dx**2 + dy**2)
        self.max_drag_distance = max(self.max_drag_distance, current_distance)

        if self.max_drag_distance > self.DRAG_THRESHOLD:
            self.is_dragging = True
            self.is_dirty = True
            
            new_x = cursor_x - self.offset_x
            new_y = cursor_y - self.offset_y
            
            limit = 50
            map_width = self.app_data["map_size"]["x"]
            map_height = self.app_data["map_size"]["y"]
            
            new_x = max(limit, min(new_x, map_width - limit))
            new_y = max(limit, min(new_y, map_height - limit))
            
            self.dragged_node["position"]["x"] = new_x
            self.dragged_node["position"]["y"] = new_y
            return "drag"
        return None

    def on_mouse_up(self):
        if not self.dragged_node:
            return None

        action_type = None
        if self.max_drag_distance <= self.DRAG_THRESHOLD:
            action_type = ("click", self.dragged_node)
        elif self.is_dragging:
            self.push_history()
            action_type = ("drag_end", self.dragged_node)

        self.dragged_node = None
        self.is_dragging = False
        return action_type

    def get_json_bytes(self):
        self.is_dirty = False
        return json.dumps(self.app_data, ensure_ascii=False, indent=2).encode('utf-8')

    def load_from_json(self, json_string):
        """JSON 데이터 수신 및 예외 처리 구문 검증"""
        try:
            # 1. JSON 구문 분석 (문법 오류 검출)
            loaded_data = json.loads(json_string)
            
            # 2. 최상위 데이터 타입 검사
            if not isinstance(loaded_data, dict):
                return False, "JSON 파일의 최상위 구조가 올바른 객체(Dict) 형식이 아닙니다."
            
            # 3. 필수 필수 최상위 키 존재 여부 확인
            required_keys = ["map_size", "screen_position", "nations", "nodes"]
            missing_keys = [k for k in required_keys if k not in loaded_data]
            if missing_keys:
                return False, f"필수 데이터 키가 누락되었습니다: {', '.join(missing_keys)}"
            
            # 4. 세부 구조 검증 (nodes, nations 타입 검사)
            if not isinstance(loaded_data["nodes"], list) or not isinstance(loaded_data["nations"], list):
                return False, "'nodes' 및 'nations' 항목은 배열(List) 형태여야 합니다."

            # 5. 각 노드의 필수 속성 검증
            for idx, node in enumerate(loaded_data["nodes"]):
                if not isinstance(node, dict):
                    return False, f"노드 목록의 {idx + 1}번째 항목이 객체 형식이 아닙니다."
                
                req_node_keys = ["id", "name", "position"]
                missing_node_keys = [k for k in req_node_keys if k not in node]
                if missing_node_keys:
                    return False, f"노드({node.get('name', f'index {idx}')})에 필수 속성이 누락되었습니다: {', '.join(missing_node_keys)}"
                
                if not isinstance(node["position"], dict) or "x" not in node["position"] or "y" not in node["position"]:
                    return False, f"노드({node.get('name', f'index {idx}')})의 좌표(position x, y) 형식이 올바르지 않습니다."

            # 예외 검증 통과 후 데이터 업데이트
            self.app_data = loaded_data
            self.initial_data = copy.deepcopy(loaded_data)
            self.is_dirty = False
            self.history_stack = []
            self.history_index = -1
            self.push_history()
            return True, "성공적으로 파일 데이터를 불러왔증니다."

        except json.JSONDecodeError as e:
            return False, f"JSON 파일 문법에 오류가 있습니다. (행: {e.lineno}, 열: {e.colno})"
        except Exception as e:
            return False, f"파일 검증 중 처리할 수 없는 오류가 발생했습니다: {str(e)}"

# ==========================================
# 2. 스트림릿 페이지 설정 및 초기화
# ==========================================
st.set_page_config(page_title="역사적 사건 인과관계 지도", layout="wide")

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

if 'controller' not in st.session_state:
    st.session_state.controller = NodeMapController(events_data)
if 'active_nations' not in st.session_state:
    st.session_state.active_nations = {n['id']: True for n in events_data['nations']}
if 'js_action' not in st.session_state:
    st.session_state.js_action = None

def set_action(action_type):
    st.session_state.js_action = {"type": action_type}

controller = st.session_state.controller

# ==========================================
# 3. 커스텀 CSS
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
# 4. 상단 UI: Python 기반 위젯 구성 및 로직 바인딩
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
                st.download_button(
                    label="저장하기",
                    data=controller.get_json_bytes(),
                    file_name="history_map.json",
                    mime="application/json",
                    use_container_width=True
                )
                
                # 파일 업로드 및 예외 처리
                uploaded_file = st.file_uploader("불러오기", type=["json"], label_visibility="collapsed")
                if uploaded_file is not None:
                    try:
                        file_content = uploaded_file.read().decode('utf-8')
                        success, message = controller.load_from_json(file_content)
                        if success:
                            st.session_state.js_action = {"type": "reload_data"}
                        else:
                            st.error(message)
                    except UnicodeDecodeError:
                        st.error("파일 인코딩 오류: UTF-8 형식의 텍스트 파일만 읽을 수 있습니다.")
                    except Exception as e:
                        st.error(f"파일을 읽는 도중 오류가 발생했습니다: {e}")

        with m_col2:
            with st.popover("명령"):
                if st.button("실행 취소", use_container_width=True):
                    controller.undo()
                    set_action("undo")
                if st.button("다시 실행", use_container_width=True):
                    controller.redo()
                    set_action("redo")
        with m_col3:
            with st.popover("화면"):
                st.button("화면 위치 초기화", use_container_width=True, on_click=set_action, args=("reset_screen",))
                st.button("노드 위치 초기화", use_container_width=True, on_click=set_action, args=("reset_nodes",))
                st.button("화면 전체 초기화", use_container_width=True, on_click=set_action, args=("reset_all",))
                
    with col_filter:
        filter_cols = st.columns(len(controller.app_data["nations"]))
        color_emoji = {"#27ae60": "🟢", "#f39c12": "🟠", "#2980b9": "🔵", "#c0392b": "🔴", "#8e44ad": "🟣", "#7f8c8d": "⚪"}
        
        for i, nation in enumerate(controller.app_data["nations"]):
            with filter_cols[i]:
                emoji = color_emoji.get(nation["color"], "⚫")
                is_checked = st.session_state.active_nations.get(nation['id'], True)
                new_val = st.checkbox(f"{emoji} {nation['name']}", value=is_checked, key=f"filter_{nation['id']}")
                st.session_state.active_nations[nation['id']] = new_val

    st.markdown("<hr style='margin: 0; border: none; border-top: 2px solid #e2e8f0;'>", unsafe_allow_html=True)

    # ==========================================
    # 5. 하단 지도: JavaScript 컴포넌트 통합
    # ==========================================
    html_code = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <style>
            body {{ margin: 0; padding: 0; font-family: 'Malgun Gothic', sans-serif; overflow: hidden; background-color: #ffffff; }}
            #map-container {{ display: flex; flex-direction: column; width: 100vw; height: 100vh; background-color: #ffffff; padding: 0; box-sizing: border-box; overflow: hidden; }}
            #bordered-box {{ display: flex; flex-direction: column; width: 100%; height: 100%; position: relative; outline: none; }}
            #network-container {{ flex: 1; position: relative; overflow: hidden; background-color: #ffffff; box-sizing: border-box; }}
            svg {{ width: 100%; height: 100%; cursor: grab; }}
            svg:active {{ cursor: grabbing; }}
            .node {{ cursor: grab; transition: opacity 0.3s; }}
            .node:active {{ cursor: grabbing; }}
            .node.dimmed {{ opacity: 0.15; pointer-events: none; }}
            .node .node-border {{ stroke: #fff; stroke-width: 3px; fill: none; transition: stroke-width 0.2s, stroke 0.2s; }}
            .node.hover-active .node-border {{ stroke-width: 5px; stroke: #333; }}
            .node text {{ font-size: 14px; font-weight: bold; pointer-events: none; text-anchor: middle; fill: #2d3436; }}
            .node text.year {{ font-size: 12px; font-weight: normal; fill: #636e72; }}
            .edge {{ stroke: #b2bec3; stroke-width: 2.5px; transition: opacity 0.3s, stroke 0.3s; }}
            .edge.dimmed {{ opacity: 0.15; }}
            #side-panel {{
                position: absolute; top: 0; right: -450px; width: 400px; height: 100%; background-color: #ffffff;
                box-shadow: -4px 0 15px rgba(0,0,0,0.1); transition: right 0.3s cubic-bezier(0.4, 0, 0.2, 1);
                padding: 30px 25px 30px 30px; box-sizing: border-box; z-index: 100; overflow-y: auto;
            }}
            #side-panel.open {{ right: 0; }}
            #panel-stripe {{ position: absolute; top: 0; left: 0; width: 6px; height: 100%; }}
            #close-btn {{ position: absolute; top: 15px; right: 15px; background: none; border: none; font-size: 24px; cursor: pointer; color: #636e72; }}
            h2 {{ margin-top: 0; color: #2d3436; font-size: 22px; margin-bottom: 10px; }}
            .badge {{ display: inline-block; background: #dfe6e9; color: #2d3436; padding: 4px 8px; border-radius: 4px; font-size: 14px; margin-bottom: 20px; font-weight: bold; }}
            p.desc {{ line-height: 1.6; color: #4a4a4a; font-size: 15px; margin-bottom: 25px; background-color: #f8f9fa; padding: 15px; border-radius: 8px; }}
            .info-group {{ margin-bottom: 15px; font-size: 14px; }}
            .info-label {{ font-weight: bold; color: #2d3436; margin-bottom: 5px; display: flex; align-items: center; }}
            .info-value {{ color: #2d3436; padding-left: 10px; line-height: 1.5; }}
            .event-link {{ color: #0984e3; text-decoration: none; cursor: pointer; font-weight: bold; transition: color 0.2s; }}
            .event-link:hover {{ color: #74b9ff; text-decoration: underline; }}
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
        let appData = {json.dumps(controller.app_data)};
        let initialData = JSON.parse(JSON.stringify(appData));
        
        let draggedNode = null;
        let dragStartX = 0, dragStartY = 0;
        let offsetX = 0, offsetY = 0;
        let isSignificantDrag = false;
        const DRAG_THRESHOLD = 5;
        
        let isPanning = false; 
        let panStartX = 0, panStartY = 0; 
        let panStartScreenX = 0, panStartScreenY = 0;

        let nationMap = {{}}; 
        let activeNations = new Set();
        let edgeElements = []; 
        let nodeElements = {{}}; 
        let parsedEdges = [];

        const svg = document.getElementById('network');
        const edgesLayer = document.getElementById('edges-layer');
        const nodesLayer = document.getElementById('nodes-layer');
        const sidePanel = document.getElementById('side-panel');

        function initData() {{
            nationMap = {{}};
            appData.nations.forEach(n => {{ nationMap[n.id] = n; }});
            parsedEdges = [];
            appData.nodes.forEach(node => {{
                (node.results || []).forEach(targetId => {{ parsedEdges.push({{ source: node.id, target: targetId }}); }});
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
            edgesLayer.innerHTML = ''; 
            nodesLayer.innerHTML = '';
            edgeElements = []; 
            nodeElements = {{}};
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
                    if (sidePanel.classList.contains('open') && document.getElementById('panel-title').textContent === node.name) closeSidebar(); 
                }}
            }});
            edgeElements.forEach(e => {{
                const sourceDimmed = nodeElements[e.source.id].classList.contains('dimmed');
                const targetDimmed = nodeElements[e.target.id].classList.contains('dimmed');
                if (!sourceDimmed && !targetDimmed) e.line.classList.remove('dimmed'); else e.line.classList.add('dimmed');
            }});
        }}

        function getSVGPoint(evt) {{
            const pt = svg.createSVGPoint(); 
            pt.x = evt.clientX; 
            pt.y = evt.clientY;
            return pt.matrixTransform(svg.getScreenCTM().inverse());
        }}

        function startDrag(e, node) {{
            e.preventDefault(); 
            const pt = getSVGPoint(e); 
            draggedNode = node; 
            isSignificantDrag = false;
            dragStartX = pt.x; 
            dragStartY = pt.y; 
            offsetX = pt.x - node.position.x; 
            offsetY = pt.y - node.position.y;
            nodeElements[node.id].classList.add('hover-active'); 
            e.stopPropagation();
        }}

        document.getElementById('bordered-box').addEventListener('mousemove', (e) => {{
            if (draggedNode) {{
                const pt = getSVGPoint(e); 
                const dx = pt.x - dragStartX; 
                const dy = pt.y - dragStartY;
                
                const distance = Math.sqrt(dx * dx + dy * dy);
                
                if (!isSignificantDrag) {{
                    if (distance > DRAG_THRESHOLD) {{
                        isSignificantDrag = true;
                    }} else return;
                }}

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
                appData.screen_position.x = panStartScreenX - dx; 
                appData.screen_position.y = panStartScreenY - dy;
                updateViewBox();
            }}
        }});

        document.getElementById('bordered-box').addEventListener('mouseup', () => {{
            if (draggedNode) {{
                if (!isSignificantDrag) {{
                    openSidebar(draggedNode);
                }}
                draggedNode = null; 
                isSignificantDrag = false;
            }}
            if (isPanning) isPanning = false;
        }});

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

        function openSidebar(node) {{
            document.getElementById('panel-title').textContent = node.name;
            document.getElementById('panel-year').textContent = node.year; 
            document.getElementById('panel-desc').textContent = node.description;
            const sortedIds = [...node.nations].sort((a,b) => a-b);
            document.getElementById('panel-nations').textContent = sortedIds.map(id => nationMap[id].name).join(', ');

            const causesHTML = (node.causes && node.causes.length > 0) 
                ? node.causes.map(id => {{ const n = appData.nodes.find(x => x.id === id); return `• <a href="#" class="event-link" onclick="openSidebarById('${{n.id}}'); return false;">${{n.name}}</a>`; }}).join('<br>') 
                : '<span style="color:#b2bec3;">없음 (시작 사건)</span>';
            document.getElementById('panel-causes').innerHTML = causesHTML;

            const resultsHTML = (node.results && node.results.length > 0) 
                ? node.results.map(id => {{ const n = appData.nodes.find(x => x.id === id); return `• <a href="#" class="event-link" onclick="openSidebarById('${{n.id}}'); return false;">${{n.name}}</a>`; }}).join('<br>') 
                : '<span style="color:#b2bec3;">없음 (마지막 사건)</span>';
            document.getElementById('panel-results').innerHTML = resultsHTML;

            const stripe = document.getElementById('panel-stripe');
            if (sortedIds.length === 1) {{ 
                stripe.style.background = nationMap[sortedIds[0]].color; 
            }} else {{
                const step = 100 / sortedIds.length;
                const colorStops = sortedIds.map((id, idx) => `${{nationMap[id].color}} ${{(idx * step).toFixed(2)}}% ${{((idx + 1) * step).toFixed(2)}}%`);
                stripe.style.background = `linear-gradient(to bottom, ${{colorStops.join(', ')}})`;
            }}

            sidePanel.classList.add('open');
        }}

        function closeSidebar() {{
            sidePanel.classList.remove('open');
        }}
        document.getElementById('close-btn').addEventListener('click', closeSidebar);

        window.openSidebarById = function(nodeId) {{
            const targetNode = appData.nodes.find(n => n.id === parseInt(nodeId));
            if (targetNode) openSidebar(targetNode);
        }};

        window.parent.document.addEventListener("streamlit_update", (e) => {{
            const data = e.detail;
            if (data.activeNations) {{
                activeNations = new Set(data.activeNations);
                updateFilters();
            }}
            if (data.action) {{
                const action = data.action.type;
                if (action === "reload_data") {{
                    location.reload();
                }}
            }}
        }});

        initData();
        activeNations = new Set({json.dumps([k for k, v in st.session_state.active_nations.items() if v])});
        renderNetwork();
        updateViewBox();
        window.addEventListener('resize', updateViewBox);
    </script>
    </body>
    </html>
    """
    
    components.html(html_code, height=750, scrolling=False)

# ==========================================
# 6. 세션 상태 동기화
# ==========================================
active_ids = [k for k, v in st.session_state.active_nations.items() if v]
current_action = st.session_state.js_action

st.markdown(f"""
<script>
    setTimeout(() => {{
        const evt = new CustomEvent("streamlit_update", {{
            detail: {{
                activeNations: {json.dumps(active_ids)},
                action: {json.dumps(current_action)}
            }}
        }});
        window.parent.document.dispatchEvent(evt);
    }}, 100);
</script>
""", unsafe_allow_html=True)

if current_action is not None:
    st.session_state.js_action = None
