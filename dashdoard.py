import inspect
import os

import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
from pathlib import Path

st.set_page_config(page_title="Marine Climate Vulnerability", layout="wide",
                   initial_sidebar_state="expanded")
from pathlib import Path

DEFAULT_PATHS = [
    Path(__file__).parent / "Boyce_etal_2022_NATCC.csv",
]
RISK_ORDER = ["N", "M", "H", "C"]
RISK_NAMES = {"N": "None", "M": "Moderate", "H": "High", "C": "Critical"}
RISK_COLORS = {"N": "#5ccbf5", "M": "#8f93f7", "H": "#6a5cf0", "C": "#ff5c7a"}
SCEN_COLORS = {"SSP126": "#5ccbf5", "SSP585": "#6c6ff0"}
FONT_FAMILY = "Plus Jakarta Sans, Poppins, Segoe UI, sans-serif"

RENAME = {
    "Experiment": "Climate_Scenario", "SpecID": "Species_ID", "SPname": "Species_Name",
    "ClimSens": "Climate_Sensitivity", "ClimSensSD": "Sensitivity_SD",
    "ClimExpo": "Climate_Exposure", "ClimExpoSD": "Exposure_SD",
    "ClimAdapt": "Climate_Adaptation", "ClimAdaptSD": "Adaptation_SD",
    "ClimVuln": "Climate_Vulnerability", "ClimVulnSD": "Vulnerability_SD",
    "ClimSensRisk": "Sensitivity_Risk_Level", "ClimExpoRisk": "Exposure_Risk_Level",
    "ClimAdaptRisk": "Adaptation_Risk_Level", "ClimRisk": "Overall_Climate_Risk",
}

px.defaults.color_discrete_sequence = ["#6c6ff0", "#5ccbf5", "#8f93f7", "#ff8aa0", "#b9bcf8", "#2fb8e6"]
px.defaults.color_continuous_scale = ["#2a2b6b", "#5b5ee6", "#5ccbf5"]

FISH_URI = 'url("data:image/svg+xml,%3Csvg%20xmlns=\'http://www.w3.org/2000/svg\'%20viewBox=\'0%200%2024%2024\'%20fill=\'none\'%20stroke=\'black\'%20stroke-width=\'2\'%20stroke-linecap=\'round\'%20stroke-linejoin=\'round\'%3E%3Cpath%20d=\'M2.5%2012C6%206.5%2012.5%206%2016.5%2012C12.5%2018%206%2017.5%202.5%2012Z\'/%3E%3Cpath%20d=\'M16.5%2012L21.5%207.5V16.5Z\'/%3E%3Cpath%20d=\'M7.5%2011.2h.01\'/%3E%3C/svg%3E")'

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap');
html, body, .stApp, button, input, textarea, select, [data-baseweb] {font-family:'Plus Jakarta Sans','Poppins','Segoe UI',sans-serif !important;}
.stApp{background:#14142e;}
.block-container{padding-top:1.6rem;max-width:1400px;}

/* sidebar */
section[data-testid="stSidebar"]{background:#1a1a3f;border-right:1px solid rgba(255,255,255,.05);}
section[data-testid="stSidebar"] .block-container{padding-top:2rem;}
.brand{font-size:1.45rem;font-weight:800;color:#fff;line-height:1.15;margin:0 0 .3rem;}
.brand small{display:block;font-size:.8rem;font-weight:500;color:#8c8fc0;margin-top:4px;}
section[data-testid="stSidebar"] .stButton>button{justify-content:flex-start;gap:.75rem;border:0;border-radius:12px;
 padding:.8rem 1rem;font-weight:600;font-size:1rem;background:transparent;color:#c3c5ea;box-shadow:none;}
section[data-testid="stSidebar"] .stButton>button>div{justify-content:flex-start;width:100%;}
section[data-testid="stSidebar"] .stButton>button p{text-align:left;}
.st-key-nav_0 [data-testid="stIconMaterial"]{font-size:0 !important;width:1.3rem;height:1.3rem;display:inline-block;
 background-color:currentColor;-webkit-mask:__FISH__ center/contain no-repeat;mask:__FISH__ center/contain no-repeat;}
section[data-testid="stSidebar"] .stButton>button:hover{background:rgba(91,94,230,.20);color:#fff;}
section[data-testid="stSidebar"] .stButton>button[kind="primary"],
section[data-testid="stSidebar"] .stButton>button[data-testid="stBaseButton-primary"]{background:#5b5ee6;color:#fff;}

/* page header */
.page-head h1{margin:0;font-size:1.9rem;font-weight:800;color:#fff;}
.page-head p{margin:4px 0 18px;color:#8c8fc0;font-size:1rem;}

/* widgets + chart cards */
div[data-baseweb="select"]>div{background:#1d1d44;border:1px solid rgba(255,255,255,.08);border-radius:12px;}
div[data-testid="stVerticalBlockBorderWrapper"]{background:#1d1d44;border:1px solid rgba(255,255,255,.05) !important;border-radius:20px;}

/* KPI cards */
.kpi-grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(260px,340px));gap:22px;margin:12px 0 30px;}
.kpi{padding:26px 28px 24px;border-radius:20px;background:#1d1d44;border:1px solid rgba(255,255,255,.05);
 min-height:150px;transition:transform .2s ease,border-color .2s ease;animation:rise .5s ease both;}
.kpi:hover{transform:translateY(-3px);border-color:rgba(108,111,240,.55);}
.kpi .row{display:flex;align-items:center;gap:18px;}
.kpi .ic{flex:none;width:56px;height:56px;border-radius:16px;display:grid;place-items:center;}
.kpi .ic.cyan{background:#5ccbf5;}
.kpi .ic.indigo{background:#5b5ee6;}
.kpi .ic svg{width:26px;height:26px;stroke:#fff;fill:none;stroke-width:2;stroke-linecap:round;stroke-linejoin:round;}
.kpi .lb{color:#9a9dc9;font-size:.98rem;font-weight:500;}
.kpi .val{font-size:2.2rem;font-weight:800;color:#fff;line-height:1.15;letter-spacing:-.01em;overflow-wrap:anywhere;}
.kpi .sub{margin-top:16px;color:#8587b3;font-size:.84rem;line-height:1.45;}
.kpi .bar{height:8px;margin-top:14px;border-radius:99px;background:rgba(255,255,255,.08);overflow:hidden;}
.kpi .bar i{display:block;height:100%;border-radius:99px;background:linear-gradient(90deg,#5b5ee6,#5ccbf5);animation:fill 1s ease both;}
@keyframes fill{from{width:0}}
@keyframes rise{from{opacity:0;transform:translateY(12px)}to{opacity:1;transform:none}}
</style>
""".replace("__FISH__", FISH_URI), unsafe_allow_html=True)

st.markdown(
    '<div class="page-head"><h1>Marine Climate Dashboard</h1>',
    unsafe_allow_html=True,
)


_PC = inspect.signature(st.plotly_chart).parameters
_PLOT_KW = {"width": "stretch"} if "width" in _PC else {"use_container_width": True}
if "theme" in _PC:
    _PLOT_KW["theme"] = None
_n = [0]


def _clean_title(ax):
    t = ax.title.text
    if t:
        ax.title.text = t.replace("_", " ")


def show(fig, h=420, top=72):
    """Render a plotly figure with the ocean look (roomy margins, axis labels never cut off)."""
    _n[0] += 1
    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#c9cbf0", size=13, family=FONT_FAMILY), height=h,
        margin=dict(l=16, r=28, t=top, b=28),
        title=dict(x=0.01, xanchor="left", y=0.97, yanchor="top", font=dict(size=16, color="#ffffff")),
        legend=dict(title_text="", orientation="h", yanchor="bottom", y=1.0, xanchor="right", x=1),
        hoverlabel=dict(bgcolor="#2a2b6b", font_color="#ffffff"),
    )
    fig.update_xaxes(gridcolor="rgba(255,255,255,.07)", zeroline=False, automargin=True,
                     title_standoff=16, tickfont=dict(size=12), title_font=dict(size=13))
    fig.update_yaxes(gridcolor="rgba(255,255,255,.07)", zeroline=False, automargin=True,
                     title_standoff=16, tickfont=dict(size=12), title_font=dict(size=13))
    fig.for_each_xaxis(_clean_title)
    fig.for_each_yaxis(_clean_title)
    if any(t.type == "bar" for t in fig.data):
        fig.update_layout(bargap=0.3)
    with st.container(border=True):
        st.plotly_chart(fig, key=f"chart_{_n[0]}", config={"displayModeBar": False}, **_PLOT_KW)


def table(data, **kw):
    try:
        st.dataframe(data, width="stretch", **kw)
    except Exception:
        st.dataframe(data, use_container_width=True, **kw)


ICONS = {
    "list": '<line x1="8" y1="6" x2="21" y2="6"/><line x1="8" y1="12" x2="21" y2="12"/><line x1="8" y1="18" x2="21" y2="18"/>'
            '<line x1="3" y1="6" x2="3.01" y2="6"/><line x1="3" y1="12" x2="3.01" y2="12"/><line x1="3" y1="18" x2="3.01" y2="18"/>',
    "pulse": '<polyline points="22 12 18 12 15 21 9 3 6 12 2 12"/>',
    "shield": '<path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/>',
    "thermo": '<path d="M14 14.76V3.5a2.5 2.5 0 0 0-5 0v11.26a4.5 4.5 0 1 0 5 0z"/>',
}


def kpi_card(icon, label, value, sub="", bar=None, tone="indigo"):
    bar_html = f'<div class="bar"><i style="width:{max(0, min(100, bar)):.0f}%"></i></div>' if bar is not None else ""
    return (f'<div class="kpi"><div class="row"><div class="ic {tone}"><svg viewBox="0 0 24 24">{ICONS[icon]}</svg></div>'
            f'<div><div class="lb">{label}</div><div class="val">{value}</div></div></div>'
            f'<div class="sub">{sub}</div>{bar_html}</div>')


def cards(items):
    st.markdown('<div class="kpi-grid">' + "".join(items) + "</div>", unsafe_allow_html=True)


DESCRIPTION = """

This dataset covers marine kingdoms, families and species, and shows how each one is affected by climate change in terms of sensitivity, vulnerability and exposure, and how well the animals adapt to these changes.

**Key scores ( values : 0-1):**
- *Sensitivity*: how much the species itself is affected
- *Exposure*: how much climate change hits its habitat
- *Adaptation*: its ability to cope (higher = better)
- *Vulnerability*: the combined result

**Risk levels:** N (none) < M (moderate) < H (high) < C (critical)  |  **Ncells:** number of grid cells the species occupies (range size)
"""

def species_gauge(n_sel, n_total):
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=n_sel,
        number={"valueformat": ",", "font": {"size": 44, "color": "#ffffff", "family": FONT_FAMILY}},
        title={"text": f"Unique species<br><span style='font-size:0.8em;color:#8c8fc0'>of {n_total:,} in the full dataset</span>",
               "font": {"size": 16, "color": "#c9cbf0", "family": FONT_FAMILY}},
        domain={"x": [0.05, 0.95], "y": [0, 0.8]},
        gauge={
            "axis": {"range": [0, n_total], "tickcolor": "#6c6f9e", "tickfont": {"color": "#8c8fc0"}},
            "bar": {"color": "#5ccbf5", "thickness": 0.35},
            "bgcolor": "rgba(91,94,230,0.25)",
            "borderwidth": 0,
            "steps": [{"range": [0, n_total * 0.5], "color": "rgba(91,94,230,0.30)"},
                      {"range": [n_total * 0.5, n_total], "color": "rgba(91,94,230,0.45)"}],
        },
    ))
    return fig


# ---------------------------------------------------------------- Data loading
@st.cache_data(show_spinner="Loading data...")
def load_data(file_bytes=None, path=None):
    d = pd.read_csv(file_bytes if file_bytes is not None else path)
    d = d.drop(columns=[c for c in ["Unnamed: 0", "Comname"] if c in d.columns])
    return d.rename(columns=RENAME)


path = next((p for p in DEFAULT_PATHS if os.path.exists(p)), None)
if path is not None:
    df = load_data(None, path)
else:
    st.warning("`Boyce_etal_2022_NATCC.csv` was not found next to dashboard.py. Upload it once to continue.")
    uploaded = st.file_uploader("Upload CSV", type="csv")
    if uploaded is None:
        st.stop()
    df = load_data(uploaded, None)

NAV = [ 
    ("View 1 · Impact on The Animal", "set_meal", "🐟"),
    ("View 2 · Impact on Its Region", "public", "🌐"),
    ("Data & statistics", "query_stats", "📈"),
]
_BP = inspect.signature(st.button).parameters
if "page" not in st.session_state:
    st.session_state["page"] = NAV[0][0]

st.sidebar.markdown('<div class="brand">Marine Climate<small>Dashboard</small></div>', unsafe_allow_html=True)
st.sidebar.write("")
for i, (label, icon, emoji) in enumerate(NAV):
    kw = {"key": f"nav_{i}", "type": "primary" if st.session_state["page"] == label else "secondary"}
    kw.update({"width": "stretch"} if "width" in _BP else {"use_container_width": True})
    if "icon" in _BP:
        kw["icon"] = icon if not icon.isascii() else f":material/{icon}:"  # emoji or Material icon name
        text = label
    else:
        text = f"{emoji}  {label}"
    if st.sidebar.button(text, **kw):
        st.session_state["page"] = label
        st.rerun()
page = st.session_state["page"]
st.sidebar.write("")


def view_filters(key):
    """Three single-select dropdowns shown inside a view."""
    c1, c2, c3 = st.columns(3)
    scenario = c1.selectbox("Climate scenario", ["All"] + sorted(df["Climate_Scenario"].unique()), key=f"{key}_sc")
    kingdom = c2.selectbox("Kingdom", ["All"] + sorted(df["Kingdom"].unique()), key=f"{key}_k")
    risk = c3.selectbox("Overall climate risk", ["All"] + RISK_ORDER, key=f"{key}_r",
                        format_func=lambda r: "All" if r == "All" else f"{r} - {RISK_NAMES[r]}")
    mask = pd.Series(True, index=df.index)
    if scenario != "All":
        mask &= df["Climate_Scenario"] == scenario
    if kingdom != "All":
        mask &= df["Kingdom"] == kingdom
    if risk != "All":
        mask &= df["Overall_Climate_Risk"] == risk
    out = df[mask]
    if out.empty:
        st.warning("No records match these filters. Please relax them.")
    return out


ANIMALS = df[df["Kingdom"] == "Animalia"] if (df["Kingdom"] == "Animalia").any() else df


def scenario_filter(key):
    """Scenario dropdown for View 1 / View 2. The views cover animals only (Animalia)."""
    c1, _ = st.columns([1, 2])
    scen = c1.selectbox("Climate scenario", ["All"] + sorted(ANIMALS["Climate_Scenario"].unique()), key=f"{key}_sc")
    return ANIMALS if scen == "All" else ANIMALS[ANIMALS["Climate_Scenario"] == scen]

def strongest(cs, ce, ca):
    """Name of the component most correlated (in absolute value) with vulnerability, plus a note if it is adaptation."""
    d = {"sensitivity": cs, "exposure": ce, "adaptation": ca}
    top = max(d, key=lambda k: abs(d[k]))
    note_ = " The weaker an animal's ability to adapt, the more vulnerable it tends to be." if top == "adaptation" else ""
    return top, note_


def paired_change(frame, col):
    """Each species appears once per scenario: compare the SAME species under SSP126 vs SSP585.
    Returns (share of species whose value is higher under SSP585, median change) or None."""
    if frame["Climate_Scenario"].nunique() < 2:
        return None
    pv = frame.pivot_table(index="Species_ID", columns="Climate_Scenario", values=col)
    if not {"SSP126", "SSP585"} <= set(pv.columns):
        return None
    diff = (pv["SSP585"] - pv["SSP126"]).dropna()
    if diff.empty:
        return None
    return float((diff > 0).mean() * 100), float(diff.median())


# ---------------------------------------------------------------- Data & Stats
def data_stats():
    f = view_filters("ds")
    if f.empty:
        return
    with st.container(border=True):
        st.markdown("#### Dataset description")
        st.markdown(DESCRIPTION)

    g1, g2 = st.columns([1, 1])
    with g1:
        cards([kpi_card("list", "Records", f"{len(f):,}", f"of {len(df):,} rows in the dataset", tone="cyan")])
    with g2:
        show(species_gauge(f["Species_ID"].nunique(), df["Species_ID"].nunique()), h=300, top=40)

    st.subheader("Data preview")
    table(f.head(10))

    st.subheader("Summary statistics")
    num_cols = ["Climate_Sensitivity", "Climate_Exposure", "Climate_Adaptation", "Climate_Vulnerability", "Ncells"]
    table(f[num_cols].describe().T.round(3))

    st.markdown("**Records per kingdom**")
    kc = f["Kingdom"].value_counts().reset_index()
    kc.columns = ["Kingdom", "Count"]
    fig = px.bar(kc, x="Kingdom", y="Count", color="Kingdom", text_auto=",")
    fig.update_traces(textposition="outside", cliponaxis=False)
    fig.update_layout(showlegend=False)
    show(fig, 360)
    st.caption("Animalia dominates the data, so overall averages mostly reflect animals.")

    A = ANIMALS
    st.subheader("Key takeaways")
    st.markdown("""
**Key patterns you discovered**

- The data is biased toward one kingdom, Animalia.
    - This affects the overall averages.
    - In modeling, the results would likely mostly reflect this kingdom, since it is the most represented.
- All species were assessed under two scenarios: high and low emissions.
- Climate change impact on animal habitats is higher under the high-emissions scenario.
    - The higher the emissions, the greater the impact on these areas.
    - Some impact is still seen under the low-emissions scenario, which is likely explained by the delayed response of the climate: gases emitted in the past remain in the atmosphere.

**Interesting relationships**

- Climate vulnerability is positively correlated with sensitivity (0.63) and exposure (0.59), and negatively correlated with adaptation (-0.83).
- Adaptation has the strongest relationship with vulnerability: the weaker a species' ability to adapt, the more vulnerable it tends to be.
- The correlation between the components themselves is weak to moderate (0.25 between sensitivity and exposure), so each component adds different information.
- This is correlation, not causation, and it does not reveal the formula used to calculate vulnerability.

**Any outliers**

- Using the IQR method, 3,192 values (6.4%) were flagged as outliers in climate sensitivity.
- Climate exposure had no outliers.
""")


def qa(question, *answers):
    """A question followed directly by its answer (computed from the current selection)."""
    st.subheader(question)
    for text in answers:
        if text:
            st.markdown(text)


def hist_kde(frame, col, color_by=None, nbins=20, title="", xlabel=""):
    """Histogram + smooth KDE line (like seaborn histplot(kde=True)), no box on top."""
    vals = frame[col].dropna()
    lo, hi = float(vals.min()), float(vals.max())
    size = (hi - lo) / nbins if hi > lo else 1.0
    if color_by:
        fig = px.histogram(frame, x=col, color=color_by, barmode="overlay", opacity=0.6,
                           color_discrete_map=SCEN_COLORS, title=title, labels={col: xlabel})
        groups = [(k, g[col].dropna(), SCEN_COLORS.get(k, "#5ccbf5")) for k, g in frame.groupby(color_by)]
    else:
        fig = px.histogram(frame, x=col, title=title, labels={col: xlabel}, color_discrete_sequence=["#6c6ff0"])
        groups = [(None, vals, "#5ccbf5")]
    fig.update_traces(xbins=dict(start=lo, end=hi, size=size), marker_line_color="rgba(255,255,255,.25)",
                      marker_line_width=0.5, selector=dict(type="histogram"))
    for name, v, colr in groups:
        v = np.asarray(v)
        if len(v) < 3 or v.std() == 0:
            continue
        n_total = len(v)
        if len(v) > 4000:
            v = np.random.default_rng(0).choice(v, 4000, replace=False)
        bw = 1.06 * v.std() * len(v) ** (-0.2)
        xs = np.linspace(lo, hi, 200)
        dens = np.exp(-0.5 * ((xs[:, None] - v[None, :]) / bw) ** 2).sum(axis=1) / (len(v) * bw * np.sqrt(2 * np.pi))
        fig.add_trace(go.Scatter(x=xs, y=dens * n_total * size, mode="lines", line=dict(color=colr, width=2.5),
                                 showlegend=False, hoverinfo="skip"))
    fig.update_yaxes(title_text="Count")
    return fig


def risk_box(frame, ycol, title, ylabel):
    """Box plot per overall risk class. With both scenarios selected it is split by scenario."""
    split = frame["Climate_Scenario"].nunique() > 1
    fig = px.box(frame, x="Overall_Climate_Risk", y=ycol, category_orders={"Overall_Climate_Risk": RISK_ORDER},
                 color="Climate_Scenario" if split else "Overall_Climate_Risk",
                 color_discrete_map=SCEN_COLORS if split else RISK_COLORS,
                 title=title + (" · by scenario" if split else ""),
                 labels={"Overall_Climate_Risk": "Overall climate risk", ycol: ylabel})
    fig.update_layout(showlegend=split)
    return fig


def corr_heatmap(frame, title):
    corr = frame[["Climate_Vulnerability", "Climate_Sensitivity", "Climate_Exposure", "Climate_Adaptation"]].corr().round(2)
    fig = px.imshow(corr, text_auto=True, zmin=-1, zmax=1, aspect="auto",
                    color_continuous_scale=[[0, "#ff5c7a"], [0.5, "#1d1d44"], [1, "#5ccbf5"]], title=title)
    fig.update_traces(textfont=dict(size=14))
    return fig


def outlier_sides(series):
    """(outliers below the lower fence, outliers above the upper fence) using 1.5 x IQR."""
    q1_, q3_ = series.quantile([0.25, 0.75])
    r_ = q3_ - q1_
    return int((series < q1_ - 1.5 * r_).sum()), int((series > q3_ + 1.5 * r_).sum())


def view_animal():
    f = scenario_filter("v1")
    if f.empty:
        return
    cards([
        kpi_card("pulse", "Avg sensitivity", f"{f['Climate_Sensitivity'].mean():.3f}",
                 "how much the animal itself is affected (0–1)", f["Climate_Sensitivity"].mean() * 100, tone="cyan"),
        kpi_card("shield", "Avg vulnerability", f"{f['Climate_Vulnerability'].mean():.3f}",
                 "combined result of sensitivity, exposure & adaptation", f["Climate_Vulnerability"].mean() * 100),
    ])

    # ---- Top 10 phyla
    top_ph = f["Phylum"].value_counts().head(10).index.tolist()
    vc = (f[f["Phylum"].isin(top_ph)].groupby(["Phylum", "Climate_Scenario"]).size()
          .reset_index(name="Records"))
    vc["Phylum"] = pd.Categorical(vc["Phylum"], categories=top_ph, ordered=True)
    vc = vc.sort_values(["Phylum", "Climate_Scenario"])
    top_row = f["Phylum"].value_counts()
    qa("Which phyla are the most represented?",
       f"**{top_row.index[0]}** is the most represented phylum, with {int(top_row.iloc[0]):,} records "
       "(each species appears twice in the data, once per climate scenario).")
    fig = px.bar(vc, x="Phylum", y="Records", color="Climate_Scenario", barmode="group", text_auto=",",
                 color_discrete_map=SCEN_COLORS, title="Top 10 phyla by count · by scenario")
    fig.update_traces(textposition="outside", cliponaxis=False)
    show(fig)

    # ---- Q1: how strongly is the animal affected (histogram + boxplot)
    sens = f["Climate_Sensitivity"]
    q1, q3 = sens.quantile([0.25, 0.75])
    iqr = q3 - q1
    lower, upper = q1 - 1.5 * iqr, q3 + 1.5 * iqr
    out_pct = ((sens < lower) | (sens > upper)).mean() * 100
    shape = "close to bell-shaped" if abs(sens.skew()) < 0.5 else "skewed"
    qa("How strongly is the animal itself affected by climate change?",
       f"The distribution of animal sensitivity is {shape}: mean {sens.mean():.2f} and median {sens.median():.2f}. Half of the "
       f"animals fall between {q1:.2f} and {q3:.2f}, so most are concentrated around the center, with a small standard "
       f"deviation ({sens.std():.2f}). Values range from {sens.min():.2f} to {sens.max():.2f}: very few animals have very low "
       "or very high sensitivity.",
       f"The boxplot makes the effect on the animal clearer and shows the outliers: {out_pct:.1f}% of records fall outside "
       f"the fences ({lower:.2f} to {upper:.2f}).")
    c1, c2 = st.columns([3, 2])
    with c1:
        show(hist_kde(f, "Climate_Sensitivity", color_by="Climate_Scenario", nbins=20, title="Distribution of climate sensitivity",
                      xlabel="Climate Sensitivity Score"))
    with c2:
        show(px.box(f, x="Climate_Sensitivity", y="Climate_Scenario", color="Climate_Scenario",
                    color_discrete_map=SCEN_COLORS, title="Boxplot of climate sensitivity",
                    labels={"Climate_Sensitivity": "Climate Sensitivity Score", "Climate_Scenario": ""}
                    ).update_layout(showlegend=False))

    # ---- Q2: sensitivity by overall risk class
    by_risk = (f.groupby("Overall_Climate_Risk")[["Climate_Sensitivity", "Climate_Exposure", "Climate_Adaptation"]]
               .mean().reindex(RISK_ORDER).dropna())
    ans3 = None
    if len(by_risk) > 1:
        a0, z0 = by_risk.iloc[0], by_risk.iloc[-1]
        ka, kz = by_risk.index[0], by_risk.index[-1]
        rising = by_risk["Climate_Sensitivity"].is_monotonic_increasing
        ans3 = ("The higher the overall risk class (N < M < H < C), the higher the animals' sensitivity to climate change"
                if rising else "Average sensitivity by overall risk class")
        ans3 += (f": from an average of {a0['Climate_Sensitivity']:.2f} in {ka} to {z0['Climate_Sensitivity']:.2f} in {kz}. "
                 f"Adaptation goes from {a0['Climate_Adaptation']:.2f} to {z0['Climate_Adaptation']:.2f}")
        together = rising and by_risk["Climate_Adaptation"].is_monotonic_decreasing
        ans3 += (", so high risk goes with animals that are more sensitive and less able to adapt." if together else ".")
    qa("Do animals with higher sensitivity fall into higher risk classes?", ans3)
    show(risk_box(f, "Climate_Sensitivity", "Climate sensitivity by overall climate risk", "Climate Sensitivity"))

    # ---- Q3: share of class H, SSP126 vs SSP585 (always both scenarios)
    pct = (f.assign(high=f["Overall_Climate_Risk"].eq("H"))
           .groupby("Climate_Scenario")["high"].mean().mul(100).reset_index())
    pm = pct.set_index("Climate_Scenario")["high"]
    ans_h = None
    if {"SSP126", "SSP585"} <= set(pm.index):
        dh = pm["SSP585"] - pm["SSP126"]
        effect = ("so a much larger share of species falls in the high-risk class when emissions are higher" if dh > 5
                  else "so a somewhat larger share of species falls in the high-risk class when emissions are higher" if dh > 0.5
                  else "so the share of species in the high-risk class does not increase with higher emissions" if dh > -0.5
                  else "so a smaller share of species falls in the high-risk class under higher emissions")
        ans_h = (f"The share of species classified in risk class H goes from about {pm['SSP126']:.0f}% under SSP126 to about "
                 f"{pm['SSP585']:.0f}% under SSP585, {effect}. This share covers class H only and does not include the "
                 "higher class C.")
    elif len(pm) == 1:
        ans_h = (f"Under {pm.index[0]}, about {pm.iloc[0]:.0f}% of species are classified in risk class H (class C is not "
                 "included). Choose 'All' in the scenario filter to compare SSP126 with SSP585.")
    qa("Does the share of species at high climate risk (H) increase under the higher-emissions scenario (SSP585) compared "
       "with the lower-emissions scenario (SSP126)?", ans_h)
    fig = px.bar(pct, x="Climate_Scenario", y="high", color="Climate_Scenario", color_discrete_map=SCEN_COLORS,
                 title="High climate risk (H) by scenario")
    fig.update_traces(texttemplate="%{y:.1f}%", textposition="outside", cliponaxis=False,
                      textfont=dict(size=14, color="#ffffff"))
    fig.update_yaxes(range=[0, 105], title_text="High risk species (%)")
    fig.update_layout(showlegend=False)
    show(fig)

    # ---- Q4: adaptation
    st.subheader("Which species have the lowest (and highest) capacity to adapt to climate change?")
    top_n = 5
    uniq = f.copy()
    uniq["Label"] = uniq["Species_Name"] + " (" + uniq["Climate_Scenario"].str.replace("SSP", "") + ")"
    low = uniq.nsmallest(top_n, "Climate_Adaptation")
    high = uniq.nlargest(top_n, "Climate_Adaptation")
    lo_min, lo_max, hi_max = low["Climate_Adaptation"].min(), low["Climate_Adaptation"].max(), high["Climate_Adaptation"].max()
    ratio = f" (about {hi_max / lo_min:.0f} times)" if lo_min > 0 else ""
    st.markdown(
        f"The lowest-adaptation species have values of around {lo_min:.2f} to {lo_max:.2f}, while the highest reach about "
        f"{hi_max:.1f}, a gap of about {hi_max - lo_min:.1f} points{ratio}. Low values mean a weak ability to adapt to "
        "climate change, which is a negative indicator for the animal. This comparison covers the extremes only and does "
        "not represent the overall distribution of adaptation.")
    c5, c6 = st.columns(2)
    with c5:
        fig = px.bar(low.sort_values("Climate_Adaptation", ascending=False), x="Climate_Adaptation",
                     y="Label", orientation="h", title="Lowest climate adaptation", text_auto=".2f",
                     color="Climate_Scenario", color_discrete_map=SCEN_COLORS)
        fig.update_traces(textposition="outside", cliponaxis=False, textfont=dict(size=13, color="#ffffff"))
        fig.update_xaxes(range=[0, max(low["Climate_Adaptation"].max() * 1.25, 0.05)])
        fig.update_yaxes(title_text="")
        fig.update_layout(legend_title_text="")
        show(fig, h=max(360, 62 * top_n + 130))
    with c6:
        fig = px.bar(high.sort_values("Climate_Adaptation"), x="Climate_Adaptation",
                     y="Label", orientation="h", title="Highest climate adaptation", text_auto=".2f",
                     color="Climate_Scenario", color_discrete_map=SCEN_COLORS)
        fig.update_traces(textposition="outside", cliponaxis=False, textfont=dict(size=13, color="#ffffff"))
        fig.update_xaxes(range=[0, min(high["Climate_Adaptation"].max() * 1.25, 1.05)])
        fig.update_yaxes(title_text="")
        fig.update_layout(legend_title_text="")
        show(fig, h=max(360, 62 * top_n + 130))

    # ---- Q5: vulnerability and its components
    c_a = f["Climate_Vulnerability"].corr(f["Climate_Adaptation"])
    c_s = f["Climate_Vulnerability"].corr(f["Climate_Sensitivity"])
    c_e = f["Climate_Vulnerability"].corr(f["Climate_Exposure"])
    pairs = [f["Climate_Sensitivity"].corr(f["Climate_Exposure"]), f["Climate_Sensitivity"].corr(f["Climate_Adaptation"]),
             f["Climate_Exposure"].corr(f["Climate_Adaptation"])]
    c_se = pairs[0]
    big = max(abs(p) for p in pairs)
    comp_desc = "weak" if big < 0.3 else "weak to moderate" if big < 0.7 else "moderate to strong"
    top_c, top_note = strongest(c_s, c_e, c_a)
    qa("How is climate vulnerability related to its components?",
       f"Climate vulnerability correlates positively with sensitivity ({c_s:.2f}) and exposure ({c_e:.2f}), and negatively with "
       f"adaptation ({c_a:.2f}). The strongest correlation is with {top_c}.{top_note} The correlations between the components "
       f"themselves are {comp_desc} ({c_se:.2f} between sensitivity and exposure), so each component adds different "
       "information. This is a correlation, not causation, and it does not reveal the formula used to compute vulnerability.")
    if f["Climate_Scenario"].nunique() > 1:
        h1, h2 = st.columns(2)
        for col_, (sc_, g_) in zip((h1, h2), f.groupby("Climate_Scenario")):
            with col_:
                show(corr_heatmap(g_, f"Correlations · {sc_}"), h=440)
    else:
        show(corr_heatmap(f, f"Correlations · {f['Climate_Scenario'].iloc[0]}"), h=440)


def view_habitat():
    f = scenario_filter("v2")
    if f.empty:
        return
    cards([
        kpi_card("thermo", "Avg exposure", f"{f['Climate_Exposure'].mean():.3f}",
                 "how much climate change hits the animal's habitat (0–1)", f["Climate_Exposure"].mean() * 100, tone="cyan"),
    ])

    # ---- Q1: exposure by scenario (histogram)
    mean_e = f.groupby("Climate_Scenario")["Climate_Exposure"].mean()
    ans = []
    if {"SSP126", "SSP585"} <= set(mean_e.index):
        de = mean_e["SSP585"] - mean_e["SSP126"]
        lead = ("Under the higher-emissions scenario (SSP585) the exposure score is higher, so the more emissions rise, the "
                "greater the effect on the regions where these animals live." if de > 0 else
                "Under the higher-emissions scenario (SSP585) the exposure score is not higher than under SSP126.")
        ans.append(f"{lead} The difference between the two scenarios in average exposure is {abs(de):.2f} "
                   f"({mean_e['SSP585']:.2f} under SSP585 vs {mean_e['SSP126']:.2f} under SSP126).")
    else:
        sc_name = f["Climate_Scenario"].iloc[0]
        ans.append(f"Average exposure under {sc_name} is {f['Climate_Exposure'].mean():.2f}.")
    if "SSP126" in set(mean_e.index) and mean_e["SSP126"] > 0.05:
        ans.append("Exposure also appears under the low-emissions scenario (SSP126). This is likely explained by the delayed "
                   "response of the climate: gases emitted in the past stay in the atmosphere and keep warming the oceans, so "
                   "climate change continues and animals are affected even when emissions fall.")
    qa("To what degree are the animals' regions affected by climate change?", *ans)
    show(hist_kde(f, "Climate_Exposure", color_by="Climate_Scenario", nbins=20,
                  title="Distribution of climate exposure by scenario", xlabel="Climate Exposure Score"))

    # ---- Q2: spread of exposure (boxplot per scenario)
    med_e = f.groupby("Climate_Scenario")["Climate_Exposure"].median()
    ans2 = []
    if {"SSP126", "SSP585"} <= set(med_e.index):
        ans2.append(f"Both scenarios show exposure in the animals' regions, but exposure values are clearly higher under SSP585 "
                    f"(median about {med_e['SSP585']:.2f} vs about {med_e['SSP126']:.2f} under SSP126).")
    else:
        ans2.append(f"The median exposure in the selected scenario is about {f['Climate_Exposure'].median():.2f}.")
    for sc, g in f.groupby("Climate_Scenario"):
        below, above = outlier_sides(g["Climate_Exposure"])
        if below == 0 and above == 0:
            where = "has no outliers"
        elif below == 0:
            where = "has outliers on the right only (animals with higher exposure than usual)"
        elif above == 0:
            where = "has outliers on the left only (animals with lower exposure than usual)"
        else:
            side = "left (lower than usual)" if below > above else "right (higher than usual)"
            where = f"has outliers on both sides, mostly on the {side}"
        ans2.append(f"{sc} {where} ({below} below, {above} above the fences).")
    qa("How widely is exposure spread across the animals' regions?", " ".join(ans2))
    show(px.box(f, x="Climate_Exposure", y="Climate_Scenario", color="Climate_Scenario", color_discrete_map=SCEN_COLORS,
                title="Boxplot of climate exposure by scenario",
                labels={"Climate_Exposure": "Climate Exposure Score", "Climate_Scenario": "Scenario"}
                ).update_layout(showlegend=False), h=340)

    # ---- Q3: range size vs sensitivity
    rho_s = f["Ncells"].rank().corr(f["Climate_Sensitivity"].rank())
    if rho_s <= -0.1:
        verdict = ("Animals with a small range (low Ncells) tend to have higher climate sensitivity, while animals spread over "
                   "wide areas are usually low to moderate in sensitivity.")
    elif rho_s >= 0.1:
        verdict = "Animals with a wide range tend to have higher climate sensitivity than animals with a small range."
    else:
        verdict = "There is no clear relationship between range size and climate sensitivity."
    qa("Are animals with a small range more sensitive?",
       f"{verdict} (Spearman correlation between Ncells and sensitivity: {rho_s:.2f}).")
    show(px.scatter(f, x="Ncells", y="Climate_Sensitivity", opacity=0.3, render_mode="webgl",
                    color="Climate_Scenario", color_discrete_map=SCEN_COLORS,
                    title="Relationship between species range and climate sensitivity",
                    labels={"Ncells": "Ncells (range size)", "Climate_Sensitivity": "Climate Sensitivity"}))

    # ---- Q4: exposure vs overall risk class
    exp_by_risk = f.groupby("Overall_Climate_Risk")["Climate_Exposure"].median().reindex(RISK_ORDER).dropna()
    ans_r = None
    if len(exp_by_risk) > 1:
        rising = exp_by_risk.is_monotonic_increasing
        ans_r = (("Yes: median exposure by overall risk class is " if rising else "Median exposure by overall risk class is ") + ", ".join(f"{k} {v:.2f}" for k, v in exp_by_risk.items())
                 + ("; regions facing stronger climate change fall in higher risk classes." if rising else "."))
    qa("Do the animals' regions facing stronger climate change (higher exposure) fall in higher risk classes?", ans_r)
    show(risk_box(f, "Climate_Exposure", "Climate exposure by overall climate risk", "Climate Exposure"))


if page == NAV[0][0]:
    view_animal()      # View 1
elif page == NAV[1][0]:
    view_habitat()     # View 2
else:
    data_stats()