import streamlit as st
import json
import graphviz

# 페이지 기본 설정
st.set_page_config(page_title="역사적 사건 인과관계 지도", layout="wide")

def get_initial_data():
    return {
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

# 세션 상태 초기화
if 'app_data' not in st.session_state:
    st.session_state.app_data = get_initial_data()

# 사이드바 설정
with st.sidebar:
    st.header("파일 및 설정")
    
    # 데이터 불러오기
    uploaded_file = st.file_uploader("지도 데이터 불러오기", type=['json'])
    if uploaded_file is not None:
        try:
            st.session_state.app_data = json.load(uploaded_file)
            st.success("데이터를 성공적으로 불러왔습니다.")
        except:
            st.error("잘못된 파일 형식입니다.")

    # 데이터 저장하기
    data_str = json.dumps(st.session_state.app_data, ensure_ascii=False, indent=2)
    st.download_button(
        label="지도 데이터 저장하기",
        data=data_str,
        file_name="history_map.json",
        mime="application/json"
    )
    
    st.divider()
    
    # 초기화 버튼
    if st.button("화면 및 데이터 초기화", use_container_width=True):
        st.session_state.app_data = get_initial_data()
        st.rerun()

st.title("역사적 사건 인과관계 지도")

# 국가 데이터 및 필터링 설정
nations = st.session_state.app_data["nations"]
nation_options = {n["id"]: n["name"] for n in nations}
nation_colors = {n["id"]: n["color"] for n in nations}

selected_nations = st.multiselect(
    "국가 필터링 (선택된 국가와 관련된 사건만 표시됩니다)",
    options=list(nation_options.keys()),
    format_func=lambda x: nation_options[x],
    default=list(nation_options.keys())
)

col_map, col_info = st.columns([2.5, 1])
nodes = st.session_state.app_data["nodes"]

# 좌측: 인과관계 네트워크 (Graphviz)
with col_map:
    st.markdown("### 인과관계 네트워크")
    
    graph = graphviz.Digraph()
    graph.attr(rankdir='LR', bgcolor='transparent')
    graph.attr('node', fontname='Malgun Gothic', shape='box', style='rounded,filled', fillcolor='#ffffff', color='#dfe6e9', penwidth='2')
    graph.attr('edge', color='#b2bec3', penwidth='2')
    
    active_nodes = []
    
    # 필터링된 노드 생성
    for node in nodes:
        if any(nation_id in selected_nations for nation_id in node["nations"]):
            active_nodes.append(node)
            label = f"{node['name']}\n({node['year']})"
            graph.node(str(node["id"]), label)

    active_node_ids = {n["id"] for n in active_nodes}
    
    # 필터링된 노드 간의 엣지(연결선) 생성
    for node in active_nodes:
        for result_id in node["results"]:
            if result_id in active_node_ids:
                graph.edge(str(node["id"]), str(result_id))
                
    st.graphviz_chart(graph, use_container_width=True)

# 우측: 사건 상세 정보 표시
with col_info:
    st.markdown("### 사건 상세 정보")
    active_node_names = {n["id"]: n["name"] for n in active_nodes}
    
    if not active_node_names:
        st.info("선택된 국가와 관련된 사건이 없습니다.")
    else:
        selected_node_id = st.selectbox(
            "사건 선택",
            options=list(active_node_names.keys()),
            format_func=lambda x: active_node_names[x]
        )
        
        if selected_node_id:
            node_info = next(n for n in nodes if n["id"] == selected_node_id)
            
            st.subheader(node_info["name"])
            st.caption(f"{node_info['year']}년")
            
            st.markdown(f"**설명:**<br>{node_info['description']}", unsafe_allow_html=True)
            
            related_nations = [nation_options[nid] for nid in node_info["nations"]]
            st.markdown(f"**🚩 관련 국가:** {', '.join(related_nations)}")
            
            causes = [n["name"] for n in nodes if n["id"] in node_info["causes"]]
            results = [n["name"] for n in nodes if n["id"] in node_info["results"]]
            
            st.markdown("**🔻 원인 사건 (이전):**")
            if causes:
                for c in causes:
                    st.markdown(f"- {c}")
            else:
                st.caption("없음 (시작 사건)")
                
            st.markdown("**🔹 결과 사건 (이후):**")
            if results:
                for r in results:
                    st.markdown(f"- {r}")
            else:
                st.caption("없음 (마지막 사건)")
