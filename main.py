import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import numpy as np
import io

st.set_page_config(
    page_title="OECD 국가별 출산율 분석",
    page_icon="👶",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ─────────────────────────────────────────────
#  Global Style — Light Theme
# ─────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@300;400;600;700;900&display=swap');

html, body, [class*="css"] {
    font-family: 'Noto Sans KR', sans-serif;
}

.stApp {
    background: #f8f9fc;
    color: #1a1a2e;
}

[data-testid="stSidebar"] {
    background: #ffffff;
}

.hero-section {
    background: linear-gradient(135deg, #eef2ff 0%, #f0f9ff 50%, #faf5ff 100%);
    border: 1px solid rgba(99,102,241,0.2);
    border-radius: 20px;
    padding: 2.5rem 3rem;
    margin-bottom: 2rem;
    position: relative;
    overflow: hidden;
}

.hero-section::before {
    content: '';
    position: absolute;
    top: -50%;
    left: -50%;
    width: 200%;
    height: 200%;
    background: radial-gradient(circle at 70% 30%, rgba(99,102,241,0.07) 0%, transparent 60%),
                radial-gradient(circle at 20% 80%, rgba(59,130,246,0.05) 0%, transparent 60%);
    pointer-events: none;
}

.hero-title {
    font-size: 2.6rem;
    font-weight: 900;
    background: linear-gradient(135deg, #4f46e5, #0ea5e9, #7c3aed);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    margin: 0 0 0.5rem 0;
    line-height: 1.2;
}

.hero-sub {
    font-size: 0.95rem;
    color: #64748b;
    font-weight: 400;
}

.kpi-card {
    background: #ffffff;
    border: 1px solid #e2e8f0;
    border-radius: 16px;
    padding: 1.4rem 1.6rem;
    text-align: center;
    transition: all 0.2s;
    box-shadow: 0 1px 6px rgba(0,0,0,0.06);
}

.kpi-card:hover {
    border-color: rgba(99,102,241,0.4);
    box-shadow: 0 4px 16px rgba(99,102,241,0.12);
    transform: translateY(-2px);
}

.kpi-value {
    font-size: 2rem;
    font-weight: 700;
    color: #4f46e5;
    line-height: 1;
    margin-bottom: 0.3rem;
}

.kpi-label {
    font-size: 0.8rem;
    color: #94a3b8;
    font-weight: 400;
}

.kpi-country {
    font-size: 1rem;
    font-weight: 600;
    color: #1e293b;
    margin-bottom: 0.2rem;
}

.section-title {
    font-size: 1.3rem;
    font-weight: 700;
    color: #1e293b;
    margin-bottom: 1rem;
    display: flex;
    align-items: center;
    gap: 0.5rem;
}

.note-box {
    background: rgba(251,191,36,0.08);
    border: 1px solid rgba(251,146,36,0.3);
    border-radius: 10px;
    padding: 0.8rem 1.2rem;
    font-size: 0.82rem;
    color: #92400e;
    margin-top: 1rem;
}

.stTabs [data-baseweb="tab-list"] {
    background: #ffffff;
    border-radius: 12px;
    padding: 4px;
    gap: 4px;
    border: 1px solid #e2e8f0;
    box-shadow: 0 1px 4px rgba(0,0,0,0.05);
}

.stTabs [data-baseweb="tab"] {
    border-radius: 8px;
    color: #64748b;
    font-weight: 600;
    font-size: 0.9rem;
}

.stTabs [aria-selected="true"] {
    background: rgba(99,102,241,0.1) !important;
    color: #4f46e5 !important;
}

div[data-testid="metric-container"] {
    background: #ffffff;
    border: 1px solid #e2e8f0;
    border-radius: 12px;
    padding: 1rem;
}
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────
#  데이터
# ─────────────────────────────────────────────
raw = [
    ("대한민국",   0.80, "KOR", "아시아",     51.7,  "원본"),
    ("스페인",     1.11, "ESP", "유럽",       47.4,  "원본"),
    ("리투아니아", 1.03, "LTU", "유럽",        2.8,  "원본"),
    ("라트비아",   1.16, "LVA", "유럽",        1.9,  "원본"),
    ("폴란드",     1.16, "POL", "유럽",       37.6,  "OECD추정"),
    ("그리스",     1.23, "GRC", "유럽",       10.4,  "원본"),
    ("체코",       1.27, "CZE", "유럽",       10.9,  "원본"),
    ("독일",       1.30, "DEU", "유럽",       84.4,  "원본"),
    ("핀란드",     1.30, "FIN", "유럽",        5.5,  "원본"),
    ("헝가리",     1.31, "HUN", "유럽",        9.7,  "원본"),
    ("에스토니아", 1.35, "EST", "유럽",        1.4,  "OECD추정"),
    ("튀르키예",   1.37, "TUR", "유럽/아시아", 85.3,  "원본"),
    ("영국",       1.39, "GBR", "유럽",       67.6,  "원본"),
    ("스웨덴",     1.42, "SWE", "유럽",       10.5,  "원본"),
    ("벨기에",     1.44, "BEL", "유럽",       11.6,  "원본"),
    ("칠레",       1.47, "CHL", "아메리카",   19.5,  "OECD추정"),
    ("노르웨이",   1.48, "NOR", "유럽",        5.4,  "원본"),
    ("덴마크",     1.51, "DNK", "유럽",        5.9,  "원본"),
    ("뉴질랜드",   1.55, "NZL", "오세아니아",  5.1,  "원본"),
    ("프랑스",     1.56, "FRA", "유럽",       68.2,  "원본"),
    ("슬로바키아", 1.57, "SVK", "유럽",        5.8,  "OECD추정"),
    ("미국",       1.58, "USA", "아메리카",  335.0,  "원본"),
    ("호주",       1.58, "AUS", "오세아니아", 26.5,  "OECD추정"),
    ("아이슬란드", 1.59, "ISL", "유럽",        0.37, "OECD추정"),
    ("아일랜드",   1.62, "IRL", "유럽",        5.1,  "OECD추정"),
    ("포르투갈",   1.38, "PRT", "유럽",       10.2,  "OECD추정"),
    ("슬로베니아", 1.71, "SVN", "유럽",        2.1,  "OECD추정"),
    ("멕시코",     1.82, "MEX", "아메리카",  127.6,  "OECD추정"),
    ("이스라엘",   2.89, "ISR", "아시아",      9.7,  "OECD추정"),
]

df = pd.DataFrame(raw, columns=["국가","출산율","국가코드","대륙","인구(백만)","출처"])
df_sorted = df.sort_values("출산율").reset_index(drop=True)
df_sorted["순위"] = df_sorted.index + 1

years = [2000, 2003, 2006, 2009, 2012, 2015, 2018, 2020, 2021, 2022, 2023]
ts_raw = {
    "대한민국":   [1.47, 1.19, 1.13, 1.15, 1.30, 1.24, 0.98, 0.84, 0.81, 0.78, 0.80],
    "스페인":     [1.23, 1.30, 1.37, 1.40, 1.32, 1.33, 1.25, 1.19, 1.19, 1.16, 1.11],
    "독일":       [1.38, 1.34, 1.33, 1.36, 1.41, 1.50, 1.57, 1.53, 1.58, 1.46, 1.30],
    "프랑스":     [1.89, 1.89, 1.98, 1.99, 2.00, 1.96, 1.87, 1.84, 1.80, 1.79, 1.56],
    "미국":       [2.06, 2.04, 2.10, 2.01, 1.88, 1.84, 1.73, 1.64, 1.66, 1.67, 1.58],
    "이스라엘":   [2.68, 2.76, 2.80, 2.90, 2.97, 3.09, 3.01, 2.94, 2.93, 2.89, 2.89],
    "노르웨이":   [1.85, 1.80, 1.88, 1.98, 1.85, 1.74, 1.62, 1.48, 1.55, 1.41, 1.48],
    "핀란드":     [1.73, 1.77, 1.84, 1.86, 1.80, 1.65, 1.41, 1.37, 1.46, 1.32, 1.30],
}
ts_df = pd.DataFrame(ts_raw, index=years).reset_index().rename(columns={"index": "연도"})
ts_long = ts_df.melt(id_vars="연도", var_name="국가", value_name="출산율")

# 공통 플롯 색상
PLOT_BG  = "#ffffff"
PAPER_BG = "#f8f9fc"
GRID_CLR = "rgba(0,0,0,0.06)"
TICK_CLR = "#64748b"
TEXT_CLR = "#1e293b"

# ─────────────────────────────────────────────
#  Hero Header
# ─────────────────────────────────────────────
st.markdown("""
<div class="hero-section">
    <div class="hero-title">👶 OECD 국가별 출산율 분석 대시보드</div>
    <div class="hero-sub">
        출처: OECD Family Database · 기준연도: 2022–2023 (국가별 최신 가용 데이터 기준)<br>
        ※ 일부 국가(*표시)는 원본 이미지 데이터 누락으로 OECD 공개 추정값 사용
    </div>
</div>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────
#  KPI 카드
# ─────────────────────────────────────────────
k1, k2, k3, k4, k5 = st.columns(5)

with k1:
    st.markdown("""<div class="kpi-card">
        <div class="kpi-label">🔴 최저 출산율</div>
        <div class="kpi-country">대한민국</div>
        <div class="kpi-value" style="color:#ef4444;">0.80</div>
        <div class="kpi-label">명 / 여성</div>
    </div>""", unsafe_allow_html=True)

with k2:
    st.markdown("""<div class="kpi-card">
        <div class="kpi-label">🟢 최고 출산율</div>
        <div class="kpi-country">이스라엘</div>
        <div class="kpi-value" style="color:#10b981;">2.89</div>
        <div class="kpi-label">명 / 여성</div>
    </div>""", unsafe_allow_html=True)

with k3:
    avg = round(df["출산율"].mean(), 2)
    st.markdown(f"""<div class="kpi-card">
        <div class="kpi-label">📊 29개국 평균</div>
        <div class="kpi-country">OECD</div>
        <div class="kpi-value">{avg}</div>
        <div class="kpi-label">명 / 여성</div>
    </div>""", unsafe_allow_html=True)

with k4:
    below = (df["출산율"] < 2.1).sum()
    st.markdown(f"""<div class="kpi-card">
        <div class="kpi-label">⚠️ 인구대체율 미달</div>
        <div class="kpi-country">2.1명 미만</div>
        <div class="kpi-value" style="color:#f59e0b;">{below}</div>
        <div class="kpi-label">개국 / 29개국</div>
    </div>""", unsafe_allow_html=True)

with k5:
    below_15 = (df["출산율"] < 1.5).sum()
    st.markdown(f"""<div class="kpi-card">
        <div class="kpi-label">🚨 초저출산 (1.5↓)</div>
        <div class="kpi-country">임계점 이하</div>
        <div class="kpi-value" style="color:#ef4444;">{below_15}</div>
        <div class="kpi-label">개국 / 29개국</div>
    </div>""", unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# ─────────────────────────────────────────────
#  탭
# ─────────────────────────────────────────────
tab1, tab2, tab3, tab4 = st.tabs([
    "📊 국가별 순위",
    "🗺️ 세계 지도",
    "📈 연도별 추이",
    "🔵 인구수 버블 차트",
])

# ──────────────────────────────────────────────
#  TAB 1
# ──────────────────────────────────────────────
with tab1:
    st.markdown('<div class="section-title">📊 출산율 낮은 순서 — 전체 국가 순위</div>', unsafe_allow_html=True)

    col_chart, col_ctrl = st.columns([5, 1])

    with col_ctrl:
        st.markdown("**🎛️ 옵션**")
        show_estimated = st.checkbox("추정값 국가 강조", value=True)
        color_theme = st.selectbox("색상 테마", ["인디고/파랑", "초록/청록", "주황/빨강"], index=0)

    THEME_MAP = {
        "인디고/파랑": ("#6366f1", "#3b82f6"),
        "초록/청록":   ("#10b981", "#06b6d4"),
        "주황/빨강":   ("#f97316", "#ef4444"),
    }
    c_primary, c_accent = THEME_MAP[color_theme]

    bar_colors = []
    for _, row in df_sorted.iterrows():
        if row["국가"] == "대한민국":
            bar_colors.append("#ef4444")
        elif show_estimated and row["출처"] == "OECD추정":
            bar_colors.append("#f59e0b")
        else:
            bar_colors.append(c_primary)

    hover_text = [
        f"<b>{r['국가']}</b><br>"
        f"순위: {int(r['순위'])}위 (출산율 낮은 순)<br>"
        f"출산율: {r['출산율']:.2f} 명/여성<br>"
        f"인구: {r['인구(백만)']} 백만 명<br>"
        f"대륙: {r['대륙']}<br>"
        f"데이터: {'원본 이미지' if r['출처']=='원본' else 'OECD 공개 추정값'}"
        for _, r in df_sorted.iterrows()
    ]

    fig1 = go.Figure()
    fig1.add_trace(go.Bar(
        x=df_sorted["출산율"],
        y=df_sorted["국가"],
        orientation="h",
        marker=dict(
            color=bar_colors,
            line=dict(color="rgba(0,0,0,0.05)", width=0.5),
            opacity=0.88,
        ),
        text=[f"  {v:.2f}" for v in df_sorted["출산율"]],
        textposition="outside",
        textfont=dict(color="#374151", size=11),
        hovertemplate="%{customdata}<extra></extra>",
        customdata=hover_text,
    ))

    fig1.add_vline(
        x=2.1, line_dash="dot", line_color="#d97706", line_width=2,
        annotation_text="인구대체율 2.1",
        annotation_font=dict(color="#d97706", size=11),
        annotation_position="top right",
    )
    fig1.add_vline(
        x=1.5, line_dash="dot", line_color="#dc2626", line_width=1.5,
        annotation_text="초저출산 1.5",
        annotation_font=dict(color="#dc2626", size=11),
        annotation_position="bottom right",
    )

    fig1.update_layout(
        height=860,
        xaxis=dict(
            title="출산율 (명/여성)", range=[0, 3.4],
            gridcolor=GRID_CLR, zeroline=False,
            tickfont=dict(color=TICK_CLR),
            title_font=dict(color=TICK_CLR),
        ),
        yaxis=dict(tickfont=dict(size=12, color=TEXT_CLR)),
        plot_bgcolor=PLOT_BG,
        paper_bgcolor=PAPER_BG,
        font=dict(family="Noto Sans KR", color=TEXT_CLR),
        margin=dict(l=20, r=80, t=30, b=50),
        showlegend=False,
    )

    with col_chart:
        st.plotly_chart(fig1, use_container_width=True)

        lcol1, lcol2, lcol3, lcol4 = st.columns(4)
        with lcol1:
            st.markdown("🔴 **대한민국** (최저)")
        with lcol2:
            st.markdown("🟣 **원본 이미지** 데이터")
        with lcol3:
            if show_estimated:
                st.markdown("🟡 **OECD 추정값** 국가")
        with lcol4:
            st.markdown("🟡 **대체율 2.1** / 🔴 **초저 1.5**")

        try:
            img_bytes = fig1.to_image(format="png", width=1400, height=900, scale=2)
            st.download_button(
                label="⬇️ 순위 이미지 다운로드 (PNG)",
                data=img_bytes,
                file_name="oecd_fertility_ranking.png",
                mime="image/png",
            )
        except Exception:
            st.info("💡 PNG 다운로드는 kaleido 설치 후 사용 가능합니다.")

    st.markdown("""<div class="note-box">
        ⚠️ <b>OECD 추정값 적용 국가</b>: 아이슬란드(1.59), 포르투갈(1.38), 아일랜드(1.62), 호주(1.58), 멕시코(1.82),
        폴란드(1.16), 슬로바키아(1.57), 칠레(1.47), 슬로베니아(1.71), 이스라엘(2.89), 에스토니아(1.35)
        — 출처: OECD Family Database (SF2.1 Fertility Rates, 2025년 4월 업데이트)
    </div>""", unsafe_allow_html=True)

# ──────────────────────────────────────────────
#  TAB 2
# ──────────────────────────────────────────────
with tab2:
    st.markdown('<div class="section-title">🗺️ 세계 지도로 보는 출산율 분포</div>', unsafe_allow_html=True)

    fig2 = px.choropleth(
        df,
        locations="국가코드",
        color="출산율",
        hover_name="국가",
        hover_data={"출산율": ":.2f", "인구(백만)": True, "대륙": True, "국가코드": False},
        color_continuous_scale=[
            [0.0,  "#ef4444"],
            [0.15, "#f97316"],
            [0.35, "#facc15"],
            [0.60, "#34d399"],
            [1.0,  "#0ea5e9"],
        ],
        range_color=[0.7, 3.0],
        labels={"출산율": "출산율", "인구(백만)": "인구(백만)"},
    )
    fig2.update_geos(
        showframe=False,
        showcoastlines=True,
        coastlinecolor="rgba(0,0,0,0.15)",
        showland=True,
        landcolor="#f1f5f9",
        showocean=True,
        oceancolor="#dbeafe",
        showlakes=False,
        projection_type="natural earth",
        bgcolor=PAPER_BG,
    )
    fig2.update_layout(
        height=520,
        paper_bgcolor=PAPER_BG,
        font=dict(family="Noto Sans KR", color=TEXT_CLR),
        coloraxis_colorbar=dict(
            title="출산율",
            tickfont=dict(color=TICK_CLR),
            title_font=dict(color=TICK_CLR),
        ),
        margin=dict(l=0, r=0, t=10, b=0),
    )

    st.plotly_chart(fig2, use_container_width=True)
    st.markdown("**색상 가이드**: 🔴 붉은색 → 출산율 낮음 | 🟡 노랑 → 중간 | 🔵/🟢 파랑·초록 → 출산율 높음")

# ──────────────────────────────────────────────
#  TAB 3
# ──────────────────────────────────────────────
with tab3:
    st.markdown('<div class="section-title">📈 주요 국가 출산율 연도별 추이 (2000–2023)</div>', unsafe_allow_html=True)

    countries_available = list(ts_raw.keys())
    selected = st.multiselect(
        "국가 선택 (복수 선택 가능)",
        options=countries_available,
        default=["대한민국", "프랑스", "이스라엘", "미국", "독일"],
    )

    if selected:
        filtered = ts_long[ts_long["국가"].isin(selected)]

        COLORS_TS = {
            "대한민국":   "#ef4444",
            "스페인":     "#f97316",
            "독일":       "#d97706",
            "프랑스":     "#16a34a",
            "미국":       "#2563eb",
            "이스라엘":   "#7c3aed",
            "노르웨이":   "#db2777",
            "핀란드":     "#0891b2",
        }

        fig3 = go.Figure()
        for country in selected:
            cdf = filtered[filtered["국가"] == country]
            fig3.add_trace(go.Scatter(
                x=cdf["연도"], y=cdf["출산율"],
                mode="lines+markers",
                name=country,
                line=dict(width=2.5, color=COLORS_TS.get(country, "#64748b")),
                marker=dict(size=7),
                hovertemplate=f"<b>{country}</b><br>연도: %{{x}}<br>출산율: %{{y:.2f}}<extra></extra>",
            ))

        fig3.add_hline(y=2.1, line_dash="dot", line_color="#d97706", line_width=1.5)
        fig3.add_hline(y=1.5, line_dash="dot", line_color="#dc2626", line_width=1.5)

        fig3.add_vrect(
            x0=2020, x1=2021,
            fillcolor="rgba(0,0,0,0.03)",
            layer="below", line_width=0,
        )

        fig3.update_layout(
            height=480,
            xaxis=dict(
                title="연도",
                gridcolor=GRID_CLR,
                tickfont=dict(color=TICK_CLR),
                title_font=dict(color=TICK_CLR),
            ),
            yaxis=dict(
                title="출산율 (명/여성)",
                range=[0.5, 3.5],
                gridcolor=GRID_CLR,
                tickfont=dict(color=TICK_CLR),
                title_font=dict(color=TICK_CLR),
            ),
            legend=dict(
                font=dict(color=TEXT_CLR),
                bgcolor="rgba(255,255,255,0.9)",
                bordercolor="#e2e8f0",
                borderwidth=1,
            ),
            plot_bgcolor=PLOT_BG,
            paper_bgcolor=PAPER_BG,
            font=dict(family="Noto Sans KR", color=TEXT_CLR),
            margin=dict(l=20, r=100, t=30, b=50),
        )

        st.plotly_chart(fig3, use_container_width=True)
        st.markdown("""<div class="note-box">
            📌 시계열 데이터는 OECD Family Database / World Bank 근사값 기반이며, 일부 연도는 보간 처리되었습니다.
        </div>""", unsafe_allow_html=True)
    else:
        st.info("위에서 국가를 1개 이상 선택해주세요.")

# ──────────────────────────────────────────────
#  TAB 4
# ──────────────────────────────────────────────
with tab4:
    st.markdown('<div class="section-title">🔵 인구수 × 출산율 버블 차트</div>', unsafe_allow_html=True)
    st.markdown("버블 크기 = 인구 규모, 색상 = 대륙")

    CONTINENT_COLORS = {
        "유럽":       "#6366f1",
        "아시아":     "#ef4444",
        "아메리카":   "#10b981",
        "오세아니아": "#f59e0b",
        "유럽/아시아":"#ec4899",
    }

    fig4 = go.Figure()

    for continent in df["대륙"].unique():
        sub = df[df["대륙"] == continent]
        fig4.add_trace(go.Scatter(
            x=sub["출산율"],
            y=sub["인구(백만)"],
            mode="markers+text",
            name=continent,
            text=sub["국가"],
            textposition="top center",
            textfont=dict(size=9.5, color="#374151"),
            marker=dict(
                size=sub["인구(백만)"].apply(lambda p: max(10, min(60, p**0.5 * 5))),
                color=CONTINENT_COLORS.get(continent, "#94a3b8"),
                opacity=0.75,
                line=dict(color="rgba(255,255,255,0.8)", width=1.5),
            ),
            hovertemplate=(
                "<b>%{text}</b><br>"
                "출산율: %{x:.2f}<br>"
                "인구: %{y:.1f}백만 명<br>"
                f"대륙: {continent}<extra></extra>"
            ),
        ))

    fig4.add_vline(x=2.1, line_dash="dot", line_color="#d97706", line_width=1.5)
    fig4.add_vline(x=1.5, line_dash="dot", line_color="#dc2626", line_width=1.5)

    fig4.update_layout(
        height=540,
        xaxis=dict(
            title="출산율 (명/여성)", range=[0.6, 3.3],
            gridcolor=GRID_CLR,
            tickfont=dict(color=TICK_CLR), title_font=dict(color=TICK_CLR),
        ),
        yaxis=dict(
            title="인구 (백만 명)",
            type="log",
            gridcolor=GRID_CLR,
            tickfont=dict(color=TICK_CLR), title_font=dict(color=TICK_CLR),
        ),
        legend=dict(
            font=dict(color=TEXT_CLR),
            bgcolor="rgba(255,255,255,0.9)",
            bordercolor="#e2e8f0",
            borderwidth=1,
            title=dict(text="대륙", font=dict(color=TICK_CLR)),
        ),
        plot_bgcolor=PLOT_BG,
        paper_bgcolor=PAPER_BG,
        font=dict(family="Noto Sans KR", color=TEXT_CLR),
        margin=dict(l=20, r=30, t=30, b=60),
    )

    st.plotly_chart(fig4, use_container_width=True)

# ─────────────────────────────────────────────
#  푸터
# ─────────────────────────────────────────────
st.markdown("---")
st.markdown("""
<div style="text-align:center; color:#94a3b8; font-size:0.8rem; padding:1rem 0;">
    📊 데이터 출처: OECD Family Database (SF2.1 Fertility Rates, 2025.04) · World Bank WDI<br>
    🛠️ Built with Streamlit + Plotly · 일부 국가는 OECD 공개 추정값 사용
</div>
""", unsafe_allow_html=True)
