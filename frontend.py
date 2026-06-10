import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime

# Import engine từ file backend
from backend import RiskAnalysisEngine

st.set_page_config(
    page_title="🔍 Interactive Risk Analysis Tool",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
    .metric-box {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 20px;
        border-radius: 10px;
        margin: 10px 0;
    }
    .risk-critical { color: #ff4444; font-weight: bold; }
    .risk-high { color: #ff9944; font-weight: bold; }
    .risk-medium { color: #ffaa44; font-weight: bold; }
    .risk-low { color: #44aa44; font-weight: bold; }
    .section-header { border-bottom: 3px solid #667eea; padding-bottom: 10px; }
</style>
""", unsafe_allow_html=True)

@st.cache_resource
def load_engine():
    """Tải và Cache Engine xử lý dữ liệu"""
    try:
        engine = RiskAnalysisEngine("data/gold/All_Beauty")
        return engine
    except Exception as e:
        st.error(f"❌ Lỗi khởi tạo engine. Vui lòng kiểm tra lại cấu trúc thư mục data: {str(e)}")
        st.stop()

def get_risk_level_badge(score: float) -> str:
    if score >= 0.8:
        return '<span class="risk-critical">🔴 CRITICAL</span>'
    elif score >= 0.6:
        return '<span class="risk-high">🟠 HIGH</span>'
    elif score >= 0.3:
        return '<span class="risk-medium">🟡 MEDIUM</span>'
    else:
        return '<span class="risk-low">🟢 LOW</span>'

def calculate_combined_risk(hybrid: float, graph: float, semantic: float) -> float:
    return 0.4 * hybrid + 0.3 * graph + 0.3 * semantic

def format_number(n: int) -> str:
    return f"{n:,}"

# Sidebar Navigation
st.sidebar.markdown("## 🔍 ĐIỀU HƯỚNG")
page = st.sidebar.radio(
    "Chọn chức năng",
    ["📊 Tổng Quan Hệ Thống", 
     "🔎 Truy Vấn Review", 
     "👤 Truy Vấn User", 
     "📦 Truy Vấn Product",
     "📈 Thống Kê & Xuất Báo Cáo"]
)

st.sidebar.markdown("---")
st.sidebar.markdown("### ⚙️ CẤU HÌNH")
threshold = st.sidebar.slider("Ngưỡng rủi ro (Risk Threshold)", min_value=0.0, max_value=1.0, value=0.7, step=0.05)
top_n = st.sidebar.number_input("Số lượng kết quả tối đa", min_value=5, max_value=500, value=50, step=5)

st.sidebar.markdown("---")
st.sidebar.caption("🚀 Phase 4 - Frontend")
st.sidebar.caption(f"Last Updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

if page == "📊 Tổng Quan Hệ Thống":
    with st.spinner("⏳ Đang tải dữ liệu tổng quan..."):
        engine = load_engine()
        stats = engine.get_system_statistics()
    
    st.markdown("# 📊 TỔNG QUAN HỆ THỐNG")
    st.markdown("**Khám phá cấu trúc đồ thị, phân bố rủi ro và thống kê toàn hệ thống**")
    
    st.markdown("### 📈 CHỈ SỐ CHÍNH")
    col1, col2, col3, col4 = st.columns(4)
    with col1: st.metric("👥 Tổng Users", format_number(stats['dataset_stats']['num_users']))
    with col2: st.metric("📝 Tổng Reviews", format_number(stats['dataset_stats']['num_reviews']))
    with col3: st.metric("📦 Tổng Products", format_number(stats['dataset_stats']['num_items']))
    with col4: st.metric("🔗 Tổng Edges", format_number(stats['dataset_stats']['num_edges_review_review']))
    
    st.markdown("### 🎯 PHÂN BỐ RỦI RO")
    risk_dist = stats['risk_distribution']
    col1, col2 = st.columns(2)
    
    with col1:
        risk_data = {
            'Risk Level': ['🟢 LOW', '🟡 MEDIUM', '🟠 HIGH', '🔴 CRITICAL'],
            'Count': [risk_dist['low'], risk_dist['medium'], risk_dist['high'], risk_dist['critical']]
        }
        fig_pie = px.pie(risk_data, values='Count', names='Risk Level', title='Phân bố theo Mức Rủi Ro',
                         color_discrete_sequence=['#44aa44', '#ffaa44', '#ff9944', '#ff4444'])
        st.plotly_chart(fig_pie, use_container_width=True)
    
    with col2:
        risk_stats = pd.DataFrame({
            'Mức Rủi Ro': ['🟢 LOW', '🟡 MEDIUM', '🟠 HIGH', '🔴 CRITICAL'],
            'Số Lượng': [format_number(risk_dist['low']), format_number(risk_dist['medium']),
                         format_number(risk_dist['high']), format_number(risk_dist['critical'])],
            'Tỷ Lệ %': [f"{risk_dist['low']/stats['dataset_stats']['num_reviews']*100:.2f}%",
                        f"{risk_dist['medium']/stats['dataset_stats']['num_reviews']*100:.2f}%",
                        f"{risk_dist['high']/stats['dataset_stats']['num_reviews']*100:.2f}%",
                        f"{risk_dist['critical']/stats['dataset_stats']['num_reviews']*100:.2f}%"]
        })
        st.dataframe(risk_stats, use_container_width=True, hide_index=True)
        
        col_a, col_b, col_c = st.columns(3)
        col_a.metric("📈 Điểm TB", f"{risk_dist['mean_score']:.4f}")
        col_b.metric("📍 Trung Vị", f"{risk_dist['median_score']:.4f}")
        col_c.metric("📊 Độ Lệch Chuẩn", f"{risk_dist['std_score']:.4f}")

elif page == "🔎 Truy Vấn Review":
    engine = load_engine()
    st.markdown("# 🔎 TRUY VẤN REVIEWS THEO ID")
    
    col1, col2 = st.columns([3, 1])
    with col1:
        review_id = st.number_input("Nhập Review ID", min_value=0, value=0, step=1)
    with col2:
        search_btn = st.button("🔍 Tìm Kiếm", use_container_width=True)
    
    if search_btn:
        with st.spinner(f"⏳ Đang truy vấn review {review_id}..."):
            result = engine.query_by_review_id(int(review_id))
        
        if 'error' in result:
            st.error(f"❌ {result['error']}")
        else:
            risk_profile = result['risk_profile']
            combined_risk = calculate_combined_risk(
                risk_profile['hybrid_anomaly_score'], risk_profile['graph_suspicion'], risk_profile['semantic_suspicion']
            )
            
            c1, c2, c3, c4 = st.columns(4)
            c1.markdown(f"### ID: `{review_id}`")
            c2.markdown(f"### Status: {'⚠️ ANOMALY' if risk_profile['label'] == 1 else '✅ NORMAL'}")
            c3.markdown(f"### Mức: {get_risk_level_badge(combined_risk)}", unsafe_allow_html=True)
            c4.markdown(f"### Split: `{'TRAIN' if risk_profile['split'] == 0 else 'VAL' if risk_profile['split'] == 1 else 'TEST'}`")
            
            st.markdown("---")
            c1, c2, c3 = st.columns(3)
            c1.metric("🔴 Hybrid Score", f"{risk_profile['hybrid_anomaly_score']:.4f}")
            c2.metric("🕸️ Graph Suspicion", f"{risk_profile['graph_suspicion']:.4f}")
            c3.metric("💭 Semantic Suspicion", f"{risk_profile['semantic_suspicion']:.4f}")
            
            risk_components = {
                'Hybrid Anomaly': risk_profile['hybrid_anomaly_score'],
                'Graph Suspicion': risk_profile['graph_suspicion'],
                'Semantic Suspicion': risk_profile['semantic_suspicion'],
                'PageRank': risk_profile['pagerank_score']
            }
            fig_bar = go.Figure(data=[go.Bar(
                x=list(risk_components.keys()), y=list(risk_components.values()),
                marker_color=['#ff6b6b', '#ee5a6f', '#ff922e', '#ffa502'],
                text=[f"{v:.3f}" for v in risk_components.values()], textposition='auto'
            )])
            fig_bar.update_layout(title="Các Thành Phần Rủi Ro", height=400)
            st.plotly_chart(fig_bar, use_container_width=True)

elif page in ["👤 Truy Vấn User", "📦 Truy Vấn Product"]:
    engine = load_engine()
    is_user = (page == "👤 Truy Vấn User")
    
    st.markdown(f"# {'👤 TRUY VẤN USERS' if is_user else '📦 TRUY VẤN PRODUCTS'} THEO ID")
    col1, col2 = st.columns([3, 1])
    with col1:
        query_id = st.text_input(f"Nhập {'User' if is_user else 'Product'} ID", value="1")
    with col2:
        search_btn = st.button("🔍 Tìm Kiếm", use_container_width=True)
        
    if search_btn:
        with st.spinner(f"⏳ Đang truy vấn {query_id}..."):
            result = engine.query_by_user_id(query_id) if is_user else engine.query_by_product_id(query_id)
            
        if result.get('num_reviews', 0) == 0:
            st.warning(f"⚠️ Không tìm thấy kết quả cho ID: {query_id}")
        else:
            c1, c2, c3 = st.columns(3)
            c1.metric("ID", query_id)
            c2.metric("📝 Số Reviews", format_number(result['num_reviews']))
            
            if is_user:
                c3.metric("⚠️ Avg Anomaly Score", f"{result['avg_anomaly_score']:.4f}")
            else:
                c3.metric("🔴 Risky Reviews", format_number(result['risky_reviews']))
                
            st.markdown("### 📋 DANH SÁCH REVIEWS")
            df = pd.DataFrame(result['reviews'])
            if len(df) > 0:
                df['label'] = df['label'].apply(lambda x: "⚠️ ANOMALY" if x == 1 else "✅ NORMAL")
                st.dataframe(df, use_container_width=True, hide_index=True)

elif page == "📈 Thống Kê & Xuất Báo Cáo":
    engine = load_engine()
    st.markdown("# 📈 THỐNG KÊ & XUẤT BÁO CÁO")
    
    fetch_btn = st.button("📥 Lấy Dữ Liệu Rủi Ro Cao", use_container_width=True)
    if fetch_btn:
        with st.spinner("⏳ Đang lấy top risky reviews..."):
            risky_reviews = engine.get_risk_log(top_n=top_n, threshold=threshold)
            
        if risky_reviews:
            df = pd.DataFrame(risky_reviews)
            df['label'] = df['label'].apply(lambda x: "⚠️ ANOMALY" if x == 1 else "✅ NORMAL")
            st.dataframe(df, use_container_width=True, hide_index=True)
            
            csv = df.to_csv(index=False)
            st.download_button("📥 Tải CSV", data=csv, file_name=f"risky_reviews.csv", mime="text/csv")