import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
from pathlib import Path
import json
from collections import defaultdict
from io import BytesIO

st.set_page_config(
    page_title="Хугацаа хэтрэлтийн шинжилгээ",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── CSS ──────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
/* ── base ── */
html,body,[data-testid="stAppViewContainer"],[data-testid="stMain"],
[data-testid="stHeader"],.main,.block-container{
    background:#f8f9fb !important; color:#111 !important;}
.block-container{padding-top:1.6rem !important;}

/* ── sidebar ── */
[data-testid="stSidebar"],[data-testid="stSidebarContent"]{
    background:#ffffff !important; border-right:1px solid #e8e8e8;}

/* Sidebar текст бүгд хар */
[data-testid="stSidebar"] *{color:#111111 !important;}
[data-testid="stSidebar"] .stRadio label{font-size:13px;}
[data-testid="stSidebar"] hr{border-color:#eee;}

/* Input field — цагаан дэвсгэр, хар текст */
[data-testid="stSidebar"] input,
[data-testid="stSidebar"] textarea,
[data-testid="stSidebar"] [data-baseweb="input"] input,
[data-testid="stSidebar"] [data-baseweb="textarea"] textarea {
    background-color:#ffffff !important;
    color:#111111 !important;
    border:1px solid #cccccc !important;
    border-radius:6px !important;}

/* Selectbox / dropdown */
[data-testid="stSidebar"] [data-baseweb="select"] {
    background-color:#ffffff !important;}
[data-testid="stSidebar"] [data-baseweb="select"] > div {
    background-color:#ffffff !important;
    color:#111111 !important;
    border:1px solid #cccccc !important;
    border-radius:6px !important;}
[data-testid="stSidebar"] [data-baseweb="select"] span {
    color:#111111 !important;}

/* File uploader */
[data-testid="stSidebar"] [data-testid="stFileUploader"] {
    background-color:#f8f9fb !important;
    border:1px dashed #cccccc !important;
    border-radius:8px !important;}
[data-testid="stSidebar"] [data-testid="stFileUploader"] * {
    color:#ffffff !important;}
[data-testid="stSidebar"] [data-testid="stFileUploader"] button {
    background-color:#1a73e8 !important;
    color:#ffffff !important;
    border:none !important;
    border-radius:6px !important;}

/* Slider */
[data-testid="stSidebar"] [data-testid="stSlider"] * {
    color:#111111 !important;}

/* Multiselect */
[data-testid="stSidebar"] [data-baseweb="tag"] {
    background-color:#e8f0fe !important;}
[data-testid="stSidebar"] [data-baseweb="tag"] span {
    color:#1a73e8 !important;}

/* Date input */
[data-testid="stSidebar"] [data-testid="stDateInput"] input {
    background-color:#111111 !important;
    color:#ffffff !important;}

/* Expander */
[data-testid="stSidebar"] [data-testid="stExpander"] {
    background-color:#f8f9fb !important;
    border:1px solid #e0e0e0 !important;
    border-radius:8px !important;}
[data-testid="stSidebar"] [data-testid="stExpander"] summary {
    color:#111111 !important;}

/* ── top-level tabs ── */
.stTabs [data-baseweb="tab-list"]{
    gap:4px; background:#fff;
    border-radius:12px; padding:5px 6px;
    border:1px solid #e4e6ea;
    box-shadow:0 1px 4px rgba(0,0,0,.06);
    width:fit-content;}
.stTabs [data-baseweb="tab"]{
    border-radius:8px; padding:8px 22px;
    font-size:14px; font-weight:600;
    color:#555 !important; background:transparent;
    border:none !important;}
.stTabs [aria-selected="true"]{
    background:#1a73e8 !important;
    color:#fff !important;
    box-shadow:0 2px 6px rgba(26,115,232,.35);}

/* ── section header ── */
.sh{
    font-size:13.5px; font-weight:700; color:#222;
    margin:1.1rem 0 .45rem;
    display:flex; align-items:center; gap:7px;}
.sh::before{content:""; display:inline-block;
    width:3px; height:14px; border-radius:2px;
    background:#1a73e8; flex-shrink:0;}

/* ── sub-section card ── */
.sub-card{
    background:#fff; border-radius:12px;
    border:1px solid #e8eaed;
    padding:16px 18px; margin-bottom:14px;
    box-shadow:0 1px 3px rgba(0,0,0,.05);}

/* ── KPI card ── */
[data-testid="stMetric"]{
    background:#fff !important; border-radius:10px;
    padding:12px 16px !important;
    border:1px solid #e8eaed;
    box-shadow:0 1px 3px rgba(0,0,0,.04);}
[data-testid="stMetricLabel"] p{color:#666 !important; font-size:12px !important;}
[data-testid="stMetricValue"]{color:#111 !important; font-size:1.5rem !important;}
[data-testid="stMetricDelta"]{font-size:12px !important;}

/* ── info boxes ── */
.box{padding:10px 14px; border-radius:8px;
     font-size:13px; margin-bottom:10px; line-height:1.5;}
.box-blue  {background:#f0f7ff; border-left:3px solid #1a73e8;}
.box-green {background:#f0faf5; border-left:3px solid #1d9e75;}
.box-warn  {background:#fff8e1; border-left:3px solid #f59e0b;}
.box-danger{background:#fff5f5; border-left:3px solid #e24b4a;}

/* ── Customer sub-tabs: TAB_CUST дотор 2-р st.tabs() → flex-wrap ── */
[data-testid="stTabs"]:has(button[id*="tabs"][role="tab"]:nth-of-type(5)) [data-baseweb="tab-list"]{
    flex-wrap: wrap !important;
    row-gap: 4px !important;
}
/* Харилцагч түвшний tab: TAB_CUST дотор байгаа бүх sub-tab-д heuristic selector */
.stTabs [data-baseweb="tab-list"]:has([data-baseweb="tab"]:nth-child(5)){
    flex-wrap: wrap !important;
    background:#f4f6f9 !important; border-radius:10px !important;
    padding:5px 6px !important; border:1px solid #e0e2e6 !important;
    gap:3px !important; width:100% !important;
    box-shadow:0 1px 3px rgba(0,0,0,.06) !important;
    row-gap:5px !important;}
.stTabs [data-baseweb="tab-list"]:has([data-baseweb="tab"]:nth-child(5)) [data-baseweb="tab"]{
    border-radius:7px !important; padding:7px 15px !important;
    font-size:13px !important; font-weight:600 !important;
    color:#555 !important; background:transparent !important;
    border:none !important; flex-shrink:0 !important;
    min-width:fit-content !important;}
.stTabs [data-baseweb="tab-list"]:has([data-baseweb="tab"]:nth-child(5)) [aria-selected="true"]{
    background:#1a73e8 !important; color:#fff !important;
    box-shadow:0 2px 5px rgba(26,115,232,.3) !important;}

/* ── download button ── */
.stDownloadButton button{
    background:#1a73e8 !important; color:#fff !important;
    border:none; border-radius:8px; font-weight:600;}

/* ── text ── */
h1,h2,h3,h4,h5,h6,p,span,div,label,
.stMarkdown,.stText,[data-testid="stMarkdownContainer"]{color:#111 !important;}
</style>
""", unsafe_allow_html=True)

# ── Plotly theme ─────────────────────────────────────────────────────────────
FONT   = dict(family="Arial,sans-serif", color="#111", size=12)
AXIS   = dict(tickfont=dict(color="#111",size=11),
              title_font=dict(color="#444",size=12),
              gridcolor="#f0f0f0", linecolor="#ddd")
LEGEND = dict(font=dict(color="#111",size=11), bgcolor="rgba(255,255,255,.95)",
              bordercolor="#ddd", borderwidth=1)
BASE   = dict(plot_bgcolor="#fff", paper_bgcolor="#fff", font=FONT,
              margin=dict(l=10,r=16,t=32,b=8), legend=LEGEND)

def L(fig, **kw):
    fig.update_layout(**{**BASE, **kw})
    fig.update_xaxes(**AXIS); fig.update_yaxes(**AXIS)
    return fig

CLR_STATUS = {"O_active":"#e24b4a","O_max":"#f59e0b","C":"#1d9e75"}
CLR_BUCKET = ["#1d9e75","#84cc16","#f59e0b","#f97316","#ef4444","#dc2626","#7f1d1d"]

# ── Column names ──────────────────────────────────────────────────────────────
COL_CUST    = "cust_code"
COL_DATE    = "adv_date"
COL_AMT     = "adv_amt"
COL_STATUS1 = "status_1"
COL_STATUS  = "status"
COL_SCORE   = "total_score"
COL_IS_OD   = "is_overdue"
COL_MAX_OD  = "max_overdue_day"
COL_ACT_OD  = "active_overdue"
COL_MAX_AOD = "max_active_overdue_day"

BUCKET_BINS = [-1, 0, 1, 5, 10, 15, 30, 9999]
BUCKET_LBLS = ["0","1","2–5","6–10","11–15","16–30","30+"]

CUST_ATTRS = ["age","gender","marital_status","edu_name","location",
              "has_ios","is_bio_login","fin_score","psy_score",
              "total_score_sr","slry_last_amt","slry_last_avg_6m",
              "zms_active_ln_cnt","is_device_remember","zms_monthly_payment",
              "slry_last_row_cnt_24m","slry_has_cont_salary_3m",
              "zms_closed_ln_total_amount","has_active_overdue_loan"]

# ── Archive ───────────────────────────────────────────────────────────────────
ARCHIVE_DIR = Path("archive"); ARCHIVE_DIR.mkdir(exist_ok=True)

ap  = lambda p: ARCHIVE_DIR / f"{p}.parquet"
mp_ = lambda p: ARCHIVE_DIR / f"{p}.json"
def list_periods(): return [f.stem for f in sorted(ARCHIVE_DIR.glob("*.parquet"),reverse=True)]
def save_period(df,period,filename=""):
    df.to_parquet(ap(period),index=False)
    mp_(period).write_text(json.dumps(
        {"filename":filename,"saved_at":datetime.now().isoformat(),"rows":len(df)},ensure_ascii=False))
def load_meta(p): return json.loads(mp_(p).read_text()) if mp_(p).exists() else {}
def load_period(p):
    df = pd.read_parquet(ap(p))
    df.columns = df.columns.str.strip().str.lower()
    return df
def delete_period(p):
    for f in [ap(p),mp_(p)]:
        if f.exists(): f.unlink()

# ── Preprocess ────────────────────────────────────────────────────────────────
@st.cache_data(show_spinner=False)
def preprocess(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    # Баганын нэрийг lowercase + strip → жишээ нь "Cust_code" → "cust_code"
    df.columns = df.columns.str.strip().str.lower()

    if COL_DATE in df.columns:
        df[COL_DATE] = pd.to_datetime(df[COL_DATE], errors="coerce")
    for c in [COL_AMT, COL_SCORE, COL_MAX_OD, COL_MAX_AOD]:
        if c in df.columns:
            df[c] = pd.to_numeric(df[c], errors="coerce")

    # max_active_overdue_day хоосон → 0  (dependent variable)
    if COL_MAX_AOD in df.columns:
        df[COL_MAX_AOD] = df[COL_MAX_AOD].fillna(0)

    # Цалингийн -1 утга → NaN (мэдээлэл байхгүй гэсэн утга)
    for c in ["slry_last_amt","slry_last_avg_6m","slry_last_row_cnt_24m",
              "zms_monthly_payment","zms_closed_ln_total_amount"]:
        if c in df.columns:
            df[c] = pd.to_numeric(df[c], errors="coerce").replace(-1, np.nan)

    for c in [COL_IS_OD, COL_ACT_OD]:
        if c in df.columns:
            df[c] = df[c].map(lambda x:
                True  if str(x).strip().upper() in ("TRUE","1","YES") else
                False if str(x).strip().upper() in ("FALSE","0","NO") else np.nan)

    if COL_STATUS1 in df.columns:
        df[COL_STATUS1] = df[COL_STATUS1].astype(str).str.strip()
        # 'N' төлвийг 'C' болгоно (хаалттай гэж үзнэ)
        df[COL_STATUS1] = df[COL_STATUS1].replace("N", "C")

    if COL_MAX_AOD in df.columns:
        df["bucket"] = pd.cut(df[COL_MAX_AOD].fillna(0),
            bins=BUCKET_BINS, labels=BUCKET_LBLS, right=True)

    if COL_DATE in df.columns:
        df["loan_ym"]   = df[COL_DATE].dt.to_period("M").astype(str)
        df["loan_year"] = df[COL_DATE].dt.year

    if COL_SCORE in df.columns:
        df["score_band"] = pd.cut(df[COL_SCORE],
            bins=[0,350,400,450,500,550,9999],
            labels=["<350","351–400","401–450","451–500","501–550","551+"], right=True)
    
    if "age" in df.columns:
        age_num = pd.to_numeric(df["age"], errors="coerce")
        df["age_group"] = pd.cut(age_num,
            bins=[0, 17, 18, 20, 25, 30, 35, 40, 99],
            labels=["17-оос бага", "18", "19–20", "21–25", "26–30", "31–35", "36–40", "40+"],
            right=True)

    # slry_has_cont_salary_3m → label
    if "slry_has_cont_salary_3m" in df.columns:
        df["slry_cont_label"] = pd.to_numeric(
            df["slry_has_cont_salary_3m"], errors="coerce"
        ).map({1:"Тасралтгүй 3 сар", 0:"Тасралттай"}).fillna("Мэдээлэл байхгүй")

    bool_maps = {
        "gender":             ("gender_label",   {True:"Эрэгтэй",   False:"Эмэгтэй"}),
        "has_ios":            ("ios_label",      {True:"iOS",        False:"Android"}),
        "is_bio_login":       ("bio_label",      {True:"Биометр",   False:"Нууц үг"}),
        "is_device_remember": ("dev_label",      {True:"Санасан",   False:"Санаагүй"}),
    }
    for src,(tgt,mp) in bool_maps.items():
        if src in df.columns:
            df[src] = df[src].map(lambda x:
                True  if str(x).strip().upper() in ("TRUE","1","YES") else
                False if str(x).strip().upper() in ("FALSE","0","NO") else np.nan)
            df[tgt] = df[src].map(mp)

    if "marital_status" in df.columns:
        df["marital_label"] = df["marital_status"].map(
            {"SNG":"Ганц бие","MRD":"Гэрлэсэн",
             "BGF":"Хамтран амьд.","DIV":"Салсан","WID":"Бэлэвсэн"}
        ).fillna("Тодорхойгүй")

    if "location" in df.columns:
        df["location_type"] = df["location"].apply(
            lambda x: "Улаанбаатар" if "УЛААНБААТАР" in str(x).upper() else "Орон нутаг")

    return df

# ── Customer-level builder ────────────────────────────────────────────────────
@st.cache_data(show_spinner=False)
def build_customer_df(df: pd.DataFrame) -> pd.DataFrame:
    if COL_CUST not in df.columns: return pd.DataFrame()
    grp = df.groupby(COL_CUST)

    # ── 1. Хэтрэлтийн үндсэн нэгтгэл ──────────────────────────────────────
    base = grp[COL_MAX_AOD].agg(
        max_overdue_day="max",
        avg_overdue_day="mean",
        total_loan_cnt ="count",
    ).reset_index()
    base["overdue_loan_cnt"] = grp[COL_MAX_AOD].apply(lambda x: (x > 0).sum()).values

    # ── 2. Зээлийн төлөвийн тоо ────────────────────────────────────────────
    if COL_STATUS1 in df.columns:
        base["closed_cnt"]   = grp[COL_STATUS1].apply(lambda x: (x == "C").sum()).values
        base["o_max_cnt"]    = grp[COL_STATUS1].apply(lambda x: (x == "O_max").sum()).values
        base["o_active_cnt"] = grp[COL_STATUS1].apply(lambda x: (x == "O_active").sum()).values
        base["status2"]      = grp[COL_STATUS1].apply(
            lambda x: 1 if (x == "O_active").any() else 0).values

    # ── 3. Зээлийн дүнгийн нэгтгэл ─────────────────────────────────────────
    if COL_AMT in df.columns:
        base["total_loan_amt"] = grp[COL_AMT].sum().values
        base["avg_loan_amt"]   = grp[COL_AMT].mean().values
        base["max_loan_amt"]   = grp[COL_AMT].max().values
        base["min_loan_amt"]   = grp[COL_AMT].min().values

    # ── 4. Оноогийн нэгтгэл ────────────────────────────────────────────────
    if COL_SCORE in df.columns:
        base["max_score"]  = grp[COL_SCORE].max().values
        base["min_score"]  = grp[COL_SCORE].min().values
        base["avg_score"]  = grp[COL_SCORE].mean().values

    # ── 5. Хязгаарын нэгтгэл ───────────────────────────────────────────────
    if "calc_lmt" in df.columns:
        lmt = pd.to_numeric(df["calc_lmt"], errors="coerce")
        df["calc_lmt_num"] = lmt
        base["max_calc_lmt"] = grp["calc_lmt_num"].max().values
        df.drop(columns=["calc_lmt_num"], inplace=True, errors="ignore")

    # ── 6. Идэвхтэй зээлийн тоо (ZMS) ─────────────────────────────────────
    if "zms_active_ln_cnt" in df.columns:
        base["zms_active_ln_cnt"] = grp["zms_active_ln_cnt"].max().values

    # ── 7. Хаагдсан зээлийн нийт дүн ──────────────────────────────────────
    if "zms_closed_ln_total_amount" in df.columns:
        base["zms_closed_ln_total_amount"] = grp["zms_closed_ln_total_amount"].max().values

    # ── 8. Сарын төлбөрийн нэгтгэл ─────────────────────────────────────────
    if "zms_monthly_payment" in df.columns:
        base["total_monthly_payment"] = grp["zms_monthly_payment"].sum().values
        base["avg_monthly_payment"]   = grp["zms_monthly_payment"].mean().values

    # ── 9. Харилцагчийн демо + цалингийн шинж чанар (first) ────────────────
    attr_cols = [c for c in CUST_ATTRS if c in df.columns]
    extra     = ["gender_label","ios_label","bio_label","dev_label","slry_cont_label",
                 "marital_label","location_type","age_group","score_band"]
    all_first = attr_cols + [c for c in extra if c in df.columns]
    if all_first:
        attrs = grp[list(dict.fromkeys(all_first))].first().reset_index()
        base  = base.merge(attrs, on=COL_CUST, how="left")

    # ── 10. Цалингийн тооцоолсон баганууд ──────────────────────────────────
    if "slry_last_amt" in base.columns and "total_monthly_payment" in base.columns:
        slry = pd.to_numeric(base["slry_last_amt"], errors="coerce")
        pmt  = pd.to_numeric(base["total_monthly_payment"], errors="coerce")
        # DTI (Debt-to-Income ratio): сарын нийт төлбөр / цалин
        base["dti_ratio"] = (pmt / slry.replace(0, np.nan)).round(3)

    if "slry_last_avg_6m" in base.columns:
        slry6 = pd.to_numeric(base["slry_last_avg_6m"], errors="coerce")
        if "total_loan_amt" in base.columns:
            # Зээл/цалин харьцаа: нийт зээл / 6 сарын дундаж цалин
            base["loan_to_salary_ratio"] = (
                pd.to_numeric(base["total_loan_amt"], errors="coerce") /
                slry6.replace(0, np.nan)
            ).round(2)

    # ── 11. Хэтрэлтийн ангилал ─────────────────────────────────────────────
    _OD_BINS = [-1, 0, 1, 5, 10, 15, 30, 9999]
    _OD_LBLS = ["0", "1", "2–5", "6–10", "11–15", "16–30", "30+"]
    base["overdue_band"]   = pd.cut(base["max_overdue_day"].astype(float),
        bins=_OD_BINS, labels=_OD_LBLS, right=True)
    base["overdue_status"] = base["overdue_band"].astype(str)
    base["has_overdue"]    = base["overdue_loan_cnt"] > 0

    return base

def _migrate_archive():
    """Хуучин архивыг preprocess хийж шинэчлэнэ (нэг удаа ажиллана)."""
    flag = ARCHIVE_DIR / ".migrated_v2"
    if flag.exists():
        return
    for f in ARCHIVE_DIR.glob("*.parquet"):
        try:
            df = pd.read_parquet(f)
            df.columns = df.columns.str.strip().str.lower()
            if "gender_label" not in df.columns:
                df = preprocess(df)
                df.to_parquet(f, index=False)
        except:
            pass
    flag.touch()

_migrate_archive()

# ── Excel export ───────────────────────────────────────────────────────────────
def to_excel(dfs: dict) -> bytes:
    buf = BytesIO()
    with pd.ExcelWriter(buf, engine="openpyxl") as w:
        for sheet,df in dfs.items():
            df.to_excel(w, sheet_name=sheet[:31], index=False)
    return buf.getvalue()

# ═════════════════════════════════════════════════════════════════════════════
# SIDEBAR
# ═════════════════════════════════════════════════════════════════════════════
with st.sidebar:
    st.markdown("## 📂 Өгөгдөл")
    st.markdown("---")

    # ── Upload ──
    st.markdown("**① Файл оруулах**")
    uploaded     = st.file_uploader("Excel / CSV", type=["xlsx","xls","csv"],
                                    label_visibility="collapsed")
    period_input = st.text_input("Он сар (жишээ: 2026-04)",
                                 value=datetime.now().strftime("%Y-%m"))

    if uploaded and st.button("💾 Хадгалах", type="primary", use_container_width=True):
        try:
            raw = (pd.read_csv(uploaded) if uploaded.name.endswith(".csv")
                   else pd.read_excel(uploaded))
            # Баганын нэрийг шалгахын өмнө lowercase болгоно
            raw.columns = raw.columns.str.strip().str.lower()
            missing = [c for c in [COL_STATUS1, COL_MAX_AOD] if c not in raw.columns]
            if missing:
                st.error(f"Дутуу багана: {', '.join(missing)} | Байгаа баганууд: {list(raw.columns)}")
            else:
                save_period(preprocess(raw), period_input, filename=uploaded.name)
                st.success(f"✓ {period_input} — {len(raw):,} данс")
                st.rerun()
        except Exception as e:
            st.error(f"Алдаа: {e}")

    st.markdown("---")

    # ── Period selector ──
    periods = list_periods()
    if not periods:
        st.info("Файл upload хийгээгүй байна.")
        st.stop()

    st.markdown("**② Үе сонгох**")
    MONTH_MN = {f"{i:02d}":f"{i}-р сар" for i in range(1,13)}
    def period_label(p):
        parts = p.split("-")
        m = MONTH_MN.get(parts[1], parts[1]) if len(parts)>=2 else p
        r = load_meta(p).get("rows","")
        return f"{m}  ({r:,} данс)" if r else m

    year_map = defaultdict(list)
    for p in periods:
        year_map[p.split("-")[0]].append(p)

    sel_year = st.selectbox("Он:", sorted(year_map.keys(), reverse=True),
                            label_visibility="collapsed")
    selected = st.selectbox("Сар:", sorted(year_map[sel_year], reverse=True),
                            format_func=period_label, label_visibility="collapsed")

    st.markdown("---")

    # ── Filters ──
    st.markdown("**③ Шүүлтүүр**")

    @st.cache_data
    def get_df(p):
        df = load_period(p)
        if 'gender_label' not in df.columns or 'age_group' not in df.columns:
            df = preprocess(df)
        return df

    df_raw = get_df(selected)

    # ── 1. Огноо ──────────────────────────────────────────────────────────
    if COL_DATE in df_raw.columns and df_raw[COL_DATE].notna().any():
        d_min = df_raw[COL_DATE].min().date()
        d_max = df_raw[COL_DATE].max().date()
        if d_min < d_max:
            dr = st.date_input("📅 Огноо", value=(d_min, d_max),
                               min_value=d_min, max_value=d_max)
            if isinstance(dr, (list, tuple)) and len(dr) == 2:
                df_raw = df_raw[df_raw[COL_DATE].dt.date.between(*dr)].copy()

    # ── 2. Нас ────────────────────────────────────────────────────────────
    if "age" in df_raw.columns and df_raw["age"].notna().any():
        _age = pd.to_numeric(df_raw["age"], errors="coerce")
        age_r = st.slider("👤 Нас", int(_age.min()), int(_age.max()),
                           (int(_age.min()), int(_age.max())))
    else:
        age_r = None

    # ── 3. Хугацаа хэтрэлт ────────────────────────────────────────────────
    if COL_MAX_AOD in df_raw.columns and df_raw[COL_MAX_AOD].notna().any():
        od_min, od_max = int(df_raw[COL_MAX_AOD].min()), int(df_raw[COL_MAX_AOD].max())
        od_r = st.slider("⏱️ Хугацаа хэтрэлт (хоног)", od_min, od_max, (od_min, od_max))
    else:
        od_r = None

    # ── 4. Жендэр ─────────────────────────────────────────────────────────
    g_opts = sorted(df_raw["gender_label"].dropna().unique()) if "gender_label" in df_raw.columns else []
    g_sel  = st.multiselect("⚥ Жендэр", g_opts, default=g_opts)

    # ── 5. Боловсрол ──────────────────────────────────────────────────────
    e_opts = sorted(df_raw["edu_name"].dropna().unique()) if "edu_name" in df_raw.columns else []
    e_sel  = st.multiselect("🎓 Боловсрол", e_opts, default=e_opts)

    # ── 6. Гэрлэлтийн байдал ──────────────────────────────────────────────
    m_opts = sorted(df_raw["marital_label"].dropna().unique()) if "marital_label" in df_raw.columns else []
    m_sel  = st.multiselect("💍 Гэрлэлтийн байдал", m_opts, default=m_opts)

    # ── 7. Байршил ────────────────────────────────────────────────────────
    lt_sel = st.radio("📍 Байршил", ["Бүгд", "Улаанбаатар", "Орон нутаг"],
                      horizontal=True)

    # ── 8. Төлөв ──────────────────────────────────────────────────────────
    s1_opts = sorted(df_raw[COL_STATUS1].dropna().unique()) if COL_STATUS1 in df_raw.columns else []
    s1_sel  = st.multiselect("🏷️ Төлөв", s1_opts, default=s1_opts)

    st.markdown("---")
    if st.button(f"🗑️ {selected} устгах", use_container_width=True):
        delete_period(selected); st.rerun()

    # ── Cache & migrate цэвэрлэх ──────────────────────────────────────────
    with st.expander("⚙️ Cache & дахин боловсруулах"):
        st.caption("Насны бүлэг эсвэл бусад derived баганууд өөрчлөгдсөн бол дарна уу.")
        if st.button("🔄 Бүх архивыг дахин боловсруулах", use_container_width=True):
            flag = ARCHIVE_DIR / ".migrated_v2"
            if flag.exists(): flag.unlink()
            for f in ARCHIVE_DIR.glob("*.parquet"):
                try:
                    df_m = pd.read_parquet(f)
                    df_m.columns = df_m.columns.str.strip().str.lower()
                    df_m = preprocess(df_m)
                    df_m.to_parquet(f, index=False)
                except: pass
            st.cache_data.clear()
            st.success("✓ Дахин боловсруулж дууслаа!")
            st.rerun()
        if st.button("🗑️ Бүх архив устгах", use_container_width=True):
            for f in list(ARCHIVE_DIR.glob("*.parquet")): f.unlink()
            for f in list(ARCHIVE_DIR.glob("*.json")):    f.unlink()
            for f in list(ARCHIVE_DIR.glob(".*")):        f.unlink()
            st.cache_data.clear()
            st.success("✓ Бүх архив устгагдлаа!")
            st.rerun()

# ── Apply filters ──────────────────────────────────────────────────────────────
has_cust     = COL_CUST in df_raw.columns
df_cust_full = build_customer_df(df_raw) if has_cust else pd.DataFrame()

# Loan-level шүүлтүүр
df_acct = df_raw.copy()
if s1_sel and COL_STATUS1 in df_acct.columns:
    df_acct = df_acct[df_acct[COL_STATUS1].isin(s1_sel)]
if g_sel and "gender_label" in df_acct.columns:
    df_acct = df_acct[df_acct["gender_label"].isin(g_sel)]
if age_r and "age" in df_acct.columns:
    df_acct = df_acct[pd.to_numeric(df_acct["age"], errors="coerce").between(*age_r)]
if m_sel and "marital_label" in df_acct.columns:
    df_acct = df_acct[df_acct["marital_label"].isin(m_sel)]
if e_sel and "edu_name" in df_acct.columns:
    df_acct = df_acct[df_acct["edu_name"].isin(e_sel)]
if lt_sel != "Бүгд" and "location_type" in df_acct.columns:
    df_acct = df_acct[df_acct["location_type"] == lt_sel]
if od_r and COL_MAX_AOD in df_acct.columns:
    df_acct = df_acct[df_acct[COL_MAX_AOD].between(*od_r)]

# Customer-level шүүлтүүр
df_cust = df_cust_full.copy() if has_cust else pd.DataFrame()
if not df_cust.empty:
    if s1_sel:
        if "O_active" in s1_sel and "status2" in df_cust.columns:
            pass
        elif set(s1_sel) == {"C"} and "status2" in df_cust.columns:
            df_cust = df_cust[df_cust["status2"] == 0]
    if g_sel and "gender_label" in df_cust.columns:
        df_cust = df_cust[df_cust["gender_label"].isin(g_sel)]
    if age_r and "age" in df_cust.columns:
        df_cust = df_cust[pd.to_numeric(df_cust["age"], errors="coerce").between(*age_r)]
    if m_sel and "marital_label" in df_cust.columns:
        df_cust = df_cust[df_cust["marital_label"].isin(m_sel)]
    if e_sel and "edu_name" in df_cust.columns:
        df_cust = df_cust[df_cust["edu_name"].isin(e_sel)]
    if lt_sel != "Бүгд" and "location_type" in df_cust.columns:
        df_cust = df_cust[df_cust["location_type"] == lt_sel]
    if od_r and "max_overdue_day" in df_cust.columns:
        df_cust = df_cust[df_cust["max_overdue_day"].between(*od_r)]

# ═════════════════════════════════════════════════════════════════════════════
# HEADER
# ═════════════════════════════════════════════════════════════════════════════
col_h1, col_h2 = st.columns([5,2])
with col_h1:
    st.markdown(f"## 📊 Хугацаа хэтрэлтийн шинжилгээ")
    st.caption(
        f"Үе: **{selected}**  |  "
        f"Данс: **{len(df_acct):,}** / {len(df_raw):,}  |  "
        f"Харилцагч: **{len(df_cust):,}** / {len(df_cust_full):,}"
    )
with col_h2:
    xl = to_excel({"loan_level":df_acct[
        [c for c in [COL_CUST,COL_DATE,COL_AMT,COL_STATUS1,
                     COL_SCORE,COL_MAX_OD,COL_MAX_AOD,"bucket"] if c in df_acct.columns]],
        "customer_level":df_cust})
    st.download_button("⬇️ Excel татах", data=xl,
        file_name=f"analysis_{selected}.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        use_container_width=True)

st.markdown("---")

# ═════════════════════════════════════════════════════════════════════════════
# TOP-LEVEL TABS
# ═════════════════════════════════════════════════════════════════════════════
TAB_LOAN, TAB_CUST = st.tabs(["🏦  Данс түвшин", "👤  Харилцагч түвшин"])

# ─────────────────────────────────────────────────────────────────────────────
# 🏦  ДАНС ТҮВШИН
# ─────────────────────────────────────────────────────────────────────────────
with TAB_LOAN:

    vc_all  = df_raw[COL_STATUS1].value_counts() if COL_STATUS1 in df_raw.columns else {}
    n_total = len(df_raw)
    n_C     = int(vc_all.get("C",0))
    n_omax  = int(vc_all.get("O_max",0))
    n_oact  = int(vc_all.get("O_active",0))
    n_open  = n_omax + n_oact

    # ── KPI row ──────────────────────────────────────────────────────────────
    # k1,k2,k3,k4,k5,k6 = st.columns(6)
    # k1.metric("Нийт данс",         f"{n_total:,}")
    # k2.metric("🟢 Хаалттай (C)",   f"{n_C:,}", f"{n_C/max(n_total,1)*100:.1f}%", delta_color="off")
    # k3.metric("🔵 Нээлттэй",       f"{n_open:,}", f"{n_open/max(n_total,1)*100:.1f}%", delta_color="off")
    # k4.metric("🔴 Идэвхтэй х.хэтрэлттэй",       f"{n_oact:,}", f"{n_oact/max(n_total,1)*100:.1f}%", delta_color="inverse")
    # oa_d = df_raw.loc[df_raw[COL_STATUS1]=="O_active", COL_MAX_AOD] if COL_STATUS1 in df_raw.columns and COL_MAX_AOD in df_raw.columns else pd.Series()
    # k5.metric("Дундаж хэтрэлт",    f"{oa_d.mean():.1f} хон." if len(oa_d) else "–")
    # k6.metric("30+ хоног",         f"{int((oa_d>=30).sum()):,}" if len(oa_d) else "–", delta_color="inverse")
    # st.markdown("---")
    oa_d = df_raw.loc[df_raw[COL_STATUS1]=="O_active", COL_MAX_AOD] if COL_STATUS1 in df_raw.columns and COL_MAX_AOD in df_raw.columns else pd.Series()
 
    # Харилцагчийн тоо
    _n_cust       = df_raw[COL_CUST].nunique()              if COL_CUST    in df_raw.columns else 0
    _n_cust_C     = df_raw[df_raw[COL_STATUS1]=="C"][COL_CUST].nunique()        if COL_STATUS1 in df_raw.columns and COL_CUST in df_raw.columns else 0
    _n_cust_open  = df_raw[df_raw[COL_STATUS1].isin(["O_max","O_active"])][COL_CUST].nunique() if COL_STATUS1 in df_raw.columns and COL_CUST in df_raw.columns else 0
    _n_cust_oact  = df_raw[df_raw[COL_STATUS1]=="O_active"][COL_CUST].nunique() if COL_STATUS1 in df_raw.columns and COL_CUST in df_raw.columns else 0
 
    # ── Эгнээ 1: Данс ──────────────────────────────────────────────────────
    st.markdown('<div style="font-size:12px;font-weight:600;color:#888;margin-bottom:4px;">📄 Дансны тоогоор</div>', unsafe_allow_html=True)
    k1,k2,k3,k4,k5,k6 = st.columns(6)
    k1.metric("Нийт данс",                f"{n_total:,}")
    k2.metric("🟢 Хаалттай (C)",          f"{n_C:,}",    f"{n_C/max(n_total,1)*100:.1f}%",    delta_color="off")
    k3.metric("🔵 Нээлттэй",              f"{n_open:,}", f"{n_open/max(n_total,1)*100:.1f}%",  delta_color="off")
    k4.metric("🔴 Идэвхтэй хэтрэлттэй",  f"{n_oact:,}", f"{n_oact/max(n_total,1)*100:.1f}%",  delta_color="off")
    k5.metric("30+ хоног",                f"{int((oa_d>30).sum()):,}" if len(oa_d) else "–", f"{(oa_d>30).sum()/max(n_total,1)*100:.1f}%" if len(oa_d) else None,  delta_color="off")
    k6.metric("Дундаж хэтрэлт",           f"{oa_d.mean():.1f} хон." if len(oa_d) else "–")

 
    # ── Эгнээ 2: Харилцагч ─────────────────────────────────────────────────
    st.markdown('<div style="font-size:12px;font-weight:600;color:#888;margin-bottom:4px;margin-top:8px;">👤 Харилцагчийн тоогоор</div>', unsafe_allow_html=True)
    c1,c2,c3,c4,c5,c6 = st.columns(6)
    c1.metric("Нийт харилцагч",           f"{_n_cust:,}")
    c2.metric("🟢 Хаалттай (C)",          f"{_n_cust_C:,}",    f"{_n_cust_C/max(_n_cust,1)*100:.1f}%",   delta_color="off")
    c3.metric("🔵 Нээлттэй",              f"{_n_cust_open:,}", f"{_n_cust_open/max(_n_cust,1)*100:.1f}%", delta_color="off")
    c4.metric("🔴 Идэвхтэй хэтрэлттэй",  f"{_n_cust_oact:,}", f"{_n_cust_oact/max(_n_cust,1)*100:.1f}%", delta_color="off")
    _oa_cust_od = df_raw[df_raw[COL_STATUS1]=="O_active"].groupby(COL_CUST)[COL_MAX_AOD].max() if COL_STATUS1 in df_raw.columns and COL_CUST in df_raw.columns and COL_MAX_AOD in df_raw.columns else pd.Series()
    c5.metric("30+ хоног",                f"{int((_oa_cust_od>30).sum()):,}" if len(_oa_cust_od) else "–", f"{(_oa_cust_od>30).sum()/max(_n_cust,1)*100:.1f}%" if len(_oa_cust_od) else None, delta_color="off")
    c6.metric("Дундаж хэтрэлт",           f"{_oa_cust_od.mean():.1f} хон." if len(_oa_cust_od) else "–")
    st.markdown("---")

    # ── SUB-SECTIONS ─────────────────────────────────────────────────────────
    L1, L2, L3, L4, L5 = st.tabs([
        "📋 Ерөнхий тойм",
        "⏱️ Хугацаа хэтрэлт",
        "🔍 Харилцагч хайх",
        "📅 Он сарын трэнд",
        "🗂️ Өгөгдөл",
    ])

    # ── L1: Ерөнхий тойм ──────────────────────────────────────────────────
    with L1:
        c1,c2 = st.columns(2)

        with c1:
            st.markdown('<div class="sh">Status_1 тархалт</div>', unsafe_allow_html=True)
            if COL_STATUS1 in df_acct.columns:
                sv = df_acct[COL_STATUS1].value_counts().reset_index()
                sv.columns = ["Төлөв","Тоо"]
                sv["Хувь"] = (sv["Тоо"]/sv["Тоо"].sum()*100).round(1)
                fig = px.bar(sv, x="Төлөв", y="Тоо", color="Төлөв",
                    color_discrete_map=CLR_STATUS,
                    text=sv.apply(lambda r:f"{r['Тоо']:,}\n({r['Хувь']}%)",axis=1))
                fig.update_traces(textposition="outside", textfont=dict(color="#111",size=12))
                L(fig, height=300, showlegend=False)
                st.plotly_chart(fig, use_container_width=True)

        with c2:
            st.markdown('<div class="sh">Зээл олгосон он сараар — зээлийн төлөв</div>', unsafe_allow_html=True)
            if "loan_ym" in df_acct.columns and COL_STATUS1 in df_acct.columns:
                ym = pd.crosstab(df_acct["loan_ym"], df_acct[COL_STATUS1]).reset_index()
                ym = ym.melt(id_vars="loan_ym", var_name="Төлөв", value_name="Тоо")
                fig2 = px.bar(ym, x="loan_ym", y="Тоо", color="Төлөв",
                    color_discrete_map=CLR_STATUS, barmode="stack")
                fig2.update_xaxes(tickangle=-40)
                L(fig2, height=300)
                st.plotly_chart(fig2, use_container_width=True)

        c3,c4 = st.columns(2)
        with c3:
            st.markdown('<div class="sh">Зээлийнм нийт дүн — зээлийн төлөв (box plot)</div>', unsafe_allow_html=True)
            if COL_AMT in df_acct.columns and COL_STATUS1 in df_acct.columns:
                fig3 = px.box(df_acct, x=COL_STATUS1, y=COL_AMT,
                    color=COL_STATUS1, color_discrete_map=CLR_STATUS)
                L(fig3, height=280, showlegend=False)
                st.plotly_chart(fig3, use_container_width=True)
        with c4:
            st.markdown('<div class="sh">Нэг харилцагчид ногдох зээлийн тоо</div>', unsafe_allow_html=True)
            if has_cust and COL_CUST in df_acct.columns and COL_STATUS1 in df_acct.columns:
                lc = df_acct.groupby(COL_CUST).size().reset_index()
                lc.columns=[COL_CUST,"Зээлийн тоо"]
                oa_cnt = (df_acct[df_acct[COL_STATUS1]=="O_active"]
                          .groupby(COL_CUST).size().reset_index())
                oa_cnt.columns=[COL_CUST,"OA"]
                lc  = lc.merge(oa_cnt, on=COL_CUST, how="left")
                lc["OA"] = lc["OA"].fillna(0).astype(int)
                grp = lc.groupby("Зээлийн тоо").agg(
                    Харилцагч    =("Зээлийн тоо","count"),
                    OA_харилцагч =("OA", lambda x:(x>0).sum())
                ).reset_index()
                grp["OA_%"] = (grp["OA_харилцагч"]/grp["Харилцагч"]*100).round(1)
                fig4 = go.Figure()
                # Нийт — цэнхэр, өргөн
                fig4.add_trace(go.Bar(
                    x=grp["Зээлийн тоо"], y=grp["Харилцагч"],
                    name="Нийт харилцагч",
                    marker=dict(color="#1a73e8", opacity=0.8, line=dict(width=0)),
                    width=0.7, yaxis="y1",
                ))
                # Идэвхтэй хэтрэлттэй — улаан, давхарласан
                fig4.add_trace(go.Bar(
                    x=grp["Зээлийн тоо"], y=grp["OA_харилцагч"],
                    name="Идэвхтэй хэтрэлттэй",
                    marker=dict(color="#e24b4a", opacity=0.85, line=dict(width=0)),
                    width=0.7, yaxis="y1",
                ))
                # Хэтрэлтийн % — шар шугам
                fig4.add_trace(go.Scatter(
                    x=grp["Зээлийн тоо"], y=grp["OA_%"],
                    name="Хэтрэлтийн %",
                    mode="lines+markers",
                    line=dict(color="#f59e0b", width=2.5),
                    marker=dict(size=8, color="#f59e0b",
                                line=dict(color="#fff", width=1.5)),
                    yaxis="y2",
                ))
                # Харилцагч 3-аас бага байгаа мөрийг хасна
                grp = grp[grp["Харилцагч"] >= 3].copy()
 
                fig4 = go.Figure()
                fig4.add_trace(go.Bar(
                    x=grp["Зээлийн тоо"], y=grp["Харилцагч"],
                    name="Нийт харилцагч",
                    marker=dict(color="#1a73e8", opacity=0.8, line=dict(width=0)),
                    width=0.7, yaxis="y1",
                ))
                fig4.add_trace(go.Bar(
                    x=grp["Зээлийн тоо"], y=grp["OA_харилцагч"],
                    name="Идэвхтэй хэтрэлттэй",
                    marker=dict(color="#e24b4a", opacity=0.85, line=dict(width=0)),
                    width=0.7, yaxis="y1",
                ))
                fig4.add_trace(go.Scatter(
                    x=grp["Зээлийн тоо"], y=grp["OA_%"],
                    name="Хэтрэлтийн %",
                    mode="lines+markers",
                    line=dict(color="#f59e0b", width=2.5),
                    marker=dict(size=8, color="#f59e0b",
                                line=dict(color="#fff", width=1.5)),
                    yaxis="y2",
                ))
                L(fig4, height=340,
                  barmode="overlay",
                  xaxis=dict(**AXIS,
                      title="Зээлийн тоо (нэг харилцагчид)",
                      tickmode="array",
                      tickvals=grp["Зээлийн тоо"].tolist(),
                      ticktext=[str(v) for v in grp["Зээлийн тоо"].tolist()],
                  ),
                  yaxis=dict(**AXIS, title="Харилцагчийн тоо"),
                  yaxis2=dict(
                      overlaying="y", side="right",
                      title="Хэтрэлтийн %",
                      ticksuffix="%",
                      tickfont=dict(color="#f59e0b", size=11),
                      title_font=dict(color="#f59e0b", size=12),
                      gridcolor="rgba(0,0,0,0)",
                      range=[0, min(grp["OA_%"].max()*2.5, 100)],
                  ),
                  legend=dict(
                      font=dict(color="#111", size=11),
                      bgcolor="rgba(255,255,255,0.9)",
                      bordercolor="#ddd", borderwidth=1,
                      x=0.99, xanchor="right",
                      y=0.99, yanchor="top",
                  ),
                  margin=dict(l=10, r=70, t=32, b=8),
                )
                st.plotly_chart(fig4, use_container_width=True)
        # Summary table
        st.markdown('<div class="sh">Зээлийн төлвөөр нэгтгэсэн хүснэгт</div>', unsafe_allow_html=True)
        rows=[]
        for s in ["C","O_max","O_active"]:
            sub = df_acct[df_acct[COL_STATUS1]==s] if COL_STATUS1 in df_acct.columns else pd.DataFrame()
            row={"Төлөв":s,"Данс":len(sub),"Хувь (%)":round(len(sub)/max(n_total,1)*100,1)}
            if COL_AMT in sub.columns:
                row["Нийт дүн (₮)"]=sub[COL_AMT].sum()
                row["Дундаж дүн"]=round(sub[COL_AMT].mean(),0)
            if COL_MAX_AOD in sub.columns:
                row["Дундаж хэтрэлт"]=round(sub[COL_MAX_AOD].mean(),1)
            rows.append(row)
        st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)

    # ── L2: Хугацаа хэтрэлт ───────────────────────────────────────────────
    with L2:
        oa = df_acct[df_acct[COL_STATUS1]=="O_active"].copy() if COL_STATUS1 in df_acct.columns else df_acct.copy()
        _oad = oa[COL_MAX_AOD] if COL_MAX_AOD in oa.columns else pd.Series()

        # KPI
        b1,b2,b3,b4 = st.columns(4)
        b1.metric("Идэвхтэй х.хэтэрсэн данс", f"{len(oa):,}")
        b2.metric("Дундаж хэтрэлт", f"{_oad.mean():.1f} хон." if len(_oad) else "–")
        b3.metric("Медиан", f"{_oad.median():.0f} хон." if len(_oad) else "–")
        b4.metric("Хамгийн их", f"{int(_oad.max())} хон." if len(_oad) else "–")

        bk1 = st.columns(6)
        for i,(lbl,lo,hi) in enumerate([("1 хоног",1,1),("2–5",2,5),("6–10",6,10),
                                         ("11–15",11,15),("16–30",16,30),("30+",31,9999)]):
            _n = int(_oad.between(lo,hi).sum()) if len(_oad) else 0
            bk1[i].metric(lbl, f"{_n:,}", f"{_n/max(n_total,1)*100:.1f}%", delta_color="off")
        st.markdown("---")

        c1,c2 = st.columns(2)
        with c1:
            st.markdown('<div class="sh">Хэтрэлтийн хоногийн тархалт (Идэвхтэй хугацаа хэтрэлт)</div>', unsafe_allow_html=True)
            if len(_oad):
                fig = px.histogram(oa, x=COL_MAX_AOD, nbins=31,
                    color_discrete_sequence=["#e24b4a"])
                fig.add_vline(x=30, line_dash="dash", line_color="#888",
                    annotation_text="30 хоног")
                L(fig, height=300, showlegend=False)
                st.plotly_chart(fig, use_container_width=True)

        with c2:
            st.markdown('<div class="sh">Эрсдэлийн оноо × Хугацаа хэтрэлт (scatter)</div>', unsafe_allow_html=True)
            st.markdown('<div class="sh">Шугаман трэнд:</b> Хоёр хувьсагчийн хоорондын шугаман хамаарлыг харуулна.</div>', unsafe_allow_html=True)
            if COL_SCORE in oa.columns and COL_MAX_AOD in oa.columns:
                fig2 = px.scatter(oa, x=COL_SCORE, y=COL_MAX_AOD,
                    color="bucket" if "bucket" in oa.columns else None,
                    color_discrete_sequence=CLR_BUCKET,
                    opacity=0.55, trendline="ols",
                    labels={COL_SCORE:"Эрсдэлийн оноо",
                            COL_MAX_AOD:"Идэвхтэй хэтрэлт (хоног)",
                            "bucket":"Хэтрэлтийн бүс"})
                corr = oa[[COL_SCORE,COL_MAX_AOD]].dropna().corr().iloc[0,1]
                L(fig2, height=300)
                st.plotly_chart(fig2, use_container_width=True)
 
                # Корреляцын тайлбар
                if corr > 0.1:
                    corr_msg = f"Оноо өндөр байсан ч хугацаа хэтрэлт ихэссэн хандлага ажиглагдаж байна — оноолтын загвар хэтрэлтийг хангалттай ялгаж чадахгүй байж болзошгүй."
                    corr_box = "box box-warn"
                elif corr < -0.1:
                    corr_msg = f"Оноо бага байсан харилцагчид илүү их хэтэрч байна — оноолтын загвар хэтрэлтийг зөв таньж байна."
                    corr_box = "box box-green"
                else:
                    corr_msg = f"Оноо болон хэтрэлтийн хоорондын хамаарал маш сул байна — оноо дангаараа хэтрэлтийг тайлбарлах чадвар хязгаарлагдмал."
                    corr_box = "box box-blue"
 
                # st.markdown(
                #     f'''<div class="{corr_box}">
                #     📌 <b>Шугаман трэнд:</b> хоёр хувьсагчийн хоорондын шугаман хамаарлыг харуулна.<br>
                #     📊 <b>Корреляц: {corr:+.3f}</b> — {corr_msg}
                #     </div>''',
                #     unsafe_allow_html=True
                # )
                st.caption(f"Корреляц: **{corr:+.3f}** — {corr_msg}")
        c3,c4 = st.columns(2)
        # with c3:
        #     st.markdown('<div class="sh">Оноогоор — Идэвхтэй хугацаа хэтэрсэн зээлийн тоо</div>', unsafe_allow_html=True)
        #     if "score_band" in oa.columns:
        #         sb = oa["score_band"].value_counts().sort_index().reset_index()
        #         sb.columns = ["Бүс", "Тоо"]
        #         fig3 = px.bar(sb, x="Бүс", y="Тоо", color="Тоо",
        #             color_continuous_scale=["#aac8f5","#e24b4a"], text="Тоо")
        #         fig3.update_traces(textposition="outside")
        #         fig3.update_coloraxes(showscale=False)
        #         L(fig3, height=280, showlegend=False)
        #         st.plotly_chart(fig3, use_container_width=True)
        with c3:
            st.markdown('<div class="sh">Оноогийн бүсээр — O_active тоо & rate</div>', unsafe_allow_html=True)
            if "score_band" in oa.columns and "score_band" in df_acct.columns:
                sb_oa  = oa["score_band"].value_counts().sort_index().reset_index()
                sb_oa.columns = ["Бүс", "O_active тоо"]
                sb_all = df_acct["score_band"].value_counts().sort_index().reset_index()
                sb_all.columns = ["Бүс", "Нийт"]
                sb = sb_oa.merge(sb_all, on="Бүс", how="left")
                sb["Rate %"] = (sb["O_active тоо"] / sb["Нийт"] * 100).round(1)
 
                fig3 = go.Figure()
                fig3.add_trace(go.Bar(
                    x=sb["Бүс"].astype(str), y=sb["O_active тоо"],
                    name="O_active тоо",
                    marker=dict(color=sb["O_active тоо"],
                        colorscale=[[0,"#aac8f5"],[1,"#e24b4a"]], showscale=False),
                    yaxis="y1",
                ))
                fig3.add_trace(go.Scatter(
                    x=sb["Бүс"].astype(str), y=sb["Rate %"],
                    name="O_active rate %",
                    mode="lines+markers+text",
                    line=dict(color="#e24b4a", width=2.5),
                    marker=dict(size=8, color="#e24b4a",
                                line=dict(color="#fff", width=1.5)),
                    text=sb["Rate %"].astype(str) + "%",
                    textposition="top center",
                    textfont=dict(color="#e24b4a", size=11),
                    yaxis="y2",
                ))
                L(fig3, height=300,
                  xaxis=dict(**AXIS, title="Оноогийн бүс", tickangle=-20),
                  yaxis=dict(**AXIS, title="O_active дансны тоо"),
                  yaxis2=dict(
                      overlaying="y", side="right",
                      title="O_active rate %",
                      ticksuffix="%",
                      tickfont=dict(color="#e24b4a", size=11),
                      title_font=dict(color="#e24b4a", size=12),
                      gridcolor="rgba(0,0,0,0)",
                      range=[0, min(sb["Rate %"].max()*2.5, 100)],
                  ),
                  legend=dict(
                      font=dict(color="#111", size=11),
                      bgcolor="rgba(255,255,255,0.9)",
                      bordercolor="#ddd", borderwidth=1,
                      x=0.99, xanchor="right", y=0.99, yanchor="top",
                  ),
                  margin=dict(l=10, r=70, t=32, b=8),
                )
                st.plotly_chart(fig3, use_container_width=True)

        with c4:
            st.markdown('<div class="sh">Нийт хэтрэлт vs Идэвхтэй хэтрэлт</div>', unsafe_allow_html=True)
            if COL_MAX_OD in oa.columns and COL_MAX_AOD in oa.columns:
                fig4 = go.Figure()
                fig4.add_trace(go.Histogram(x=oa[COL_MAX_OD], name="Нийт (max_overdue)",
                    opacity=0.5, marker_color="#f59e0b", nbinsx=31))
                fig4.add_trace(go.Histogram(x=oa[COL_MAX_AOD], name="Идэвхтэй",
                    opacity=0.7, marker_color="#e24b4a", nbinsx=31))
                L(fig4, height=280, barmode="overlay")
                st.plotly_chart(fig4, use_container_width=True)

        # 25+ жагсаалт
        st.markdown("---")
        thr = st.slider("Яаралтай жагсаалт — хязгаар (хоног)", 20, 31, 25, key="thr_loan")
        oa25 = oa[oa[COL_MAX_AOD]>=thr] if COL_MAX_AOD in oa.columns else pd.DataFrame()
        if len(oa25):
            st.markdown(f'<div class="box box-danger">🚨 <b>{thr}+</b> хоног: <b>{len(oa25):,}</b> данс ({len(oa25)/max(len(oa),1)*100:.1f}%)</div>',unsafe_allow_html=True)
            show = {k:v for k,v in {COL_CUST:"Харилцагч",COL_DATE:"Огноо",
                COL_AMT:"Дүн",COL_MAX_AOD:"Хэтрэлт",COL_SCORE:"Оноо"}.items() if k in oa25.columns}
            st.dataframe(oa25[list(show.keys())].rename(columns=show)
                .sort_values("Хэтрэлт",ascending=False).reset_index(drop=True),
                use_container_width=True, height=320)
            st.download_button("📥 Татах", oa25.to_csv(index=False).encode("utf-8-sig"),
                f"urgent_{thr}plus.csv","text/csv")

    # ── L3: Харилцагч хайх ────────────────────────────────────────────────
    with L3:
        if not has_cust:
            st.warning(f"'{COL_CUST}' багана байхгүй.")
        else:
            # ── Харилцагчийн жагсаалт: зээлийн тоогоор буурах эрэмбэ ──────
            @st.cache_data
            def build_cust_options(p):
                """Зээлийн тоо + MAX хэтрэлт + төлөв хамт харуулсан dropdown жагсаалт"""
                d = load_period(p)
                if "gender_label" not in d.columns:
                    d = preprocess(d)
                if COL_CUST not in d.columns:
                    return [], {}
                grp = d.groupby(COL_CUST)
                info = grp.agg(
                    loan_cnt=(COL_CUST, "count"),
                    max_od=(COL_MAX_AOD, "max") if COL_MAX_AOD in d.columns else (COL_CUST, "count"),
                ).reset_index()
                if COL_STATUS1 in d.columns:
                    info["has_oa"] = grp[COL_STATUS1].apply(
                        lambda x: "🔴" if (x == "O_active").any()
                        else ("🟡" if (x == "O_max").any() else "🟢")
                    ).values
                else:
                    info["has_oa"] = "–"
                # Зээлийн тоогоор буурах, хэтрэлтээр буурах эрэмбэлэлт
                info = info.sort_values(["loan_cnt", "max_od"], ascending=[False, False])
                # Dropdown-д харуулах label: "2604087942 — 10 зээл | 🔴 | MAX:25хон"
                od_col = "max_od" if "max_od" in info.columns else None
                labels = []
                for _, r in info.iterrows():
                    od_str = f" | MAX:{int(r['max_od'])}хон" if od_col and r["max_od"] > 0 else ""
                    labels.append(
                        f"{r[COL_CUST]}  —  {int(r['loan_cnt'])} зээл  {r['has_oa']}{od_str}"
                    )
                code_map = {lbl: str(r[COL_CUST]) for lbl, (_, r) in zip(labels, info.iterrows())}
                return labels, code_map

            labels, code_map = build_cust_options(selected)

            if not labels:
                st.warning("Харилцагч олдсонгүй.")
            else:
                col_sel, col_info = st.columns([3, 1])
                with col_sel:
                    chosen_lbl = st.selectbox(
                        f"Харилцагч сонгох ({len(labels):,} харилцагч — зээлийн тоогоор эрэмблэсэн):",
                        options=labels,
                        index=0,
                    )
                with col_info:
                    st.markdown("<br>", unsafe_allow_html=True)
                    st.caption(f"Нийт **{len(labels):,}** харилцагч")

                selected_code = code_map.get(chosen_lbl, "")
                rows_ = df_raw[df_raw[COL_CUST].astype(str).str.strip() == selected_code]

                if len(rows_) == 0:
                    st.warning("Олдсонгүй.")
                else:
                    vc2 = rows_[COL_STATUS1].value_counts() if COL_STATUS1 in rows_.columns else {}
                    c1, c2, c3, c4, c5 = st.columns(5)
                    c1.metric("Нийт зээл", len(rows_))
                    c2.metric("C", int(vc2.get("C", 0)))
                    c3.metric("O_max", int(vc2.get("O_max", 0)))
                    c4.metric("O_active", int(vc2.get("O_active", 0)))
                    c5.metric("MAX хэтрэлт",
                        f"{int(rows_[COL_MAX_AOD].max())} хон." if COL_MAX_AOD in rows_.columns else "–")

                    show = {k: v for k, v in {
                        COL_DATE: "Огноо", COL_AMT: "Дүн",
                        COL_STATUS1: "Төлөв", COL_SCORE: "Оноо",
                        COL_MAX_AOD: "Идэвхтэй хэтрэлт", "bucket": "Bucket",
                    }.items() if k in rows_.columns}
                    st.dataframe(
                        rows_[list(show.keys())].rename(columns=show)
                            .sort_values("Огноо" if "Огноо" in show.values() else list(show.values())[0])
                            .reset_index(drop=True),
                        use_container_width=True, height=280,
                    )

                    if COL_DATE in rows_.columns and COL_MAX_AOD in rows_.columns:
                        rs = rows_.sort_values(COL_DATE).copy()
                        rs["lbl"] = rs[COL_DATE].dt.strftime("%Y-%m-%d")
                        fig = px.bar(rs, x="lbl", y=COL_MAX_AOD,
                            color=COL_STATUS1 if COL_STATUS1 in rs.columns else None,
                            color_discrete_map=CLR_STATUS, text=COL_MAX_AOD,
                            labels={"lbl": "Авсан огноо", COL_MAX_AOD: "Хэтрэлт (хоног)"})
                        fig.add_hline(y=25, line_dash="dash", line_color="#888",
                            annotation_text="25 хоног", annotation_font=dict(color="#888", size=11))
                        fig.update_traces(textposition="outside", textfont=dict(color="#111", size=12))
                        L(fig, height=300)
                        st.plotly_chart(fig, use_container_width=True)

    # ── L4: Он сарын трэнд ────────────────────────────────────────────────
    with L4:
        all_p = list_periods()
        if len(all_p) < 2:
            st.info("2+ үе хадгалагдсан байх шаардлагатай.")
        else:
            rows=[]
            for p in reversed(all_p):
                try:
                    dp = load_period(p)
                    s1 = dp[COL_STATUS1].value_counts() if COL_STATUS1 in dp.columns else {}
                    n  = len(dp)
                    oad= dp.loc[dp[COL_STATUS1]=="O_active",COL_MAX_AOD] if COL_STATUS1 in dp.columns and COL_MAX_AOD in dp.columns else pd.Series()
                    rows.append({"Он сар":p,"Нийт данс":n,
                        "C":int(s1.get("C",0)),"O_max":int(s1.get("O_max",0)),
                        "O_active":int(s1.get("O_active",0)),
                        "O_active %":round(s1.get("O_active",0)/max(n,1)*100,1),
                        "Дундаж хэтрэлт":round(oad.mean(),2) if len(oad) else 0})
                except: pass
            tdf = pd.DataFrame(rows)

            # KPI delta
            if len(tdf)>=2:
                cur,prev = tdf.iloc[-1], tdf.iloc[-2]
                d1,d2,d3 = st.columns(3)
                d1.metric("Энэ үеийн O_active", f"{cur['O_active']:,}")
                d2.metric("Өмнөх үетэй зөрүү",
                    f"{cur['O_active']-prev['O_active']:+,}", delta_color="inverse")
                d3.metric("O_active % зөрүү",
                    f"{cur['O_active %']-prev['O_active %']:+.1f}%", delta_color="inverse")
                st.markdown("---")

            if len(tdf)>=2:
                fig = go.Figure()
                fig.add_trace(go.Bar(x=tdf["Он сар"], y=tdf["O_active"],
                    name="O_active тоо", marker_color="rgba(226,75,74,.2)", yaxis="y2"))
                fig.add_trace(go.Scatter(x=tdf["Он сар"], y=tdf["O_active %"],
                    name="O_active %", mode="lines+markers+text",
                    line=dict(color="#e24b4a",width=2.5), marker=dict(size=9),
                    text=tdf["O_active %"].astype(str)+"%",
                    textposition="top center", textfont=dict(color="#e24b4a",size=11)))
                L(fig, height=360,
                  yaxis=dict(**AXIS,title="O_active %"),
                  yaxis2=dict(overlaying="y",side="right",title="Тоо",
                              tickfont=dict(color="#bbb",size=10),gridcolor="rgba(0,0,0,0)"))
                st.plotly_chart(fig, use_container_width=True)
            st.dataframe(tdf, use_container_width=True, height=240)
            st.download_button("📥 Трэнд татах", tdf.to_csv(index=False).encode("utf-8-sig"),
                "trend.csv","text/csv")

    # ── L5: Өгөгдөл ───────────────────────────────────────────────────────
    with L5:
        quick = st.radio("", ["Бүгд","O_active","O_max","C"], horizontal=True)
        show_ = df_acct[df_acct[COL_STATUS1]==quick].copy() if quick!="Бүгд" and COL_STATUS1 in df_acct.columns else df_acct.copy()
        st.caption(f"{len(show_):,} данс")
        dcols={k:v for k,v in {COL_CUST:"Харилцагч",COL_DATE:"Огноо",
            COL_AMT:"Дүн",COL_STATUS1:"Төлөв",COL_SCORE:"Оноо",
            COL_MAX_AOD:"Хэтрэлт","bucket":"Bucket"}.items() if k in show_.columns}
        st.dataframe(show_[list(dcols.keys())].rename(columns=dcols)
            .sort_values("Хэтрэлт" if "Хэтрэлт" in dcols.values() else list(dcols.values())[0], ascending=False)
            .reset_index(drop=True), use_container_width=True, height=500)
        st.download_button("📥 CSV татах", show_.to_csv(index=False).encode("utf-8-sig"),
            f"loan_{quick}_{selected}.csv","text/csv")


# ─────────────────────────────────────────────────────────────────────────────
# 👤  ХАРИЛЦАГЧ ТҮВШИН
# ─────────────────────────────────────────────────────────────────────────────
with TAB_CUST:
    if not has_cust or df_cust.empty:
        st.error(f"'{COL_CUST}' багана байхгүй / дата хоосон.")
        st.stop()

    OD = "max_overdue_day"
    od_s = df_cust[OD] if OD in df_cust.columns else pd.Series()
    n_tot = len(df_cust)

    # ── KPI row ──────────────────────────────────────────────────────────────
    st.markdown("---")
    if "total_loan_amt" in df_cust.columns:
        ka,kb,kc, kd = st.columns(4)
        ka.metric("Нийт зээлийн дүн", f"₮{df_cust['total_loan_amt'].sum()/1e9:.2f} тэрбум")
        kb.metric("Дундаж дүн/хүн",   f"₮{df_cust['total_loan_amt'].mean()/1e6:.1f} сая")
        kc.metric("Олон зээлтэй (+1)",
            f"{int((df_cust['total_loan_cnt']>1).sum()):,}" if "total_loan_cnt" in df_cust.columns else "–")
        kd.metric("Дундаж зээл/хүн",
        f"{df_cust['total_loan_cnt'].mean():.1f}" if "total_loan_cnt" in df_cust.columns else "–")

    k1,k2,k3,k4 = st.columns(4)
    k1.metric("Нийт харилцагч",    f"{n_tot:,}")
    k2.metric("Хэтрэлттэй",
        f"{df_cust['has_overdue'].sum():,}" if "has_overdue" in df_cust.columns else "–",
        f"{df_cust['has_overdue'].mean()*100:.1f}%" if "has_overdue" in df_cust.columns else None,
        delta_color="off")
    k3.metric("Дундаж MAX хэтрэлт", f"{od_s.mean():.1f} хон." if len(od_s) else "–")
    # k4.metric("30+ хоног (MAX)",   f"{int((od_s>=30).sum()):,}" if len(od_s) else "–", f"{df_cust['has_overdue'].mean()*100:.1f}%" if "has_overdue" in df_cust.columns else None, delta_color="off")
    k4.metric("30+ хоног (MAX)",   f"{int((od_s>30).sum()):,}" if len(od_s) else "–", f"{int((od_s>30).sum())/max(n_tot,1)*100:.1f}%" if len(od_s) else None, delta_color="off")
    
    # ── SUB-SECTIONS ─────────────────────────────────────────────────────────
    C1, C3, C6, C7, C8, C9, C10 = st.tabs([
        "📈 Тархалт",
        # "👤 Нас & Жендэр",
        "🏷️ Категори",
        # "🔗 Олон зээлийн шинжилгээ",
        # "⚠️ 25+ хоног",
        "💰 Цалингийн шинжилгээ",
        "🏷️ Зээлийн дүн & DTI",
        "🎯 Score шинжилгээ",
        "📊 Корреляц & scatter",
        "🗂️ Өгөгдөл",
    ])

    # ── C1: Тархалт ───────────────────────────────────────────────────────
    with C1:
        OD = "max_overdue_day" 
         # ── Bucket KPI ───────────────────────────────────────────────────────
        _od_cust = df_cust[OD] if OD in df_cust.columns else pd.Series()
        bk_c = st.columns(7)
        bk_c[0].metric("Хэвийн (0)",
            f"{int((_od_cust==0).sum()):,}" if len(_od_cust) else "–",
            f"{(_od_cust==0).sum()/max(n_tot,1)*100:.1f}%", delta_color="off")
        for i,(lbl,lo,hi) in enumerate([("1",1,1),("2–5",2,5),("6–10",6,10),
                                         ("11–15",11,15),("16–30",16,30),("30+",31,9999)]):
            _n = int(_od_cust.between(lo,hi).sum()) if len(_od_cust) else 0
            bk_c[i+1].metric(lbl, f"{_n:,}",
                f"{_n/max(n_tot,1)*100:.1f}%", delta_color="off")
        st.markdown("---")
        c1,c2 = st.columns(2)
        with c1:
            st.markdown('<div class="sh">MAX хэтрэлт — гистограм</div>', unsafe_allow_html=True)
            fig = px.histogram(df_cust, x=OD, nbins=32, color_discrete_sequence=["#1d9e75"])
            fig.add_vline(x=30, line_dash="dash", line_color="#e24b4a",
                annotation_text="30 хоног", annotation_font=dict(color="#e24b4a"))
            L(fig, height=280, showlegend=False)
            st.plotly_chart(fig, use_container_width=True)

        with c2:
            st.markdown('<div class="sh">Зээлийн тоо ба MAX хэтрэлт</div>', unsafe_allow_html=True)
            if "total_loan_cnt" in df_cust.columns:
                fig4 = px.scatter(df_cust, x="total_loan_cnt", y=OD,
                    color="overdue_status" if "overdue_status" in df_cust.columns else None,
                    color_discrete_sequence=["#1d9e75","#F5A623","#E8813A","#E24B4A"],
                    opacity=0.55, trendline="ols",
                    labels={"total_loan_cnt":"Зээлийн тоо", OD:"MAX хэтрэлт (хоног)",
                            "overdue_status":"Хэтрэлтийн байдал"})
                L(fig4, height=280)
                st.plotly_chart(fig4, use_container_width=True)
 
                # Корреляц + тайлбар
                _corr4 = df_cust[["total_loan_cnt", OD]].dropna().corr().iloc[0,1]
                if _corr4 < -0.05:
                    _msg4 = "Зээлийн тоо нэмэгдэхэд хэтрэлт буурах хандлагатай — олон зээлтэй харилцагчид харилцангуй хариуцлагатай байна."
                    _box4 = "box box-green"
                elif _corr4 > 0.05:
                    _msg4 = "Зээлийн тоо нэмэгдэхэд хэтрэлт нэмэгдэх хандлагатай — олон зээлтэй харилцагчид санхүүгийн дарамттай байж болзошгүй."
                    _box4 = "box box-warn"
                else:
                    _msg4 = "Зээлийн тоо болон хэтрэлтийн хоорондын шугаман хамаарал бараг байхгүй байна."
                    _box4 = "box box-blue"
                st.markdown(
                    f'<div class="{_box4}">📊 <b>Корреляц: {_corr4:+.3f}</b> — {_msg4}</div>',
                    unsafe_allow_html=True)
        st.markdown('<div class="sh">Зээлийн тооноор нэгтгэсэн хүснэгт</div>', unsafe_allow_html=True)
        seg = df_cust.groupby("total_loan_cnt").agg(
            Харилцагч=("total_loan_cnt","count"),
                Дундаж_MAX=(OD,"mean"),
                Медиан=(OD,"median"),
                Хэтэрсэн=("has_overdue","sum"),
            ).reset_index().rename(columns={"total_loan_cnt":"Зээлийн тоо"})
        seg["Хэтрэлт %"]=(seg["Хэтэрсэн"]/seg["Харилцагч"]*100).round(1)
        seg["Дундаж_MAX"]=seg["Дундаж_MAX"].round(1)
        st.dataframe(seg, use_container_width=True, height=260)
    with C3:

        st.markdown('<div class="sh">Насны бүлгээр — хэтрэлтийн байдал %</div>', unsafe_allow_html=True)
        if "overdue_status" in df_cust.columns:
                    cr = pd.crosstab(df_cust["age_group"],df_cust["overdue_status"],normalize="index")*100
                    cr = cr.reset_index().melt(id_vars="age_group",var_name="Байдал",value_name="Хувь")
                    fig2 = px.bar(cr, x="age_group", y="Хувь", color="Байдал",
                        color_discrete_sequence=["#1d9e75","#F5A623","#E8813A","#E24B4A"])
                    L(fig2, height=300, barmode="stack")
                    st.plotly_chart(fig2, use_container_width=True)


        OD = "max_overdue_day"

        # ── Dual-axis chart helper ────────────────────────────────────────────
        def dual_bar(col, title, h=300, min_cnt=3):
            """
            Баганан диаграм: дундаж хэтрэлт (хоног) — зүүн тэнхлэг
            Шугаман диаграм: хэтрэлтийн rate %    — баруун тэнхлэг
            Дундаж хоногоор буурах эрэмбэ
            """
            if col not in df_cust.columns: return None
            if "has_overdue" not in df_cust.columns: return None

            d = df_cust.groupby(col, observed=True).agg(
                нийт   =(col,          "count"),
                дундаж =(OD,           "mean"),
                хэтэрсэн=("has_overdue","sum"),
            ).reset_index()
            d = d[d["нийт"] >= min_cnt].copy()
            d["rate"]   = (d["хэтэрсэн"] / d["нийт"] * 100).round(1)
            d["дундаж"] = d["дундаж"].round(2)
            d = d.sort_values("дундаж")           # дундаж хоногоор эрэмбэ

            cats = d[col].astype(str).tolist()
            fig = go.Figure()

            # ── Bar: дундаж хоног ─────────────────────────────────────────────
            bar_colors = [
                f"rgba({int(26 + (226-26)*v)},{int(115 + (75-115)*v)},{int(232 + (74-232)*v)},0.82)"
                for v in [x/max(d["дундаж"].max(),1) for x in d["дундаж"]]
            ]
            fig.add_trace(go.Bar(
                x=cats, y=d["дундаж"],
                name="Дундаж хоног",
                marker_color=bar_colors,
                text=d["дундаж"].round(1),
                textposition="outside",
                textfont=dict(color="#111", size=11),
                yaxis="y1",
            ))

            # ── Line: хэтрэлтийн rate % ───────────────────────────────────────
            fig.add_trace(go.Scatter(
                x=cats, y=d["rate"],
                name="Хэтрэлтийн rate %",
                mode="lines+markers+text",
                line=dict(color="#e24b4a", width=2.5),
                marker=dict(size=8, color="#e24b4a",
                            line=dict(color="#fff", width=1.5)),
                text=d["rate"].astype(str) + "%",
                textposition="top center",
                textfont=dict(color="#e24b4a", size=11),
                yaxis="y2",
            ))

            L(fig, height=h,
              xaxis=dict(**{**AXIS, "tickfont": dict(color="#111", size=11)},
                         tickangle=-30, automargin=True),
              yaxis=dict(**AXIS, title="Дундаж хоног"),
              yaxis2=dict(
                  overlaying="y", side="right",
                  title="Хэтрэлтийн rate %",
                  ticksuffix="%",
                  tickfont=dict(color="#e24b4a", size=11),
                  title_font=dict(color="#e24b4a", size=12),
                  gridcolor="rgba(0,0,0,0)",
                  range=[0, min(d["rate"].max() * 2, 100)],
              ),
              legend=dict(
                  font=dict(color="#111",size=11),
                  bgcolor="rgba(255,255,255,0.88)",
                  bordercolor="#ddd", borderwidth=1,
                  orientation="v",
                  x=0.01, xanchor="left",
                  y=0.99, yanchor="top",
              ),
              barmode="group",
              margin=dict(l=10, r=20, t=36, b=8),
            )
            return fig, d

        # ── Бүх категорийн жагсаалт ───────────────────────────────────────────
        PAIRS = [
            ("marital_label",  "Гэрлэлтийн байдал"),
            ("edu_name",       "Боловсролын түвшин"),
            ("age_group",      "Насны бүлэг"),
            ("ios_label",      "Төхөөрөмж (iOS / Android)"),
            ("bio_label",      "Биометр нэвтрэлт"),
            ("dev_label",      "Төхөөрөмж санасан эсэх"),
            ("slry_cont_label","Цалингийн тасралтгүй байдал"),
            ("location_type",  "Байршил (УБ / Орон нутаг)"),
            ("gender_label",   "Жендэр"),
        ]
        FIXED_H = 340  # Бүх chart ижил өндөр

        for i in range(0, len(PAIRS), 2):
            row_pairs = PAIRS[i:i+2]
            cols_ = st.columns(2)
            for j in range(2):
                with cols_[j]:
                    if j < len(row_pairs):
                        col, title = row_pairs[j]
                        st.markdown(f'<div class="sh">{title}</div>', unsafe_allow_html=True)
                        res = dual_bar(col, title, FIXED_H)
                        if res:
                            fig, _ = res
                            st.plotly_chart(fig, use_container_width=True)

        # ── Байршлаар (дэлгэрэнгүй) ──────────────────────────────────────────
        st.markdown('<div class="sh">Байршлаар — дундаж хоног & хэтрэлтийн rate (тоо ≥ 5)</div>',
            unsafe_allow_html=True)
        if "location" in df_cust.columns and "has_overdue" in df_cust.columns:
            ld = df_cust.groupby("location", observed=True).agg(
                нийт    =("location",    "count"),
                дундаж  =(OD,            "mean"),
                хэтэрсэн=("has_overdue", "sum"),
            ).reset_index()
            ld = ld[ld["нийт"] >= 5].copy()
            ld["rate"]   = (ld["хэтэрсэн"] / ld["нийт"] * 100).round(1)
            ld["дундаж"] = ld["дундаж"].round(2)
            ld = ld.sort_values("дундаж", ascending=True)

            fig_loc = go.Figure()
            # Bar — дундаж хоног (horizontal)
            fig_loc.add_trace(go.Bar(
                y=ld["location"].astype(str), x=ld["дундаж"],
                name="Дундаж хоног",
                orientation="h",
                marker=dict(
                    color=ld["дундаж"],
                    colorscale=[[0,"#1a73e8"],[1,"#e24b4a"]],
                    showscale=False,
                ),
                text=ld["дундаж"].round(1),
                textposition="outside",
                textfont=dict(color="#111", size=11),
                xaxis="x1",
            ))
            # Scatter — rate % (horizontal)
            fig_loc.add_trace(go.Scatter(
                y=ld["location"].astype(str), x=ld["rate"],
                name="Хэтрэлтийн rate %",
                mode="markers+text",
                marker=dict(size=9, color="#e24b4a",
                            symbol="diamond",
                            line=dict(color="#fff", width=1.2)),
                text=ld["rate"].astype(str) + "%",
                textposition="middle right",
                textfont=dict(color="#e24b4a", size=10),
                xaxis="x2",
            ))
            h_loc = max(380, len(ld) * 26)
            L(fig_loc, height=h_loc,
              xaxis =dict(**AXIS, title="Дундаж хоног"),
              xaxis2=dict(
                  overlaying="x", side="top",
                  title="Хэтрэлтийн rate %",
                  ticksuffix="%",
                  tickfont=dict(color="#e24b4a", size=11),
                  title_font=dict(color="#e24b4a", size=12),
                  gridcolor="rgba(0,0,0,0)",
                  range=[0, min(ld["rate"].max() * 2.2, 100)],
              ),
              legend=dict(
                  font=dict(color="#111",size=11),
                  bgcolor="rgba(255,255,255,0.88)",
                  bordercolor="#ddd", borderwidth=1,
                  orientation="v",
                  x=0.01, xanchor="left",
                  y=0.99, yanchor="top",
              ),
              margin=dict(l=10, r=20, t=36, b=16),
            )
            st.plotly_chart(fig_loc, use_container_width=True)

        # ── Нэгтгэл хүснэгт ──────────────────────────────────────────────────
        st.markdown('<div class="sh">Бүх категорийн нэгтгэл хүснэгт</div>', unsafe_allow_html=True)
        summ_rows = []
        for col, title in PAIRS:
            if col not in df_cust.columns or "has_overdue" not in df_cust.columns:
                continue
            for val, grp in df_cust.groupby(col, observed=True):
                od_r = grp["has_overdue"].mean() * 100
                summ_rows.append({
                    "Хувьсагч": title,
                    "Утга":     str(val),
                    "Тоо":      len(grp),
                    "Хэтрэлтийн rate %": round(od_r, 1),
                    "Дундаж хоног":      round(grp[OD].mean(), 1),
                    "Медиан хоног":      round(grp[OD].median(), 1),
                })
        if summ_rows:
            summ_df = pd.DataFrame(summ_rows).sort_values(
                ["Хувьсагч","Хэтрэлтийн rate %"], ascending=[True, False])
            st.dataframe(summ_df, use_container_width=True,
                hide_index=True, height=400)

    # ── C6: Цалингийн шинжилгээ ──────────────────────────────────────────
    with C6:
        OD = "max_overdue_day"
        has_slry = "slry_last_amt" in df_cust.columns

        if not has_slry:
            st.info("Цалингийн мэдээлэл байхгүй байна.")
        else:
            # ── KPI ──────────────────────────────────────────────────────────
            sl = df_cust["slry_last_amt"].dropna()
            sl6 = df_cust["slry_last_avg_6m"].dropna() if "slry_last_avg_6m" in df_cust.columns else pd.Series()
            od_sl  = df_cust[df_cust["has_overdue"]]["slry_last_amt"].dropna() if "has_overdue" in df_cust.columns else pd.Series()
            nod_sl = df_cust[~df_cust["has_overdue"]]["slry_last_amt"].dropna() if "has_overdue" in df_cust.columns else pd.Series()
            pct_no_slry = df_cust["slry_last_amt"].isna().mean()*100 if "slry_last_amt" in df_cust.columns else 0

            k1,k2,k3,k4,k5 = st.columns(5)
            k1.metric("Дундаж цалин",         f"₮{sl.mean()/1e6:.2f}M" if len(sl) else "–")
            k2.metric("Медиан цалин",          f"₮{sl.median()/1e6:.2f}M" if len(sl) else "–")
            k3.metric("Мэдээлэлгүй хувь",      f"{pct_no_slry:.1f}%")
            k4.metric("OD дундаж цалин",        f"₮{od_sl.mean()/1e6:.2f}M" if len(od_sl) else "–")
            k5.metric("NOD дундаж цалин",       f"₮{nod_sl.mean()/1e6:.2f}M" if len(nod_sl) else "–")
            st.markdown("---")

            # ── sub1: Цалингийн тархалт ──────────────────────────────────────
            c1, c2 = st.columns(2)
            with c1:
                st.markdown('<div class="sh">Цалингийн тархалт (гистограм)</div>', unsafe_allow_html=True)
                tmp = df_cust[["slry_last_amt","has_overdue"]].dropna(subset=["slry_last_amt"])
                tmp["Бүлэг"] = tmp["has_overdue"].map({True:"Хэтрэлттэй", False:"Хэвийн"})
                fig = px.histogram(tmp, x="slry_last_amt", color="Бүлэг", nbins=40,
                    barmode="overlay", opacity=0.65,
                    color_discrete_map={"Хэтрэлттэй":"#e24b4a","Хэвийн":"#1d9e75"},
                    labels={"slry_last_amt":"Сүүлийн цалин (₮)"})
                L(fig, height=300)
                st.plotly_chart(fig, use_container_width=True)
            with c2:
                st.markdown('<div class="sh">Цалин vs MAX хэтрэлт (scatter)</div>', unsafe_allow_html=True)
                tmp2 = df_cust[["slry_last_amt", OD, "overdue_status"]].dropna(subset=["slry_last_amt"])
                fig2 = px.scatter(tmp2, x="slry_last_amt", y=OD,
                    color="overdue_status",
                    color_discrete_sequence=["#1d9e75","#F5A623","#E8813A","#E24B4A"],
                    opacity=0.5, trendline="ols",
                    labels={"slry_last_amt":"Цалин (₮)", OD:"MAX хэтрэлт (хоног)"})
                corr = df_cust[["slry_last_amt", OD]].dropna().corr().iloc[0,1]
                L(fig2, height=300)
                st.plotly_chart(fig2, use_container_width=True)
                if corr < -0.05:
                    _msg = "Цалин өндөр байсан харилцагчид хэтрэлт харьцангуй бага — орлого хэтрэлтийн эрсдэлийг бууруулж байна."
                    _box = "box box-green"
                elif corr > 0.05:
                    _msg = "Цалин өндөр ч хэтрэлт их байгаа нь зээлийн дарамт орлогоос хэтэрсэн байж болзошгүй."
                    _box = "box box-warn"
                else:
                    _msg = "Цалин болон хэтрэлтийн хоорондын хамаарал маш сул — цалин дангаараа хэтрэлтийг тайлбарлах чадвар хязгаарлагдмал."
                    _box = "box box-blue"
                st.markdown(
                    f'<div class="{_box}">📊 <b>Корреляц: {corr:+.3f}</b> — {_msg}</div>',
                    unsafe_allow_html=True)


            # ── sub2: Цалингийн bucket × хэтрэлтийн rate ────────────────────
            st.markdown('<div class="sh">Цалингийн бүсээр — хэтрэлтийн rate</div>', unsafe_allow_html=True)
            def slry_bucket(x):
                if pd.isna(x): return "Мэдээлэлгүй"
                if x < 500_000:   return "<500K"
                if x < 1_000_000: return "500K–1M"
                if x < 2_000_000: return "1M–2M"
                if x < 3_000_000: return "2M–3M"
                if x < 5_000_000: return "3M–5M"
                return "5M+"
            order = ["Мэдээлэлгүй","<500K","500K–1M","1M–2M","2M–3M","3M–5M","5M+"]
            df_cust["slry_bucket"] = df_cust["slry_last_amt"].apply(slry_bucket)
            sr = df_cust.groupby("slry_bucket").agg(
                нийт=("cust_code","count"),
                хэтэрсэн=("has_overdue","sum")
            ).reset_index()
            sr["rate"] = (sr["хэтэрсэн"]/sr["нийт"]*100).round(1)
            sr["slry_bucket"] = pd.Categorical(sr["slry_bucket"], categories=order, ordered=True)
            sr = sr.sort_values("slry_bucket")
            fig3 = go.Figure()
            fig3.add_trace(go.Bar(x=sr["slry_bucket"], y=sr["нийт"],
                name="Нийт", marker_color="#1a73e8", opacity=0.7,
                text=sr["нийт"], textposition="outside", yaxis="y1"))
            fig3.add_trace(go.Scatter(x=sr["slry_bucket"], y=sr["rate"],
                name="Хэтрэлтийн rate %", mode="lines+markers+text",
                line=dict(color="#e24b4a",width=2.5), marker=dict(size=9),
                text=sr["rate"].astype(str)+"%",
                textposition="top center", textfont=dict(color="#e24b4a",size=11),
                yaxis="y2"))
            L(fig3, height=340,
              yaxis=dict(**AXIS, title="Харилцагч"),
              yaxis2=dict(overlaying="y", side="right", title="Rate %",
                          ticksuffix="%", tickfont=dict(color="#e24b4a",size=11),
                          gridcolor="rgba(0,0,0,0)", range=[0,25]))
            st.plotly_chart(fig3, use_container_width=True)

            # ── sub3: 6 сарын дундаж цалин & тасралтгүй байдал ──────────────
            c3, c4 = st.columns(2)
            with c3:
                st.markdown('<div class="sh">6 сарын дундаж цалин — OD vs NOD (box)</div>', unsafe_allow_html=True)
                if "slry_last_avg_6m" in df_cust.columns:
                    tmp3 = df_cust[["slry_last_avg_6m","has_overdue"]].dropna(subset=["slry_last_avg_6m"])
                    tmp3["Бүлэг"] = tmp3["has_overdue"].map({True:"Хэтрэлттэй",False:"Хэвийн"})
                    fig4 = px.box(tmp3, x="Бүлэг", y="slry_last_avg_6m", color="Бүлэг",
                        color_discrete_map={"Хэтрэлттэй":"#e24b4a","Хэвийн":"#1d9e75"},
                        labels={"slry_last_avg_6m":"6 сарын дундаж цалин (₮)"})
                    L(fig4, height=300, showlegend=False)
                    st.plotly_chart(fig4, use_container_width=True)
            with c4:
                st.markdown('<div class="sh">Тасралтгүй цалин 3 сар — хэтрэлтийн rate</div>', unsafe_allow_html=True)
                if "slry_cont_label" in df_cust.columns:
                    sc = df_cust.groupby("slry_cont_label").agg(
                        нийт=("cust_code","count"), хэтэрсэн=("has_overdue","sum")).reset_index()
                    sc["rate"] = (sc["хэтэрсэн"]/sc["нийт"]*100).round(1)
                    fig5 = px.bar(sc, x="slry_cont_label", y="rate",
                        color="slry_cont_label",
                        color_discrete_sequence=["#1d9e75","#e24b4a","#f59e0b"],
                        text=sc.apply(lambda r:f"{r['rate']}% ({r['нийт']:,})",axis=1),
                        labels={"slry_cont_label":"Цалингийн байдал","rate":"Хэтрэлтийн rate %"})
                    fig5.update_traces(textposition="outside")
                    L(fig5, height=300, showlegend=False)
                    st.plotly_chart(fig5, use_container_width=True)
            # ── sub4: 24 сард цалин төлсөн тоо ──────────────────────────────
            if "slry_last_row_cnt_24m" in df_cust.columns:
                st.markdown('<div class="sh">24 сард цалин төлсөн тоо — хэтрэлтийн шинжилгээ</div>',
                    unsafe_allow_html=True)
                c5, c6 = st.columns(2)
                with c5:
                    # OD vs NOD box plot
                    tmp_24 = df_cust[["slry_last_row_cnt_24m","has_overdue"]].dropna(
                        subset=["slry_last_row_cnt_24m"])
                    tmp_24["Бүлэг"] = tmp_24["has_overdue"].map(
                        {True:"Хэтрэлттэй", False:"Хэвийн"})
                    fig_24a = px.box(tmp_24, x="Бүлэг", y="slry_last_row_cnt_24m",
                        color="Бүлэг",
                        color_discrete_map={"Хэтрэлттэй":"#e24b4a","Хэвийн":"#1d9e75"},
                        labels={"slry_last_row_cnt_24m":"24 сард цалин төлсөн тоо"})
                    L(fig_24a, height=300, showlegend=False)
                    st.plotly_chart(fig_24a, use_container_width=True)
                    _corr_24 = df_cust[["slry_last_row_cnt_24m", OD]].dropna().corr().iloc[0,1]
                    if _corr_24 < -0.05:
                        _m24 = "Цалин тогтмол орж байсан харилцагчид хэтрэлт бага — тасралтгүй орлого хамгаалалт болж байна."
                        _b24 = "box box-green"
                    elif _corr_24 > 0.05:
                        _m24 = "Цалин тооны өсөлт хэтрэлтийг буурааж чадахгүй байна."
                        _b24 = "box box-warn"
                    else:
                        _m24 = "24 сарын цалингийн бичилт хэтрэлттэй шугаман хамаарал сул байна."
                        _b24 = "box box-blue"
                    st.markdown(
                        f'<div class="{_b24}">📊 <b>Корреляц: {_corr_24:+.3f}</b> — {_m24}</div>',
                        unsafe_allow_html=True)
 

    # # ── C7: Зээлийн дүн & DTI ─────────────────────────────────────────────
    with C7:
        OD = "max_overdue_day"

        # ── KPI ──────────────────────────────────────────────────────────────
        k1,k2,k3,k4,k5 = st.columns(5)
        ta = df_cust["total_loan_amt"] if "total_loan_amt" in df_cust.columns else pd.Series()
        dti = df_cust["dti_ratio"].dropna() if "dti_ratio" in df_cust.columns else pd.Series()
        lsr = df_cust["loan_to_salary_ratio"].dropna() if "loan_to_salary_ratio" in df_cust.columns else pd.Series()
        k1.metric("Нийт зээлийн дүн (нийт)",  f"₮{ta.sum()/1e9:.2f}T" if len(ta) else "–")
        k2.metric("Дундаж зээлийн дүн/хүн",    f"₮{ta.mean()/1e6:.2f}M" if len(ta) else "–")
        k3.metric("Дундаж DTI",                 f"{dti.mean():.2f}" if len(dti) else "–")
        k4.metric("DTI > 0.5 харилцагч",
            f"{int((dti>0.5).sum()):,}" if len(dti) else "–", delta_color="inverse")
        k5.metric("Зээл/Цалин дундаж харьцаа",  f"{lsr.mean():.1f}x" if len(lsr) else "–")
        st.markdown("---")

        # ── sub1: Зээлийн дүнгийн тархалт ───────────────────────────────────
        c1, c2 = st.columns(2)
        with c1:
            st.markdown('<div class="sh">Нийт зээлийн дүн — OD vs NOD (box)</div>', unsafe_allow_html=True)
            if "total_loan_amt" in df_cust.columns and "has_overdue" in df_cust.columns:
                tmp = df_cust[["total_loan_amt","has_overdue"]].copy()
                tmp["Бүлэг"] = tmp["has_overdue"].map({True:"Хэтрэлттэй",False:"Хэвийн"})
                fig = px.box(tmp, x="Бүлэг", y="total_loan_amt", color="Бүлэг",
                    color_discrete_map={"Хэтрэлттэй":"#e24b4a","Хэвийн":"#1d9e75"},
                    labels={"total_loan_amt":"Нийт зээлийн дүн (₮)"})
                L(fig, height=300, showlegend=False)
                st.plotly_chart(fig, use_container_width=True)
        with c2:
            st.markdown('<div class="sh">Зээлийн дүн × MAX хэтрэлт (scatter)</div>', unsafe_allow_html=True)
            if "total_loan_amt" in df_cust.columns:
                tmp2 = df_cust[["total_loan_amt", OD, "has_overdue"]].dropna()
                tmp2["Бүлэг"] = tmp2["has_overdue"].map({True:"Хэтрэлттэй",False:"Хэвийн"})
                fig2 = px.scatter(tmp2, x="total_loan_amt", y=OD, color="Бүлэг",
                    color_discrete_map={"Хэтрэлттэй":"#e24b4a","Хэвийн":"#1d9e75"},
                    opacity=0.5, trendline="ols",
                    labels={"total_loan_amt":"Нийт зээлийн дүн (₮)", OD:"MAX хэтрэлт (хоног)"})
                corr = tmp2[["total_loan_amt", OD]].corr().iloc[0,1]
                L(fig2, height=300)
                st.plotly_chart(fig2, use_container_width=True)
                st.caption(f"Корреляц: **{corr:+.3f}**")

        # ── sub2: DTI шинжилгээ ───────────────────────────────────────────────
        st.markdown('<div class="sh">DTI (Сарын төлбөр / Цалин) — хэтрэлтийн rate</div>', unsafe_allow_html=True)
        if "dti_ratio" in df_cust.columns and "has_overdue" in df_cust.columns:
            def dti_bucket(x):
                if pd.isna(x): return "Мэдээлэлгүй"
                if x <= 0.2:  return "≤0.2"
                if x <= 0.4:  return "0.2–0.4"
                if x <= 0.6:  return "0.4–0.6"
                if x <= 0.8:  return "0.6–0.8"
                if x <= 1.0:  return "0.8–1.0"
                return ">1.0"
            dti_order = ["Мэдээлэлгүй","≤0.2","0.2–0.4","0.4–0.6","0.6–0.8","0.8–1.0",">1.0"]
            df_cust["dti_bucket"] = df_cust["dti_ratio"].apply(dti_bucket)
            dr = df_cust.groupby("dti_bucket").agg(
                нийт=("cust_code","count"), хэтэрсэн=("has_overdue","sum")).reset_index()
            dr["rate"] = (dr["хэтэрсэн"]/dr["нийт"]*100).round(1)
            dr["dti_bucket"] = pd.Categorical(dr["dti_bucket"], categories=dti_order, ordered=True)
            dr = dr.sort_values("dti_bucket")
            c3, c4 = st.columns(2)
            with c3:
                fig3 = go.Figure()
                fig3.add_trace(go.Bar(x=dr["dti_bucket"], y=dr["нийт"],
                    name="Нийт", marker_color="#1a73e8", opacity=0.7,
                    text=dr["нийт"], textposition="outside", yaxis="y1"))
                fig3.add_trace(go.Scatter(x=dr["dti_bucket"], y=dr["rate"],
                    name="Rate %", mode="lines+markers+text",
                    line=dict(color="#e24b4a",width=2.5), marker=dict(size=9),
                    text=dr["rate"].astype(str)+"%",
                    textposition="top center", textfont=dict(color="#e24b4a",size=11),
                    yaxis="y2"))
                L(fig3, height=340,
                  yaxis=dict(**AXIS, title="Харилцагч"),
                  yaxis2=dict(overlaying="y", side="right", title="Rate %",
                              ticksuffix="%", tickfont=dict(color="#e24b4a",size=11),
                              gridcolor="rgba(0,0,0,0)", range=[0,30]))
                st.plotly_chart(fig3, use_container_width=True)
            with c4:
                st.markdown('<div class="sh">DTI тархалт — OD vs NOD</div>', unsafe_allow_html=True)
                tmp3 = df_cust[["dti_ratio","has_overdue"]].dropna(subset=["dti_ratio"])
                tmp3["Бүлэг"] = tmp3["has_overdue"].map({True:"Хэтрэлттэй",False:"Хэвийн"})
                fig4 = px.histogram(tmp3, x="dti_ratio", color="Бүлэг",
                    barmode="overlay", opacity=0.65, nbins=30,
                    color_discrete_map={"Хэтрэлттэй":"#e24b4a","Хэвийн":"#1d9e75"},
                    labels={"dti_ratio":"DTI харьцаа"})
                L(fig4, height=300)
                st.plotly_chart(fig4, use_container_width=True)

        # ── sub3: Зээл/Цалин харьцаа ─────────────────────────────────────────
        st.markdown('<div class="sh">Зээл/Цалин харьцаа × MAX хэтрэлт</div>', unsafe_allow_html=True)
        if "loan_to_salary_ratio" in df_cust.columns:
            def lsr_bucket(x):
                if pd.isna(x): return "Мэдээлэлгүй"
                if x <= 1:  return "≤1x"
                if x <= 2:  return "1–2x"
                if x <= 3:  return "2–3x"
                if x <= 5:  return "3–5x"
                return ">5x"
            lsr_order = ["Мэдээлэлгүй","≤1x","1–2x","2–3x","3–5x",">5x"]
            df_cust["lsr_bucket"] = df_cust["loan_to_salary_ratio"].apply(lsr_bucket)
            lr = df_cust.groupby("lsr_bucket").agg(
                нийт=("cust_code","count"), хэтэрсэн=("has_overdue","sum")).reset_index()
            lr["rate"] = (lr["хэтэрсэн"]/lr["нийт"]*100).round(1)
            lr["lsr_bucket"] = pd.Categorical(lr["lsr_bucket"], categories=lsr_order, ordered=True)
            lr = lr.sort_values("lsr_bucket")
            fig5 = go.Figure()
            fig5.add_trace(go.Bar(x=lr["lsr_bucket"], y=lr["нийт"],
                name="Нийт", marker_color="#1a73e8", opacity=0.7,
                text=lr["нийт"], textposition="outside", yaxis="y1"))
            fig5.add_trace(go.Scatter(x=lr["lsr_bucket"], y=lr["rate"],
                name="Rate %", mode="lines+markers+text",
                line=dict(color="#e24b4a",width=2.5), marker=dict(size=9),
                text=lr["rate"].astype(str)+"%",
                textposition="top center", textfont=dict(color="#e24b4a",size=11),
                yaxis="y2"))
            L(fig5, height=320,
              yaxis=dict(**AXIS, title="Харилцагч"),
              yaxis2=dict(overlaying="y", side="right", title="Rate %",
                          ticksuffix="%", tickfont=dict(color="#e24b4a",size=11),
                          gridcolor="rgba(0,0,0,0)", range=[0,30]))
            st.plotly_chart(fig5, use_container_width=True)

    # ── C8: Score шинжилгээ ───────────────────────────────────────────────
    with C8:
        OD = "max_overdue_day"

         # Bucket тодорхойлолт
        _BUCK_BINS   = [-1, 0, 1, 5, 10, 15, 30, 9999]
        _BUCK_LABELS = ["0", "1", "2–5", "6–10", "11–15", "16–30", "30+"]
        _BUCK_COLORS = {
            "0":     "#1d9e75",
            "1":     "#84cc16",
            "2–5":   "#f59e0b",
            "6–10":  "#f97316",
            "11–15": "#ef4444",
            "16–30": "#dc2626",
            "30+":   "#7f1d1d",
        }
        score_cols = {
            "total_score":    "Нийт оноо",
            "fin_score":      "Санхүүгийн оноо",
            "psy_score":      "Сэтгэл зүйн оноо",
            "total_score_sr": "Нийт оноо (SR)",
        }
        avail = {k:v for k,v in score_cols.items() if k in df_cust.columns}

        # ── KPI: OD vs NOD дундаж оноо ───────────────────────────────────────
        if avail and "has_overdue" in df_cust.columns:
            od_g  = df_cust[df_cust["has_overdue"]]
            nod_g = df_cust[~df_cust["has_overdue"]]
            cols_k = st.columns(len(avail))
            for i, (col, lbl) in enumerate(avail.items()):
                od_m  = od_g[col].mean()  if col in od_g.columns  else None
                nod_m = nod_g[col].mean() if col in nod_g.columns else None
                diff  = od_m - nod_m if (od_m is not None and nod_m is not None) else None
                cols_k[i].metric(
                    lbl,
                    f"OD:{od_m:.1f}" if od_m is not None else "–",
                    delta=f"NOD-тай зөрүү: {diff:+.1f}" if diff is not None else None,
                    delta_color="inverse"
                )
        st.markdown("---")

        # ── sub1: Score тархалт — bucket-аар (selectbox) ─────────────────────
        st.markdown('<div class="sh">Score тархалт — хэтрэлтийн bucket-аар</div>', unsafe_allow_html=True)
        sel_score = st.selectbox("Оноо сонгох:", list(avail.keys()),
            format_func=lambda x: avail.get(x, x), key="score_sel")

       

        if sel_score and OD in df_cust.columns:
            tmp = df_cust[[sel_score, OD]].dropna(subset=[sel_score, OD]).copy()
            tmp["Bucket"] = pd.cut(tmp[OD], bins=_BUCK_BINS, labels=_BUCK_LABELS, right=True)
            tmp["Bucket"] = pd.Categorical(tmp["Bucket"], categories=_BUCK_LABELS, ordered=True)
            tmp_2g = df_cust[[sel_score, "has_overdue"]].dropna(subset=[sel_score]).copy()
            tmp_2g["Бүлэг"] = tmp_2g["has_overdue"].map({True:"Хэтрэлттэй", False:"Хэвийн"})

            # ① Histogram — бүтэн өргөн
            st.markdown('<div class="sh">① Оноогийн тархалт — Хэвийн vs Хэтрэлттэй</div>',
                unsafe_allow_html=True)
            fig_h = px.histogram(tmp_2g, x=sel_score, color="Бүлэг",
                barmode="overlay", opacity=0.65, nbins=40,
                color_discrete_map={"Хэтрэлттэй":"#e24b4a","Хэвийн":"#1d9e75"},
                labels={sel_score: avail.get(sel_score, sel_score), "Бүлэг":"Бүлэг"})
            L(fig_h, height=320)
            st.plotly_chart(fig_h, use_container_width=True)

            # ② 2 бүлэг box | 7 bucket box
            st.markdown('<div class="sh">② Box plot — Хэвийн vs Хэтрэлттэй  |  Хэтрэлтийн bucket-аар</div>',
                unsafe_allow_html=True)
            ca, cb = st.columns(2)
            with ca:
                fig_b2 = px.box(tmp_2g, x="Бүлэг", y=sel_score, color="Бүлэг",
                    color_discrete_map={"Хэтрэлттэй":"#e24b4a","Хэвийн":"#1d9e75"},
                    points="outliers",
                    labels={"Бүлэг":"", sel_score: avail.get(sel_score, sel_score)})
                fig_b2.update_traces(marker=dict(size=3, opacity=0.4))
                L(fig_b2, height=360, showlegend=False)
                st.plotly_chart(fig_b2, use_container_width=True)
            with cb:
                fig_bk = px.box(tmp, x="Bucket", y=sel_score, color="Bucket",
                    color_discrete_map=_BUCK_COLORS, points=False,
                    category_orders={"Bucket": _BUCK_LABELS},
                    labels={"Bucket":"Хэтрэлтийн бүс (хоног)",
                            sel_score: avail.get(sel_score, sel_score)})
                L(fig_bk, height=360, showlegend=False)
                st.plotly_chart(fig_bk, use_container_width=True)

            # Нэгтгэл хүснэгт
            # summ = tmp.groupby("Bucket", observed=False)[sel_score].agg(
            #     Тоо="count", Дундаж="mean", Медиан="median", Std="std"
            # ).reset_index()
            # summ["Дундаж"] = summ["Дундаж"].round(1)
            # summ["Медиан"] = summ["Медиан"].round(1)
            # summ["Std"]    = summ["Std"].round(1)
            # summ.columns   = ["Bucket", "Тоо", "Дундаж", "Медиан", "Std"]
            # st.dataframe(summ, use_container_width=True, hide_index=True, height=295)

        # ── sub2: Score band × хэтрэлтийн rate ──────────────────────────────
        st.markdown('<div class="sh">Score band × хэтрэлтийн rate</div>', unsafe_allow_html=True)
        sel2 = st.selectbox("Оноо сонгох (band):", list(avail.keys()),
            format_func=lambda x: avail.get(x, x), key="score_band_sel")
        if sel2 in df_cust.columns and "has_overdue" in df_cust.columns:
            mn = df_cust[sel2].min(); mx = df_cust[sel2].max()
            step = (mx - mn) / 8
            bins  = [mn + i*step for i in range(9)]
            labels_b = [f"{int(bins[i])}–{int(bins[i+1])}" for i in range(8)]
            df_cust["_tmp_band"] = pd.cut(df_cust[sel2], bins=bins, labels=labels_b, include_lowest=True)
            sb = df_cust.groupby("_tmp_band", observed=True).agg(
                нийт=("cust_code","count"), хэтэрсэн=("has_overdue","sum"),
                avg_od=(OD,"mean")).reset_index()
            sb["rate"] = (sb["хэтэрсэн"]/sb["нийт"]*100).round(1)
            fig3 = go.Figure()
            fig3.add_trace(go.Bar(x=sb["_tmp_band"].astype(str), y=sb["нийт"],
                name="Нийт", marker_color="#1a73e8", opacity=0.6,
                text=sb["нийт"], textposition="outside", yaxis="y1"))
            fig3.add_trace(go.Scatter(x=sb["_tmp_band"].astype(str), y=sb["rate"],
                name="Хэтрэлт %", mode="lines+markers+text",
                line=dict(color="#e24b4a",width=2.5), marker=dict(size=9),
                text=sb["rate"].astype(str)+"%",
                textposition="top center", textfont=dict(color="#e24b4a",size=11),
                yaxis="y2"))
            L(fig3, height=360,
              yaxis=dict(**AXIS, title="Харилцагч"),
              yaxis2=dict(overlaying="y", side="right", title="Rate %",
                          ticksuffix="%", tickfont=dict(color="#e24b4a",size=11),
                          gridcolor="rgba(0,0,0,0)", range=[0,25]))
            st.plotly_chart(fig3, use_container_width=True)
            df_cust.drop(columns=["_tmp_band"], inplace=True, errors="ignore")

        # ── sub3: fin_score vs psy_score scatter ─────────────────────────────
        if "fin_score" in df_cust.columns and "psy_score" in df_cust.columns:
            st.markdown('<div class="sh">Санхүүгийн оноо × Сэтгэл зүйн оноо</div>', unsafe_allow_html=True)
            tmp3 = df_cust[["fin_score","psy_score","has_overdue", OD]].dropna(subset=["fin_score","psy_score"])
            tmp3["Бүлэг"] = tmp3["has_overdue"].map({True:"Хэтрэлттэй",False:"Хэвийн"})
            c3, c4 = st.columns(2)
            with c3:
                fig4 = px.scatter(tmp3, x="fin_score", y="psy_score", color="Бүлэг",
                    color_discrete_map={"Хэтрэлттэй":"#e24b4a","Хэвийн":"#1d9e75"},
                    opacity=0.5,
                    labels={"fin_score":"Санхүүгийн оноо","psy_score":"Сэтгэл зүйн оноо"})
                L(fig4, height=320)
                st.plotly_chart(fig4, use_container_width=True)
            with c4:
                fig5 = px.scatter(tmp3, x="fin_score", y="psy_score",
                    color=OD, color_continuous_scale="RdYlGn_r",
                    opacity=0.6,
                    labels={"fin_score":"Санхүүгийн оноо","psy_score":"Сэтгэл зүйн оноо",
                            OD:"MAX хэтрэлт (хоног)"})
                L(fig5, height=320)
                st.plotly_chart(fig5, use_container_width=True)

        # ── sub4: Score нэгтгэл хүснэгт ──────────────────────────────────────
        st.markdown('<div class="sh">Score нэгтгэл хүснэгт — OD vs NOD</div>', unsafe_allow_html=True)
        if avail and "has_overdue" in df_cust.columns:
            rows_s = []
            for col, lbl in avail.items():
                if col not in df_cust.columns: continue
                od_v  = df_cust[df_cust["has_overdue"]][col].dropna()
                nod_v = df_cust[~df_cust["has_overdue"]][col].dropna()
                rows_s.append({
                    "Оноо": lbl,
                    "OD дундаж": round(od_v.mean(),1) if len(od_v) else "–",
                    "NOD дундаж": round(nod_v.mean(),1) if len(nod_v) else "–",
                    "Зөрүү": round(od_v.mean()-nod_v.mean(),1) if len(od_v) and len(nod_v) else "–",
                    "OD медиан": round(od_v.median(),1) if len(od_v) else "–",
                    "NOD медиан": round(nod_v.median(),1) if len(nod_v) else "–",
                })
            st.dataframe(pd.DataFrame(rows_s), use_container_width=True, hide_index=True)

    # ── C9: Корреляц & Scatter ────────────────────────────────────────────
    with C9:
        OD = "max_overdue_day"
        NUM = {
            "age":                       "Нас",
            # "total_loan_amt":            "Нийт зээлийн дүн",
            # "avg_loan_amt":              "Дундаж зээлийн дүн",
            "fin_score":                 "Санхүүгийн оноо",
            "psy_score":                 "Сэтгэл зүйн оноо",
            "total_score":               "Нийт оноо",
            "zms_active_ln_cnt":         "Идэвхтэй зээлийн тоо",
            "total_monthly_payment":     "Сарын нийт төлбөр",
            "zms_closed_ln_total_amount":"Хаагдсан зээлийн нийт дүн",
            "slry_last_avg_6m":          "Цалингийн 6с дундаж",
            "slry_last_amt":             "Сүүлийн цалин",
            "slry_last_row_cnt_24m":     "Цалингийн бичилт (24с)",
            "dti_ratio":                 "DTI харьцаа",
            # "loan_to_salary_ratio":      "Зээл/Цалин харьцаа",
            "total_loan_cnt":            "Нийт зээлийн тоо",
            # "max_calc_lmt":              "Зээлийн хязгаар",
        }

        # ── Корреляц bar chart ────────────────────────────────────────────────
        st.markdown('<div class="sh">Бүх тоон хувьсагчийн хэтрэлттэй корреляц</div>', unsafe_allow_html=True)
        @st.cache_data(show_spinner=False)
        def _calc_corr(period, num_cols_tuple):
            _d = load_period(period)
            if "gender_label" not in _d.columns:
                _d = preprocess(_d)
            _cd = build_customer_df(_d)
            _od = "max_overdue_day"
            _rows = []
            for col, lbl in num_cols_tuple:
                if col not in _cd.columns: continue
                tmp = _cd[[col, _od]].dropna()
                if len(tmp) > 5:
                    _rows.append({
                        "Хувьсагч": lbl,
                        "Корреляц": round(tmp[col].corr(tmp[_od]), 4),
                        "n": len(tmp)
                    })
            return _rows

        rows_c = _calc_corr(selected, tuple(NUM.items()))
        if rows_c:
            cdf = pd.DataFrame(rows_c).sort_values("Корреляц")
            figC = go.Figure(go.Bar(
                x=cdf["Корреляц"], y=cdf["Хувьсагч"], orientation="h",
                marker_color=["#E24B4A" if v < 0 else "#1D9E75" for v in cdf["Корреляц"]],
                text=[f"{v:+.4f}  (n={n:,})" for v, n in zip(cdf["Корреляц"], cdf["n"])],
                textposition="outside", textfont=dict(color="#111", size=12)))
            figC.add_vline(x=0, line_color="#888", line_width=1.5)
            L(figC, height=480, showlegend=False,
              margin=dict(l=10, r=160, t=32, b=8))
            st.plotly_chart(figC, use_container_width=True)
            st.caption("🟢 Эерэг = хувьсагч нэмэгдэхэд хэтрэлт нэмэгдэнэ  |  🔴 Сөрөг = хэтрэлт багасна")
        st.markdown("---")

        # ── Scatter: хувьсагч сонгоод харах ──────────────────────────────────
        st.markdown('<div class="sh">Тоон хувьсагч сонгоод scatter харах</div>', unsafe_allow_html=True)
        avail_n = {k: v for k, v in NUM.items() if k in df_cust.columns}
        sel_n = st.selectbox("Хувьсагч:", list(avail_n.keys()),
            format_func=lambda x: avail_n[x], key="corr_scatter_sel")
        if sel_n:
            color_col = "age_group" if "age_group" in df_cust.columns else None
            tmp2 = df_cust[[sel_n, OD] + ([color_col] if color_col else [])].dropna(subset=[sel_n, OD])
            figS = px.scatter(tmp2, x=sel_n, y=OD,
                color=color_col if color_col else None,
                color_discrete_sequence=px.colors.qualitative.Set2,
                opacity=0.55, trendline="ols",
                labels={sel_n: avail_n[sel_n], OD: "MAX хэтрэлт (хоног)",
                        "age_group": "Насны бүлэг"})
            corr2 = tmp2[[sel_n, OD]].corr().iloc[0, 1]
            L(figS, height=380)
            st.plotly_chart(figS, use_container_width=True)
            st.caption(f"**{avail_n[sel_n]}** × MAX хэтрэлт корреляц: **{corr2:+.4f}**")
        st.markdown("---")

        # ── C10: Өгөгдөл ───────────────────────────────────────────────────────
    with C10:
        # Бүх баганын нэрийн орчуулга — байгаа баганыг л харуулна
        ALL_COLS = {
            # ── Харилцагчийн үндсэн мэдээлэл ──
            COL_CUST:                    "Харилцагчийн код",
            "age":                       "Нас",
            "age_group":                 "Насны бүлэг",
            "gender_label":              "Жендэр",
            "marital_label":             "Гэрлэлтийн байдал",
            "edu_name":                  "Боловсрол",
            "location":                  "Байршил",
            "location_type":             "Байршлын төрөл",
            "is_bio_login":              "Биометр нэвтрэлт",
            "bio_label":                 "Биометр (label)",
            "has_ios":                   "iOS хэрэглэгч",
            "ios_label":                 "iOS (label)",
            "is_device_remember":        "Төхөөрөмж санасан",
            # ── Зээлийн нэгтгэл ──
            "total_loan_cnt":            "Нийт зээлийн тоо",
            "closed_cnt":                "Хаалттай (C)",
            "o_max_cnt":                 "O_max тоо",
            "o_active_cnt":              "O_active тоо",
            "overdue_loan_cnt":          "Хэтэрсэн зээлийн тоо",
            "status2":                   "O_active байсан уу (1/0)",
            "overdue_status":            "Хэтрэлтийн байдал",
            "overdue_band":              "Хэтрэлтийн бүс",
            OD:                          "MAX хэтрэлт (хоног)",
            "avg_overdue_day":           "Дундаж хэтрэлт (хоног)",
            "has_overdue":               "Хэтрэлттэй эсэх",
            # ── Зээлийн дүн ──
            "total_loan_amt":            "Нийт зээлийн дүн (₮)",
            "avg_loan_amt":              "Дундаж зээлийн дүн (₮)",
            "max_loan_amt":              "Хамгийн их зээлийн дүн (₮)",
            "min_loan_amt":              "Хамгийн бага зээлийн дүн (₮)",
            "max_calc_lmt":              "Зээлийн хязгаар (₮)",
            # ── Оноо ──
            "total_score":               "Нийт оноо",
            "total_score_sr":            "Нийт оноо (SR)",
            "fin_score":                 "Санхүүгийн оноо",
            "psy_score":                 "Сэтгэл зүйн оноо",
            "avg_score":                 "Дундаж оноо",
            "max_score":                 "Хамгийн өндөр оноо",
            "min_score":                 "Хамгийн бага оноо",
            # ── Цалингийн мэдээлэл ──
            "slry_last_amt":             "Сүүлийн цалин (₮)",
            "slry_last_avg_6m":          "6 сарын дундаж цалин (₮)",
            "slry_last_row_cnt_24m":     "24 сард цалингийн мөрийн тоо",
            "slry_has_cont_salary_3m":   "Тасралтгүй цалин 3 сар (1/0)",
            "slry_cont_label":           "Цалингийн тасралтгүй байдал",
            # ── Сарын төлбөр ──
            "zms_monthly_payment":       "Сарын зээлийн төлбөр (₮)",
            "total_monthly_payment":     "Нийт сарын төлбөр (₮)",
            "avg_monthly_payment":       "Дундаж сарын төлбөр (₮)",
            # ── ZMS зээлийн мэдээлэл ──
            "zms_active_ln_cnt":         "Идэвхтэй зээлийн тоо (ZMS)",
            "zms_closed_ln_total_amount":"Хаагдсан зээлийн нийт дүн (₮)",
            # ── Тооцоолсон баганууд ──
            "dti_ratio":                 "DTI (Сарын төлбөр / Цалин)",
            "loan_to_salary_ratio":      "Зээл/Цалин харьцаа",
            # ── Бусад ──
            "has_active_overdue_loan":   "Идэвхтэй хэтрэлттэй зээл",
        }

        # Байгаа баганыг л сонгоно
        dcols = {k: v for k, v in ALL_COLS.items() if k in df_cust.columns}

        # Хэсэг бүрээр задлан харуулна
        st.markdown('<div class="sh">Харилцагчийн бүрэн өгөгдөл</div>', unsafe_allow_html=True)
        st.caption(f"Нийт **{len(df_cust):,}** харилцагч · **{len(dcols)}** багана")

        # Шүүлтүүр: зөвхөн хэтрэлттэй харуулах сонголт
        show_od_only = st.checkbox("Зөвхөн хэтрэлттэй харилцагчийг харуулах", value=False)
        disp = df_cust[df_cust["has_overdue"]] if show_od_only and "has_overdue" in df_cust.columns else df_cust

        st.dataframe(
            disp[list(dcols.keys())]
                .rename(columns=dcols)
                .sort_values("MAX хэтрэлт (хоног)" if "MAX хэтрэлт (хоног)" in dcols.values() else list(dcols.values())[0],
                             ascending=False)
                .reset_index(drop=True),
            use_container_width=True,
            height=520,
        )

        # Download — бүрэн багана
        col_dl1, col_dl2 = st.columns(2)
        with col_dl1:
            st.download_button(
                "📥 Харилцагч CSV (бүх багана)",
                df_cust.to_csv(index=False).encode("utf-8-sig"),
                f"customer_full_{selected}.csv", "text/csv",
                use_container_width=True,
            )
        with col_dl2:
            # Зөвхөн хэтэрсэн харилцагч
            od_only = df_cust[df_cust["has_overdue"]] if "has_overdue" in df_cust.columns else df_cust
            st.download_button(
                f"📥 Хэтэрсэн харилцагч CSV ({len(od_only):,})",
                od_only.to_csv(index=False).encode("utf-8-sig"),
                f"customer_overdue_{selected}.csv", "text/csv",
                use_container_width=True,
            )

st.markdown("---")
st.caption(f"Хугацаа хэтрэлтийн шинжилгээ · {selected}")
