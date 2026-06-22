"""
Agent Activity Dashboard — Streamlit
Tampilan semirip mungkin dengan HTML template (custom CSS).
Hierarki: All Segments → Segment → Campaign → Agent (4-level drill-down)

Kolom Google Sheet (output query_agent_activity.sql):
    grass_date, team_id, segment, campaign, teleid,
    leads_assign, start_call, end_call, hours_work, contact_duration,
    calls, contacts, unique_contacts, contacts_30s, contact_duration_30s,
    calls_0810..1618, contacts_0810..1618, unique_contacts_0810..1618,
    contacts_30s_0810..1618, contact_duration_30s_0810..1618
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# ─────────────────────────────────────────────────────────────────────────
# PAGE CONFIG
# ─────────────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Agent Activity Dashboard",
    page_icon="📞",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─────────────────────────────────────────────────────────────────────────
# CUSTOM CSS — mirrors HTML template design tokens & components
# ─────────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
/* ── Design tokens ── */
:root {
  --bg-page:#F5F4F0; --bg-surf:#FFF; --bg-muted:#F1EFE8; --bg-muted2:#E8E6DF;
  --txt:#1A1A18; --txt2:#5F5E5A; --txt3:#888780;
  --bdr:rgba(0,0,0,.10); --bdr2:rgba(0,0,0,.18);
  --r8:8px; --r12:12px;
  --blue:#378ADD; --blue-lt:#E6F1FB; --blue-dk:#0C447C;
  --green:#1D9E75; --green-lt:#EAF3DE; --green-dk:#3B6D11;
  --amber:#BA7517; --amber-lt:#FAEEDA; --amber-dk:#854F0B;
  --red:#A32D2D; --red-lt:#FCEBEB;
  --coral:#D85A30; --purple:#534AB7; --purple-lt:#EEEDFE;
  --shadow:0 1px 3px rgba(0,0,0,.07),0 1px 2px rgba(0,0,0,.04);
}
@media(prefers-color-scheme:dark){
  :root {
    --bg-page:#1C1C1A; --bg-surf:#252523; --bg-muted:#2C2C2A; --bg-muted2:#333330;
    --txt:#EEECEA; --txt2:#B4B2A9; --txt3:#888780;
    --bdr:rgba(255,255,255,.10); --bdr2:rgba(255,255,255,.18);
    --blue:#5EA8E8; --blue-lt:#0C2A42; --blue-dk:#85B7EB;
    --green:#3DC99A; --green-lt:#08261B; --green-dk:#97C459;
    --amber:#EF9F27; --amber-lt:#2B1E08; --amber-dk:#FAC775;
    --red:#E05454; --red-lt:#2A0D0D;
    --coral:#F0997B; --purple:#AFA9EC; --purple-lt:#26215C;
  }
}

/* ── Hide Streamlit chrome ── */
#MainMenu, footer, header { visibility: hidden; }
.block-container { padding-top: 1rem !important; }

/* ── Page background ── */
.stApp { background: var(--bg-page) !important; }

/* ── Sidebar ── */
[data-testid="stSidebar"] {
  background: var(--bg-surf) !important;
  border-right: .5px solid var(--bdr) !important;
}
[data-testid="stSidebar"] * { color: var(--txt) !important; }

/* ── KPI Card ── */
.kpi-card {
  background: var(--bg-surf);
  border: .5px solid var(--bdr);
  border-radius: var(--r12);
  padding: 13px 14px;
  box-shadow: var(--shadow);
  margin-bottom: 10px;
}
.kpi-label {
  font-size: 11px;
  color: var(--txt3);
  font-weight: 500;
  text-transform: uppercase;
  letter-spacing: .04em;
  margin-bottom: 6px;
}
.kpi-value {
  font-size: 24px;
  font-weight: 500;
  color: var(--txt);
  line-height: 1.1;
}
.kpi-value.green { color: var(--green-dk); }
.kpi-value.amber { color: var(--amber-dk); }
.kpi-value.red   { color: var(--red); }
.kpi-value.blue  { color: var(--blue); }

/* ── Section header ── */
.sec-header {
  font-size: 11px; font-weight: 500; color: var(--txt3);
  text-transform: uppercase; letter-spacing: .06em;
  margin: 18px 0 10px;
  display: flex; align-items: center; gap: 8px;
}
.sec-header::after {
  content: ""; flex: 1; height: .5px; background: var(--bdr);
}

/* ── Card wrapper ── */
.dash-card {
  background: var(--bg-surf);
  border: .5px solid var(--bdr);
  border-radius: var(--r12);
  padding: 14px 16px;
  box-shadow: var(--shadow);
  margin-bottom: 12px;
}
.card-title {
  font-size: 12px; font-weight: 500; color: var(--txt2);
  margin-bottom: 10px;
}

/* ── Badge ── */
.badge {
  display: inline-block;
  padding: 2px 8px;
  border-radius: 10px;
  font-size: 11px;
  font-weight: 500;
}
.badge-green { background: var(--green-lt); color: var(--green-dk); }
.badge-amber { background: var(--amber-lt); color: var(--amber-dk); }
.badge-red   { background: var(--red-lt);   color: var(--red); }
.badge-blue  { background: var(--blue-lt);  color: var(--blue-dk); }
.badge-purple{ background: var(--purple-lt);color: var(--purple); }

/* ── Mini progress bar ── */
.mbar { height: 4px; border-radius: 2px; background: var(--bg-muted2); overflow: hidden; margin-top: 3px; }
.mbar-fill { height: 100%; border-radius: 2px; }

/* ── Table ── */
.dash-table {
  width: 100%; border-collapse: collapse;
  font-size: 12px; font-family: inherit;
}
.dash-table th {
  font-weight: 500; color: var(--txt2); text-align: left;
  padding: 7px 10px;
  border-bottom: .5px solid var(--bdr2);
  font-size: 11px; white-space: nowrap;
  background: var(--bg-muted);
}
.dash-table td {
  padding: 8px 10px;
  border-bottom: .5px solid var(--bdr);
  color: var(--txt);
  vertical-align: middle;
}
.dash-table tr:last-child td { border-bottom: none; }
.dash-table tr:hover td { background: var(--bg-muted); }
.dash-table td.agent-name { font-weight: 500; color: var(--blue); }

/* ── Segment / Campaign card ── */
.seg-card {
  background: var(--bg-surf);
  border: .5px solid var(--bdr);
  border-radius: var(--r12);
  padding: 14px;
  box-shadow: var(--shadow);
  margin-bottom: 10px;
  transition: border-color .2s, box-shadow .2s;
}
.seg-card:hover {
  border-color: var(--blue);
  box-shadow: 0 0 0 3px var(--blue-lt);
}
.seg-card-name { font-size: 14px; font-weight: 500; margin-bottom: 4px; }
.seg-card-sub  { font-size: 11px; color: var(--txt3); margin-bottom: 10px; }
.tc-kpis { display: grid; grid-template-columns: 1fr 1fr; gap: 6px; }
.tc-kpi {
  background: var(--bg-muted);
  border-radius: var(--r8);
  padding: 7px 9px;
}
.tc-kpi-lbl { font-size: 10px; color: var(--txt3); margin-bottom: 1px; }
.tc-kpi-val { font-size: 15px; font-weight: 500; color: var(--txt); }

/* ── Breadcrumb ── */
.breadcrumb {
  background: var(--bg-surf);
  border: .5px solid var(--bdr);
  border-radius: var(--r12);
  padding: 8px 14px;
  display: flex; align-items: center; gap: 6px;
  font-size: 13px;
  margin-bottom: 14px;
  box-shadow: var(--shadow);
}
.bc-sep { color: var(--txt3); }
.bc-link { color: var(--blue); font-weight: 400; }
.bc-current { color: var(--txt); font-weight: 500; }

/* ── Filter pill ── */
.filter-pills { display: flex; gap: 6px; flex-wrap: wrap; margin-bottom: 12px; }
.f-pill {
  display: inline-flex; align-items: center; gap: 5px;
  font-size: 11px; padding: 3px 10px; border-radius: 20px;
  font-weight: 500;
  background: var(--blue-lt); color: var(--blue-dk);
  border: .5px solid var(--blue);
}

/* ── Footer note ── */
.dash-footer {
  font-size: 10px; color: var(--txt3); line-height: 2;
  padding: 12px 14px;
  background: var(--bg-surf);
  border: .5px solid var(--bdr);
  border-radius: var(--r12);
  margin-top: 20px;
}
.dash-footer strong { color: var(--txt2); }

/* ── Streamlit button override ── */
.stButton > button {
  background: var(--bg-surf) !important;
  border: .5px solid var(--bdr2) !important;
  border-radius: var(--r8) !important;
  color: var(--txt) !important;
  font-size: 12px !important;
  padding: 4px 12px !important;
  transition: background .15s !important;
}
.stButton > button:hover {
  background: var(--bg-muted) !important;
  border-color: var(--blue) !important;
}
.btn-primary > button {
  background: var(--blue) !important;
  color: #fff !important;
  border-color: var(--blue) !important;
}
.btn-primary > button:hover { opacity: .9 !important; }
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────────────────
# CONSTANTS
# ─────────────────────────────────────────────────────────────────────────
SHEET_CSV_URL = st.secrets.get("SHEET_CSV_URL", "")

SLOTS       = ["0810","1012","1214","1416","1618"]
SLOT_LABELS = ["08-10","10-12","12-14","14-16","16-18"]

REQUIRED_COLS = [
    "grass_date","team_id","segment","campaign","teleid",
    "leads_assign","start_call","end_call","hours_work","contact_duration",
    "calls","contacts","unique_contacts","contacts_30s","contact_duration_30s",
    *[f"{m}_{s}" for s in SLOTS
      for m in ("calls","contacts","unique_contacts","contacts_30s","contact_duration_30s")],
]
NUM_COLS = [c for c in REQUIRED_COLS
            if c not in ("grass_date","team_id","segment","campaign","teleid","start_call","end_call")]

SEG_COLORS = {
    "dropoff":     "#378ADD","risk":        "#A32D2D",
    "h5_approved": "#1D9E75","telkomsel":   "#534AB7",
    "megacc_point":"#BA7517","acquisition": "#D85A30","disbursement":"#0C447C",
}

def sc(seg): return SEG_COLORS.get(str(seg), "#888888")

def cr_class(r):
    if r >= 60: return "green"
    if r >= 40: return "amber"
    return "red"

def badge_html(val, cls="blue"):
    return f'<span class="badge badge-{cls}">{val}</span>'

def cr_badge(rate):
    return badge_html(f"{rate}%", cr_class(rate))

def mbar_html(pct, color):
    return (f'<div class="mbar"><div class="mbar-fill" '
            f'style="width:{min(pct,100):.0f}%;background:{color}"></div></div>')


# ─────────────────────────────────────────────────────────────────────────
# DATA LOADING
# ─────────────────────────────────────────────────────────────────────────
@st.cache_data(ttl=300, show_spinner="Memuat data dari Google Sheet...")
def load_data(url: str) -> pd.DataFrame:
    df = pd.read_csv(url)
    df.columns = [c.strip().lower() for c in df.columns]
    missing = [c for c in REQUIRED_COLS if c not in df.columns]
    if missing:
        raise ValueError(f"Kolom tidak ditemukan: {missing}")
    df["grass_date"] = pd.to_datetime(df["grass_date"]).dt.strftime("%Y-%m-%d")
    for col in ("team_id","segment","campaign","teleid"):
        df[col] = df[col].astype(str).str.strip()
    df["team_id"] = df["team_id"].str.replace(r"\.0$","",regex=True)
    df["start_call"] = df["start_call"].fillna("-").astype(str)
    df["end_call"]   = df["end_call"].fillna("-").astype(str)
    for c in NUM_COLS:
        df[c] = pd.to_numeric(df[c], errors="coerce").fillna(0)
    df["talk_hours"]       = (df["contact_duration"]/3600).round(3)
    df["connect_rate"]     = (df["contacts"]/df["calls"].replace(0,pd.NA)*100).fillna(0).round(1)
    df["connect_rate_30s"] = (df["contacts_30s"]/df["calls"].replace(0,pd.NA)*100).fillna(0).round(1)
    return df.rename(columns={"grass_date":"date","team_id":"team","teleid":"agent"})


def agg_summary(rows: pd.DataFrame) -> dict | None:
    if rows.empty: return None
    calls = rows["calls"].sum()
    cont  = rows["contacts"].sum()
    c30s  = rows["contacts_30s"].sum()
    return {
        "agents":           rows["agent"].nunique(),
        "calls":            int(calls),
        "contacts":         int(cont),
        "unique_contacts":  int(rows["unique_contacts"].sum()),
        "contacts_30s":     int(c30s),
        "connect_rate":     round(cont/calls*100,1) if calls>0 else 0.0,
        "connect_rate_30s": round(c30s/calls*100,1) if calls>0 else 0.0,
        "talk_hours_avg":   round(rows["talk_hours"].mean(),3),
        "talk_hours_total": round(rows["talk_hours"].sum(),3),
        "hours_work":       round(rows["hours_work"].mean(),2),
        "leads_assign":     int(rows["leads_assign"].sum()),
        **{f"calls_{s}":        int(rows[f"calls_{s}"].sum())        for s in SLOTS},
        **{f"contacts_{s}":     int(rows[f"contacts_{s}"].sum())     for s in SLOTS},
        **{f"contacts_30s_{s}": int(rows[f"contacts_30s_{s}"].sum()) for s in SLOTS},
    }


# ─────────────────────────────────────────────────────────────────────────
# LOAD
# ─────────────────────────────────────────────────────────────────────────
if not SHEET_CSV_URL:
    st.error("**SHEET_CSV_URL belum diset.**\n\n"
             "Tambahkan di `.streamlit/secrets.toml` atau **App settings → Secrets**:\n\n"
             '```toml\nSHEET_CSV_URL = "https://docs.google.com/spreadsheets/d/.../pub?output=csv"\n```')
    st.stop()

try:
    df = load_data(SHEET_CSV_URL)
except Exception as e:
    st.error(f"Gagal memuat data: {e}"); st.stop()

ALL_DATES    = sorted(df["date"].dropna().unique())
ALL_TEAMS    = sorted(df["team"].dropna().astype(str).unique())
ALL_SEGMENTS = sorted(df["segment"].dropna().astype(str).unique())


def frows(date=None, team=None, segment=None, campaign=None, agent=None):
    d = df
    if date     is not None: d = d[d["date"]     == date]
    if team     is not None: d = d[d["team"]     == team]
    if segment  is not None: d = d[d["segment"]  == segment]
    if campaign is not None: d = d[d["campaign"] == campaign]
    if agent    is not None: d = d[d["agent"]    == agent]
    return d


# ─────────────────────────────────────────────────────────────────────────
# SIDEBAR
# ─────────────────────────────────────────────────────────────────────────
st.sidebar.markdown("### 📞 Agent Activity Dashboard")
st.sidebar.caption("Data via Google Sheet · update manual harian")
st.sidebar.divider()

sel_date = st.sidebar.selectbox(
    "📅 Tanggal", list(reversed(ALL_DATES)),
    format_func=lambda d: f"{d} (Terbaru)" if d==ALL_DATES[-1] else d,
)
sel_team = st.sidebar.selectbox("👥 Team", ["Semua Team"] + ALL_TEAMS)
team_f   = None if sel_team=="Semua Team" else sel_team

base_seg = sorted(frows(team=team_f)["segment"].unique()) if team_f else ALL_SEGMENTS
sel_seg  = st.sidebar.selectbox("🗂️ Segment", ["Semua Segment"]+base_seg)
seg_f    = None if sel_seg=="Semua Segment" else sel_seg

base_camp   = sorted(frows(team=team_f,segment=seg_f)["campaign"].unique())
sel_camp    = st.sidebar.selectbox("📋 Campaign", ["Semua Campaign"]+base_camp)
camp_f      = None if sel_camp=="Semua Campaign" else sel_camp

st.sidebar.divider()
if st.sidebar.button("🔄 Refresh data", use_container_width=True):
    st.cache_data.clear(); st.rerun()
st.sidebar.caption(
    f"{len(ALL_DATES)} hari · {len(ALL_TEAMS)} team\n"
    f"{len(ALL_SEGMENTS)} segment · {df['campaign'].nunique()} campaign · {df['agent'].nunique()} agen"
)


# ─────────────────────────────────────────────────────────────────────────
# SESSION STATE
# ─────────────────────────────────────────────────────────────────────────
for k,v in [("level",0),("d_seg",None),("d_camp",None),("d_agent",None)]:
    if k not in st.session_state: st.session_state[k] = v


def go(level, seg=None, camp=None, agent=None):
    st.session_state.update({"level":level,"d_seg":seg,"d_camp":camp,"d_agent":agent})


# Sidebar shortcuts
if seg_f  and st.session_state.level==0:          go(1, seg_f, camp_f)
if camp_f and st.session_state.level<=1:           go(2, seg_f, camp_f)


# ─────────────────────────────────────────────────────────────────────────
# HEADER + BREADCRUMB
# ─────────────────────────────────────────────────────────────────────────
lv = st.session_state.level

# Build breadcrumb HTML
parts = [('<span class="bc-link" style="cursor:default">🏠 All Segments</span>'
          if lv==0 else '<span class="bc-link">🏠 All Segments</span>')]
if lv >= 1 and st.session_state.d_seg:
    seg_lbl = f"🗂️ {st.session_state.d_seg}"
    parts.append(f'<span class="bc-sep">›</span>')
    parts.append(f'<span class="bc-{"current" if lv==1 else "link"}">{seg_lbl}</span>')
if lv >= 2 and st.session_state.d_camp:
    parts.append(f'<span class="bc-sep">›</span>')
    parts.append(f'<span class="bc-{"current" if lv==2 else "link"}">'
                 f'📋 {st.session_state.d_camp}</span>')
if lv == 3 and st.session_state.d_agent:
    parts.append(f'<span class="bc-sep">›</span>')
    parts.append(f'<span class="bc-current">🧑 {st.session_state.d_agent}</span>')

st.markdown(f'<div class="breadcrumb">{"".join(parts)}</div>', unsafe_allow_html=True)

# Navigation buttons
nav_cols = st.columns([1,1.4,2.2,2,6])
with nav_cols[0]:
    if st.button("🏠 All", use_container_width=True): go(0); st.rerun()
if lv >= 1 and st.session_state.d_seg:
    with nav_cols[1]:
        if st.button(f"↩ {st.session_state.d_seg}", use_container_width=True):
            go(1, st.session_state.d_seg); st.rerun()
if lv >= 2 and st.session_state.d_camp:
    with nav_cols[2]:
        if st.button(f"↩ {st.session_state.d_camp}", use_container_width=True):
            go(2, st.session_state.d_seg, st.session_state.d_camp); st.rerun()

# Filter pills
pills = []
if team_f:  pills.append(f'<span class="f-pill">👥 Team {team_f}</span>')
if seg_f:   pills.append(f'<span class="f-pill">🗂️ {seg_f}</span>')
if camp_f:  pills.append(f'<span class="f-pill">📋 {camp_f}</span>')
if pills:
    st.markdown(f'<div class="filter-pills">{"".join(pills)}</div>', unsafe_allow_html=True)

st.markdown("---")


# ─────────────────────────────────────────────────────────────────────────
# COMPONENT HELPERS
# ─────────────────────────────────────────────────────────────────────────
def render_kpi_grid(items: list[tuple]):
    """items = [(label, value, color_class?), ...]"""
    n = len(items)
    cols = st.columns(n)
    for col, item in zip(cols, items):
        lbl = item[0]; val = str(item[1]); cls = item[2] if len(item)>2 else ""
        with col:
            st.markdown(
                f'<div class="kpi-card">'
                f'<div class="kpi-label">{lbl}</div>'
                f'<div class="kpi-value {cls}">{val}</div>'
                f'</div>', unsafe_allow_html=True
            )


def render_section(title: str):
    st.markdown(f'<div class="sec-header">{title}</div>', unsafe_allow_html=True)


def plotly_defaults(fig, height=280):
    fig.update_layout(
        height=height, margin=dict(t=30,b=10,l=10,r=10),
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        font=dict(size=11, color="#5F5E5A"),
        legend=dict(orientation="h", y=1.15, font=dict(size=10)),
        xaxis=dict(gridcolor="rgba(128,128,128,.12)", tickfont=dict(size=10)),
        yaxis=dict(gridcolor="rgba(128,128,128,.12)", tickfont=dict(size=10)),
    )
    return fig


def slot_chart(s: dict, n_agents: int, color: str, height=260):
    n = max(n_agents,1)
    fig = go.Figure()
    fig.add_bar(name="Calls",         x=SLOT_LABELS, y=[s[f"calls_{sl}"]/n        for sl in SLOTS], marker_color=color+"55")
    fig.add_bar(name="Contacts",      x=SLOT_LABELS, y=[s[f"contacts_{sl}"]/n     for sl in SLOTS], marker_color=color+"99")
    fig.add_bar(name="Contacts ≥30s", x=SLOT_LABELS, y=[s[f"contacts_30s_{sl}"]/n for sl in SLOTS], marker_color=color)
    fig.update_layout(barmode="group", xaxis_title=None, yaxis_title="Avg/agent")
    return plotly_defaults(fig, height)


def trend_chart(data: list[dict], color: str, height=260):
    tdf = pd.DataFrame(data)
    fig = go.Figure()
    fig.add_scatter(x=tdf["date"],y=tdf["cr"],   name="CR %",     mode="lines+markers",
                    line=dict(color=color,width=2),
                    marker=dict(size=5,color=color,line=dict(color="#fff",width=1.5)))
    fig.add_scatter(x=tdf["date"],y=tdf["cr30"], name="CR ≥30s %", mode="lines+markers",
                    line=dict(color=color,dash="dot",width=1.5),
                    marker=dict(size=4,color=color))
    fig.update_yaxes(range=[0,100], ticksuffix="%")
    return plotly_defaults(fig, height)


def build_trend(date_f, team_f, seg, camp=None):
    result = []
    for d in ALL_DATES:
        r  = frows(date=d, team=team_f, segment=seg, campaign=camp)
        ts = agg_summary(r)
        result.append({"date":d,
                        "cr":  ts["connect_rate"]     if ts else None,
                        "cr30":ts["connect_rate_30s"] if ts else None})
    return result


def render_agent_table(rows: pd.DataFrame, key_sfx: str, seg: str, camp: str):
    """HTML table with badge + mbar, plus selectbox drill."""
    if rows.empty:
        st.info("Tidak ada agen yang sesuai."); return

    color = sc(seg)
    sorted_rows = rows.sort_values("calls", ascending=False)
    max_calls   = max(sorted_rows["calls"].max(), 1)

    # Build HTML table
    headers = ["Agent","Start","End","Calls","Contacts","Uniq","Cont≥30s","CR %","CR≥30s %","Talk (hrs)","Leads"]
    th_html = "".join(f"<th>{h}</th>" for h in headers)

    rows_html = []
    for _, r in sorted_rows.iterrows():
        pct   = r["calls"] / max_calls * 100
        cr_b  = cr_badge(r["connect_rate"])
        cr30_b= cr_badge(r["connect_rate_30s"])
        rows_html.append(f"""<tr>
          <td class="agent-name">{r['agent']}</td>
          <td>{r['start_call']}</td>
          <td>{r['end_call']}</td>
          <td>{int(r['calls'])}<br>{mbar_html(pct, color)}</td>
          <td>{int(r['contacts'])}</td>
          <td>{int(r['unique_contacts'])}</td>
          <td>{int(r['contacts_30s'])}</td>
          <td>{cr_b}</td>
          <td>{cr30_b}</td>
          <td>{r['talk_hours']:.3f}</td>
          <td>{int(r['leads_assign'])}</td>
        </tr>""")

    table_html = (f'<div class="dash-card" style="overflow-x:auto">'
                  f'<table class="dash-table"><thead><tr>{th_html}</tr></thead>'
                  f'<tbody>{"".join(rows_html)}</tbody></table></div>')
    st.markdown(table_html, unsafe_allow_html=True)

    st.caption("Pilih agen untuk detail:")
    c1, c2 = st.columns([3,1])
    sel = c1.selectbox("", sorted_rows["agent"].tolist(), key=f"asel_{key_sfx}", label_visibility="collapsed")
    with c2:
        if st.button("Detail →", key=f"abtn_{key_sfx}", use_container_width=True):
            go(3, seg, camp, sel); st.rerun()


def render_entity_cards(entity_rows: list[dict], id_col: str, on_click):
    """Generic card grid — used for both segments and campaigns."""
    cols = st.columns(3)
    for i, row in enumerate(entity_rows):
        color = sc(row.get("segment", row.get(id_col,"")))
        with cols[i % 3]:
            cr_c = cr_class(row["connect_rate"])
            st.markdown(f"""
            <div class="seg-card">
              <div class="seg-card-name" style="color:{color}">{row[id_col]}</div>
              <div class="seg-card-sub">{row.get('agents',0)} agents · {row.get('campaigns_cnt','')}</div>
              <div class="tc-kpis">
                <div class="tc-kpi">
                  <div class="tc-kpi-lbl">Calls</div>
                  <div class="tc-kpi-val">{row['calls']:,}</div>
                </div>
                <div class="tc-kpi">
                  <div class="tc-kpi-lbl">Connect Rate</div>
                  <div class="tc-kpi-val" style="color:var(--{cr_c}-dk)">{row['connect_rate']}%</div>
                </div>
                <div class="tc-kpi">
                  <div class="tc-kpi-lbl">CR ≥30s</div>
                  <div class="tc-kpi-val">{row['connect_rate_30s']}%</div>
                </div>
                <div class="tc-kpi">
                  <div class="tc-kpi-lbl">Talk (hrs avg)</div>
                  <div class="tc-kpi-val">{row['talk_hours_avg']}</div>
                </div>
              </div>
            </div>""", unsafe_allow_html=True)
            if st.button("Detail →", key=f"card_{id_col}_{i}", use_container_width=True):
                on_click(row); st.rerun()


def render_ranking_table(entity_rows: list[dict], id_col: str, label: str):
    """HTML ranking table with badges."""
    if not entity_rows: return
    headers = [label,"Agents","Calls","Contacts","Uniq Contacts","Cont≥30s","CR %","CR≥30s %","Talk (hrs avg)"]
    th_html = "".join(f"<th>{h}</th>" for h in headers)
    rhtml = []
    for r in sorted(entity_rows, key=lambda x: x["calls"], reverse=True):
        color  = sc(r.get("segment", r.get(id_col,"")))
        max_c  = max(max((x["calls"] for x in entity_rows),default=1),1)
        pct    = r["calls"]/max_c*100
        rhtml.append(f"""<tr>
          <td style="font-weight:500;color:{color}">{r[id_col]}</td>
          <td>{r['agents']}</td>
          <td>{r['calls']:,}{mbar_html(pct,color)}</td>
          <td>{r['contacts']:,}</td>
          <td>{r['unique_contacts']:,}</td>
          <td>{r['contacts_30s']:,}</td>
          <td>{cr_badge(r['connect_rate'])}</td>
          <td>{cr_badge(r['connect_rate_30s'])}</td>
          <td>{r['talk_hours_avg']}</td>
        </tr>""")
    st.markdown(
        f'<div class="dash-card" style="overflow-x:auto">'
        f'<table class="dash-table"><thead><tr>{th_html}</tr></thead>'
        f'<tbody>{"".join(rhtml)}</tbody></table></div>',
        unsafe_allow_html=True,
    )


# ─────────────────────────────────────────────────────────────────────────
# LEVEL 0 — ALL SEGMENTS OVERVIEW
# ─────────────────────────────────────────────────────────────────────────
def render_level0():
    render_section("Overall Summary")
    rows = frows(date=sel_date, team=team_f, segment=seg_f, campaign=camp_f)
    s    = agg_summary(rows)
    if not s: st.info("Tidak ada data untuk filter yang dipilih."); return

    render_kpi_grid([
        ("Agents",          s["agents"]),
        ("Total Calls",     f"{s['calls']:,}"),
        ("Contacts",        f"{s['contacts']:,}"),
        ("Unique Contacts", f"{s['unique_contacts']:,}"),
        ("Contacts ≥30s",   f"{s['contacts_30s']:,}"),
        ("Connect Rate",    f"{s['connect_rate']}%",    cr_class(s["connect_rate"])),
        ("CR ≥30s",         f"{s['connect_rate_30s']}%",cr_class(s["connect_rate_30s"])),
        ("Talk (hrs avg)",  f"{s['talk_hours_avg']}",   "blue"),
    ])

    seg_rows = []
    for sg in ALL_SEGMENTS:
        r = frows(date=sel_date, team=team_f, segment=sg, campaign=camp_f)
        ss = agg_summary(r)
        if ss:
            ss["segment"] = sg
            ss["campaigns_cnt"] = f"{r['campaign'].nunique()} campaigns"
            seg_rows.append(ss)
    seg_rows.sort(key=lambda x: x["calls"], reverse=True)

    c1, c2 = st.columns(2)
    with c1:
        sdf = pd.DataFrame(seg_rows)
        fig = px.bar(sdf, x="segment", y="calls", color="segment",
                     color_discrete_map={sg: sc(sg) for sg in ALL_SEGMENTS}, title="Calls by Segment")
        fig.update_layout(showlegend=False)
        st.plotly_chart(plotly_defaults(fig), use_container_width=True)
    with c2:
        fig = px.bar(sdf, x="segment", y="connect_rate", color="connect_rate",
                     color_continuous_scale=["#A32D2D","#BA7517","#1D9E75"],
                     range_color=[0,100], title="Connect Rate by Segment")
        fig.update_layout(showlegend=False, coloraxis_showscale=False)
        st.plotly_chart(plotly_defaults(fig), use_container_width=True)

    render_section("Segment Ranking")
    render_ranking_table(seg_rows, "segment", "Segment")

    render_section("Segment Overview")
    render_entity_cards(seg_rows, "segment", lambda row: go(1, row["segment"]))


# ─────────────────────────────────────────────────────────────────────────
# LEVEL 1 — SEGMENT → CAMPAIGNS
# ─────────────────────────────────────────────────────────────────────────
def render_level1():
    seg   = st.session_state.d_seg
    color = sc(seg)
    st.markdown(f'<h3 style="color:{color};margin-bottom:4px">🗂️ Segment: {seg}</h3>', unsafe_allow_html=True)

    rows = frows(date=sel_date, team=team_f, segment=seg, campaign=camp_f)
    s    = agg_summary(rows)
    if not s: st.info("Tidak ada data."); return

    render_kpi_grid([
        ("Agents",          s["agents"]),
        ("Calls",           f"{s['calls']:,}"),
        ("Contacts",        f"{s['contacts']:,}"),
        ("Unique Contacts", f"{s['unique_contacts']:,}"),
        ("Contacts ≥30s",   f"{s['contacts_30s']:,}"),
        ("Connect Rate",    f"{s['connect_rate']}%",    cr_class(s["connect_rate"])),
        ("CR ≥30s",         f"{s['connect_rate_30s']}%",cr_class(s["connect_rate_30s"])),
        ("Talk (hrs avg)",  f"{s['talk_hours_avg']}",   "blue"),
    ])

    c1, c2 = st.columns(2)
    with c1:
        st.markdown('<div class="card-title">Calls / Contacts by Slot (Segment Avg)</div>', unsafe_allow_html=True)
        st.plotly_chart(slot_chart(s, s["agents"], color), use_container_width=True)
    with c2:
        st.markdown('<div class="card-title">Connect Rate Trend (10-Day)</div>', unsafe_allow_html=True)
        st.plotly_chart(trend_chart(build_trend(sel_date, team_f, seg, camp_f), color), use_container_width=True)

    camps = sorted(frows(date=sel_date, team=team_f, segment=seg)["campaign"].unique())
    camp_rows = []
    for c in camps:
        r = frows(date=sel_date, team=team_f, segment=seg, campaign=c)
        cs = agg_summary(r)
        if cs:
            cs["campaign"] = c
            cs["segment"]  = seg
            cs["campaigns_cnt"] = ""
            camp_rows.append(cs)

    render_section("Campaign Ranking")
    render_ranking_table(camp_rows, "campaign", "Campaign")

    render_section("Campaign Overview")
    render_entity_cards(camp_rows, "campaign", lambda row: go(2, seg, row["campaign"]))


# ─────────────────────────────────────────────────────────────────────────
# LEVEL 2 — CAMPAIGN → AGENTS
# ─────────────────────────────────────────────────────────────────────────
def render_level2():
    seg   = st.session_state.d_seg
    camp  = st.session_state.d_camp
    color = sc(seg)

    st.markdown(
        f'<h3 style="margin-bottom:2px">📋 Campaign: {camp}</h3>'
        f'<p style="font-size:12px;color:var(--txt3);margin-bottom:12px">Segment: '
        f'<span style="color:{color};font-weight:500">{seg}</span></p>',
        unsafe_allow_html=True,
    )

    rows = frows(date=sel_date, team=team_f, segment=seg, campaign=camp)
    s    = agg_summary(rows)
    if not s: st.info("Tidak ada data."); return

    render_kpi_grid([
        ("Agents",          s["agents"]),
        ("Calls",           f"{s['calls']:,}"),
        ("Contacts",        f"{s['contacts']:,}"),
        ("Unique Contacts", f"{s['unique_contacts']:,}"),
        ("Contacts ≥30s",   f"{s['contacts_30s']:,}"),
        ("Connect Rate",    f"{s['connect_rate']}%",    cr_class(s["connect_rate"])),
        ("CR ≥30s",         f"{s['connect_rate_30s']}%",cr_class(s["connect_rate_30s"])),
        ("Talk (hrs avg)",  f"{s['talk_hours_avg']}",   "blue"),
    ])

    c1, c2 = st.columns(2)
    with c1:
        st.markdown('<div class="card-title">Calls / Contacts by Slot (Campaign Avg)</div>', unsafe_allow_html=True)
        st.plotly_chart(slot_chart(s, s["agents"], color), use_container_width=True)
    with c2:
        st.markdown('<div class="card-title">Connect Rate Trend (10-Day)</div>', unsafe_allow_html=True)
        st.plotly_chart(trend_chart(build_trend(sel_date, team_f, seg, camp), color), use_container_width=True)

    render_section("Agent Detail")
    tab_all, tab_low, tab_top = st.tabs(["All", "⚠️ Low CR (<40%)", "🏆 Top (CR ≥70%)"])
    with tab_all: render_agent_table(rows,                                             "all", seg, camp)
    with tab_low: render_agent_table(rows[rows["connect_rate"]<40],                   "low", seg, camp)
    with tab_top: render_agent_table(rows[rows["connect_rate"]>=70]
                                     .sort_values("connect_rate",ascending=False),     "top", seg, camp)


# ─────────────────────────────────────────────────────────────────────────
# LEVEL 3 — AGENT DETAIL
# ─────────────────────────────────────────────────────────────────────────
def render_level3():
    seg   = st.session_state.d_seg
    camp  = st.session_state.d_camp
    agent = st.session_state.d_agent
    color = sc(seg)

    hist    = df[df["agent"]==agent].sort_values("date")
    today_r = hist[hist["date"]==sel_date]
    t       = today_r.iloc[0] if not today_r.empty else hist.iloc[-1]

    # Header
    st.markdown(
        f'<h3 style="margin-bottom:2px">🧑 {agent}</h3>'
        f'<p style="font-size:12px;color:var(--txt3);margin-bottom:14px">'
        f'Segment: <span style="color:{color};font-weight:500">{t["segment"]}</span> · '
        f'Campaign: <strong>{t["campaign"]}</strong></p>',
        unsafe_allow_html=True,
    )

    col_prof, col_trend = st.columns([1, 2])

    with col_prof:
        rows_info = [
            ("Date",            t["date"]),
            ("Start Call",      t["start_call"]),
            ("End Call",        t["end_call"]),
            ("Hours Work",      f"{t['hours_work']:.2f} hrs"),
            ("Calls",           int(t["calls"])),
            ("Contacts",        int(t["contacts"])),
            ("Unique Contacts", int(t["unique_contacts"])),
            ("Contacts ≥30s",   int(t["contacts_30s"])),
            ("Connect Rate",    f"{t['connect_rate']}%"),
            ("CR ≥30s",         f"{t['connect_rate_30s']}%"),
            ("Talk Time",       f"{t['talk_hours']:.3f} hrs"),
            ("Leads Assigned",  int(t["leads_assign"])),
        ]
        rows_html = "".join(
            f'<tr><td style="color:var(--txt2);padding:6px 0;border-bottom:.5px solid var(--bdr);font-size:12px">{l}</td>'
            f'<td style="font-weight:500;padding:6px 0;border-bottom:.5px solid var(--bdr);font-size:12px;text-align:right">{v}</td></tr>'
            for l,v in rows_info
        )
        st.markdown(
            f'<div class="dash-card"><table style="width:100%;border-collapse:collapse">'
            f'<tbody>{rows_html}</tbody></table></div>',
            unsafe_allow_html=True,
        )

    with col_trend:
        fig = go.Figure()
        fig.add_bar(x=hist["date"], y=hist["calls"], name="Calls", marker_color=color+"80")
        fig.add_scatter(x=hist["date"], y=hist["connect_rate"],     name="CR %",     yaxis="y2",
                        mode="lines+markers", line=dict(color="#1D9E75",width=2),
                        marker=dict(size=5,color="#1D9E75",line=dict(color="#fff",width=1.5)))
        fig.add_scatter(x=hist["date"], y=hist["connect_rate_30s"], name="CR≥30s %", yaxis="y2",
                        mode="lines+markers", line=dict(color="#1D9E75",dash="dot",width=1.5),
                        marker=dict(size=4,color="#1D9E75"))
        fig.update_layout(
            yaxis=dict(title="Calls",  gridcolor="rgba(128,128,128,.12)", tickfont=dict(size=10)),
            yaxis2=dict(title="CR %",  overlaying="y", side="right", range=[0,100],
                        gridcolor="rgba(0,0,0,0)", tickfont=dict(size=10), ticksuffix="%"),
        )
        plotly_defaults(fig, height=320)
        fig.update_layout(title="10-Day Trend")
        st.plotly_chart(fig, use_container_width=True)

    render_kpi_grid([
        ("Calls",           int(t["calls"])),
        ("Contacts",        int(t["contacts"])),
        ("Unique Contacts", int(t["unique_contacts"])),
        ("Contacts ≥30s",   int(t["contacts_30s"])),
        ("Connect Rate",    f"{t['connect_rate']}%",    cr_class(t["connect_rate"])),
        ("CR ≥30s",         f"{t['connect_rate_30s']}%",cr_class(t["connect_rate_30s"])),
        ("Talk (hrs)",      f"{t['talk_hours']:.3f}",   "blue"),
    ])

    render_section("Calls by Time Slot (Today)")
    slot_s = {f"calls_{s}":        int(t[f"calls_{s}"])        for s in SLOTS}
    slot_s.update({f"contacts_{s}":     int(t[f"contacts_{s}"])     for s in SLOTS})
    slot_s.update({f"contacts_30s_{s}": int(t[f"contacts_30s_{s}"]) for s in SLOTS})
    st.plotly_chart(slot_chart(slot_s, 1, color, height=240), use_container_width=True)


# ─────────────────────────────────────────────────────────────────────────
# ROUTER
# ─────────────────────────────────────────────────────────────────────────
lv = st.session_state.level
if   lv==0: render_level0()
elif lv==1: render_level1()
elif lv==2: render_level2()
elif lv==3: render_level3()

# Export + footer
st.markdown("---")
with st.expander("📥 Export CSV"):
    exp = frows(
        date=sel_date, team=team_f,
        segment=st.session_state.d_seg   if lv>=1 else seg_f,
        campaign=st.session_state.d_camp if lv>=2 else camp_f,
        agent=st.session_state.d_agent   if lv==3 else None,
    )
    st.download_button("Download CSV", exp.to_csv(index=False).encode("utf-8-sig"),
                       file_name=f"agent_activity_{sel_date}.csv", mime="text/csv")

st.markdown(
    '<div class="dash-footer"><strong>Field Mapping</strong> · '
    'connect_rate = contacts/calls×100 · '
    'connect_rate_30s = contacts_30s/calls×100 · '
    'talk_hours = contact_duration/3600 · '
    'time slots: 08-10 / 10-12 / 12-14 / 14-16 / 16-18</div>',
    unsafe_allow_html=True,
)
