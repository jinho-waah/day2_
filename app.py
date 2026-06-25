import streamlit as st
import pandas as pd
import numpy as np

# ── 페이지 설정 ───────────────────────────────────────────────────────────────
st.set_page_config(page_title="수강생 현황 대시보드", layout="wide", page_icon="🎓")

# ── 커스텀 CSS ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
.stApp { background: #F5F7FB; }

.dashboard-header {
    background: linear-gradient(135deg, #4F8EF7 0%, #7B5EFB 100%);
    border-radius: 16px;
    padding: 28px 36px;
    margin-bottom: 24px;
    color: white;
}
.dashboard-header h1 { font-size: 2rem; font-weight: 800; margin: 0; color: white; }
.dashboard-header p  { font-size: 0.95rem; margin: 4px 0 0; opacity: 0.85; color: white; }

.kpi-card {
    background: white;
    border-radius: 14px;
    padding: 22px 26px;
    box-shadow: 0 2px 12px rgba(79,142,247,0.10);
    border-left: 5px solid;
    margin-bottom: 8px;
}
.kpi-card.blue   { border-color: #4F8EF7; }
.kpi-card.purple { border-color: #7B5EFB; }
.kpi-card.teal   { border-color: #22C9B7; }
.kpi-card.orange { border-color: #F7894F; }
.kpi-card.green  { border-color: #4FCF7A; }
.kpi-label { font-size: 0.8rem; font-weight: 600; color: #7A8599; letter-spacing: 0.05em; text-transform: uppercase; }
.kpi-value { font-size: 1.75rem; font-weight: 800; color: #1E2A3A; margin-top: 4px; }
.kpi-sub   { font-size: 0.78rem; color: #7A8599; margin-top: 2px; }

.section-card {
    background: white;
    border-radius: 14px;
    padding: 24px 28px;
    box-shadow: 0 2px 12px rgba(79,142,247,0.08);
    margin-bottom: 24px;
}
.section-title {
    font-size: 1.05rem; font-weight: 700; color: #1E2A3A;
    margin-bottom: 16px; border-bottom: 2px solid #EEF1F8; padding-bottom: 10px;
}

.upload-area {
    background: white;
    border-radius: 14px;
    padding: 32px;
    box-shadow: 0 2px 12px rgba(79,142,247,0.08);
    margin-bottom: 24px;
    text-align: center;
}
.upload-title { font-size: 1.1rem; font-weight: 700; color: #1E2A3A; margin-bottom: 8px; }
.upload-sub { font-size: 0.85rem; color: #7A8599; margin-bottom: 16px; }

label { color: #4F8EF7 !important; font-weight: 600 !important; }
[data-testid="stDataFrame"] thead th {
    background-color: #4F8EF7 !important;
    color: white !important;
}
</style>
""", unsafe_allow_html=True)

# ── 헤더 ─────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="dashboard-header">
    <h1>🎓 수강생 현황 대시보드</h1>
    <p>기본정보 + 성과·취업현황 파일을 업로드하면 통합 분석 결과를 확인할 수 있습니다.</p>
</div>
""", unsafe_allow_html=True)

# ── 파일 업로드 ───────────────────────────────────────────────────────────────
col_up1, col_up2 = st.columns(2)
with col_up1:
    file_basic = st.file_uploader(
        "📋 수강생_기본정보.xlsx",
        type=["xlsx", "xls"],
        help="수강생 ID, 이름, 과정, 트랙 등 기본 정보가 담긴 파일",
    )
with col_up2:
    file_perf = st.file_uploader(
        "📊 수강생_성과및취업현황.xlsx",
        type=["xlsx", "xls"],
        help="수료여부, 출석률, 프로젝트점수, 취업현황 등이 담긴 파일",
    )

if not file_basic or not file_perf:
    st.info("두 파일을 모두 업로드하면 대시보드가 표시됩니다.")
    st.stop()

# ── 데이터 로드 & 머지 ────────────────────────────────────────────────────────
@st.cache_data
def load_and_merge(f_basic, f_perf):
    df_basic = pd.read_excel(f_basic)
    df_perf  = pd.read_excel(f_perf)
    df = pd.merge(df_basic, df_perf, on="수강생_ID", how="left")

    # 날짜 파싱
    for col in ["등록일", "수료일", "취업일"]:
        if col in df.columns:
            df[col] = pd.to_datetime(df[col], errors="coerce")

    # 파생 컬럼
    if "등록일" in df.columns:
        df["등록월"] = df["등록일"].dt.to_period("M").astype(str)
    return df

df = load_and_merge(file_basic, file_perf)

# ── 사이드바 필터 ─────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## 🔍 필터")

    tracks = sorted(df["수강트랙"].dropna().unique().tolist()) if "수강트랙" in df.columns else []
    selected_tracks = st.multiselect("수강트랙", tracks, default=tracks)

    courses = sorted(df["등록과정"].dropna().unique().tolist()) if "등록과정" in df.columns else []
    selected_courses = st.multiselect("등록과정", courses, default=courses)

    completion_opts = ["전체", "수료", "미수료"]
    selected_comp = st.radio("수료 여부", completion_opts, index=0)

    employment_opts = ["전체", "취업", "미취업"]
    selected_emp = st.radio("취업 여부", employment_opts, index=0)

# 필터 적용
dff = df.copy()
if selected_tracks:
    dff = dff[dff["수강트랙"].isin(selected_tracks)]
if selected_courses:
    dff = dff[dff["등록과정"].isin(selected_courses)]
if selected_comp == "수료":
    dff = dff[dff["수료여부"] == "Y"]
elif selected_comp == "미수료":
    dff = dff[dff["수료여부"] != "Y"]
if selected_emp == "취업":
    dff = dff[dff["취업여부"] == "Y"]
elif selected_emp == "미취업":
    dff = dff[dff["취업여부"] != "Y"]

if dff.empty:
    st.warning("선택된 필터에 해당하는 수강생이 없습니다.")
    st.stop()

# ── KPI 카드 ──────────────────────────────────────────────────────────────────
total        = len(dff)
completed    = (dff["수료여부"] == "Y").sum() if "수료여부" in dff.columns else 0
comp_rate    = completed / total * 100 if total else 0
employed     = (dff["취업여부"] == "Y").sum() if "취업여부" in dff.columns else 0
emp_rate     = employed / completed * 100 if completed else 0
avg_salary   = dff.loc[dff["취업여부"] == "Y", "연봉(만원)"].mean() if "연봉(만원)" in dff.columns else 0
avg_attend   = dff["출석률(%)"].mean() if "출석률(%)" in dff.columns else 0

k1, k2, k3, k4, k5 = st.columns(5)
with k1:
    st.markdown(f"""<div class="kpi-card blue">
        <div class="kpi-label">총 수강생</div>
        <div class="kpi-value">{total:,}명</div>
    </div>""", unsafe_allow_html=True)
with k2:
    st.markdown(f"""<div class="kpi-card purple">
        <div class="kpi-label">수료율</div>
        <div class="kpi-value">{comp_rate:.1f}%</div>
        <div class="kpi-sub">{completed:,}명 수료</div>
    </div>""", unsafe_allow_html=True)
with k3:
    st.markdown(f"""<div class="kpi-card teal">
        <div class="kpi-label">취업률 (수료자 기준)</div>
        <div class="kpi-value">{emp_rate:.1f}%</div>
        <div class="kpi-sub">{employed:,}명 취업</div>
    </div>""", unsafe_allow_html=True)
with k4:
    st.markdown(f"""<div class="kpi-card orange">
        <div class="kpi-label">평균 연봉 (취업자)</div>
        <div class="kpi-value">{avg_salary:,.0f}만원</div>
    </div>""", unsafe_allow_html=True)
with k5:
    st.markdown(f"""<div class="kpi-card green">
        <div class="kpi-label">평균 출석률</div>
        <div class="kpi-value">{avg_attend:.1f}%</div>
    </div>""", unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# ── Row 1: 수강트랙별 수강생 수 + 월별 등록 추이 ──────────────────────────────
r1l, r1r = st.columns([1, 1], gap="large")

with r1l:
    st.markdown('<div class="section-card">', unsafe_allow_html=True)
    st.markdown('<div class="section-title">📊 수강트랙별 수강생 수</div>', unsafe_allow_html=True)
    if "수강트랙" in dff.columns:
        track_cnt = dff["수강트랙"].value_counts().sort_values(ascending=False)
        st.bar_chart(track_cnt, color="#4F8EF7", height=280)
    st.markdown('</div>', unsafe_allow_html=True)

with r1r:
    st.markdown('<div class="section-card">', unsafe_allow_html=True)
    st.markdown('<div class="section-title">📅 월별 등록 추이</div>', unsafe_allow_html=True)
    if "등록월" in dff.columns:
        monthly_reg = dff.groupby("등록월").size().rename("등록 수")
        st.line_chart(monthly_reg, color="#7B5EFB", height=280)
    st.markdown('</div>', unsafe_allow_html=True)

# ── Row 2: 수료/취업 현황 + 성과 지표 분포 ────────────────────────────────────
r2l, r2r = st.columns([1, 1], gap="large")

with r2l:
    st.markdown('<div class="section-card">', unsafe_allow_html=True)
    st.markdown('<div class="section-title">✅ 수료 · 취업 현황 (트랙별)</div>', unsafe_allow_html=True)
    if "수강트랙" in dff.columns and "수료여부" in dff.columns and "취업여부" in dff.columns:
        summary = (
            dff.groupby("수강트랙")
            .agg(
                수강생수=("수강생_ID", "count"),
                수료수=("수료여부", lambda x: (x == "Y").sum()),
                취업수=("취업여부", lambda x: (x == "Y").sum()),
            )
            .reset_index()
        )
        summary["수료율(%)"] = (summary["수료수"] / summary["수강생수"] * 100).round(1)
        summary["취업률(%)"] = (summary["취업수"] / summary["수료수"].replace(0, np.nan) * 100).round(1)
        st.dataframe(summary, use_container_width=True, height=280)
    st.markdown('</div>', unsafe_allow_html=True)

with r2r:
    st.markdown('<div class="section-card">', unsafe_allow_html=True)
    st.markdown('<div class="section-title">📈 평균 성과 지표 (트랙별)</div>', unsafe_allow_html=True)
    perf_cols = [c for c in ["출석률(%)", "과제제출률(%)", "프로젝트점수", "튜터만족도(1-5)"] if c in dff.columns]
    if "수강트랙" in dff.columns and perf_cols:
        perf = dff.groupby("수강트랙")[perf_cols].mean().round(1)
        st.dataframe(perf, use_container_width=True, height=280)
    st.markdown('</div>', unsafe_allow_html=True)

# ── Row 3: 직무별 취업 현황 + 연봉 분포 ──────────────────────────────────────
r3l, r3r = st.columns([1, 1], gap="large")

with r3l:
    st.markdown('<div class="section-card">', unsafe_allow_html=True)
    st.markdown('<div class="section-title">💼 직무별 취업 현황</div>', unsafe_allow_html=True)
    employed_df = dff[dff["취업여부"] == "Y"]
    if "직무" in employed_df.columns and not employed_df.empty:
        job_cnt = employed_df["직무"].value_counts().head(10)
        st.bar_chart(job_cnt, color="#22C9B7", height=280)
    else:
        st.info("취업자 데이터가 없습니다.")
    st.markdown('</div>', unsafe_allow_html=True)

with r3r:
    st.markdown('<div class="section-card">', unsafe_allow_html=True)
    st.markdown('<div class="section-title">💰 트랙별 평균 연봉 (취업자)</div>', unsafe_allow_html=True)
    if "수강트랙" in employed_df.columns and "연봉(만원)" in employed_df.columns and not employed_df.empty:
        salary_by_track = (
            employed_df.groupby("수강트랙")["연봉(만원)"]
            .mean()
            .round(0)
            .sort_values(ascending=False)
        )
        st.bar_chart(salary_by_track, color="#F7894F", height=280)
    else:
        st.info("취업자 연봉 데이터가 없습니다.")
    st.markdown('</div>', unsafe_allow_html=True)

# ── 유입채널 + 지역 분포 ──────────────────────────────────────────────────────
r4l, r4r = st.columns([1, 1], gap="large")

with r4l:
    st.markdown('<div class="section-card">', unsafe_allow_html=True)
    st.markdown('<div class="section-title">📣 유입채널 분포</div>', unsafe_allow_html=True)
    if "유입채널" in dff.columns:
        channel_cnt = dff["유입채널"].value_counts()
        st.bar_chart(channel_cnt, color="#7B5EFB", height=240)
    st.markdown('</div>', unsafe_allow_html=True)

with r4r:
    st.markdown('<div class="section-card">', unsafe_allow_html=True)
    st.markdown('<div class="section-title">🗺️ 지역별 수강생 분포</div>', unsafe_allow_html=True)
    if "지역" in dff.columns:
        region_cnt = dff["지역"].value_counts()
        st.bar_chart(region_cnt, color="#4FCF7A", height=240)
    st.markdown('</div>', unsafe_allow_html=True)

# ── 원본 데이터 테이블 ────────────────────────────────────────────────────────
with st.expander("🔎 전체 데이터 보기"):
    display_cols = [c for c in [
        "수강생_ID", "이름", "수강트랙", "등록과정", "등록일",
        "수료여부", "출석률(%)", "과제제출률(%)", "프로젝트점수",
        "취업여부", "직무", "취업회사", "연봉(만원)", "취업소요일(수료후)"
    ] if c in dff.columns]
    st.dataframe(dff[display_cols], use_container_width=True)
    csv = dff[display_cols].to_csv(index=False, encoding="utf-8-sig")
    st.download_button("📥 CSV 다운로드", csv, "수강생_통합현황.csv", "text/csv")
