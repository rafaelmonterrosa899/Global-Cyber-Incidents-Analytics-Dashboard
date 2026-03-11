import streamlit as st
import pandas as pd
from databricks import sql
import plotly.express as px
import plotly.graph_objects as go
import numpy as np

# ─────────────────────────────────────────────
# PAGE CONFIG
# ─────────────────────────────────────────────
st.set_page_config(
    page_title="Cyber Incidents — Control Panel",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ─────────────────────────────────────────────
# THEME TOGGLE (stored in session state)
# ─────────────────────────────────────────────
if "theme" not in st.session_state:
    st.session_state.theme = "dark"

def _toggle_theme():
    st.session_state.theme = "light" if st.session_state._light_toggle else "dark"

st.sidebar.markdown("### 🎨 Appearance")
st.sidebar.toggle(
    "☀️ Light Mode",
    value=st.session_state.theme == "light",
    key="_light_toggle",
    on_change=_toggle_theme,
)
is_dark = st.session_state.theme == "dark"

# ─────────────────────────────────────────────
# THEME PALETTE
# ─────────────────────────────────────────────
if is_dark:
    T = {
        "bg": "#0a0e17",
        "surface": "#111827",
        "surface2": "#0f1623",
        "surface3": "#0d1220",
        "border": "rgba(255,255,255,0.04)",
        "border_hover": "rgba(212,175,55,0.2)",
        "text_primary": "#f1f5f9",
        "text_secondary": "#cbd5e1",
        "text_muted": "#64748b",
        "text_dim": "#475569",
        "kpi_value": "#ffffff",
        "kpi_label": "#94a3b8",
        "kpi_sub": "#64748b",
        "sidebar_bg": "linear-gradient(180deg, #0d1220 0%, #0a0e17 100%)",
        "sidebar_border": "rgba(212, 175, 55, 0.15)",
        "sidebar_label": "#8a93a6",
        "gold": "#d4af37",
        "gold_light": "#f5d76e",
        "land": "#111827",
        "ocean": "#080c14",
        "coast": "#1e293b",
        "plotly_tpl": "plotly_dark",
        "plotly_font": "#94a3b8",
        "scrollbar_track": "#0a0e17",
        "scrollbar_thumb": "#1e293b",
        "footer_color": "#334155",
        "panel_tag_bg": "rgba(212,175,55,0.08)",
        "panel_tag_border": "rgba(212,175,55,0.15)",
        "expander_color": "#d4af37",
    }
else:
    T = {
        "bg": "#f8fafc",
        "surface": "#ffffff",
        "surface2": "#f1f5f9",
        "surface3": "#e2e8f0",
        "border": "rgba(0,0,0,0.08)",
        "border_hover": "rgba(212,175,55,0.35)",
        "text_primary": "#0f172a",
        "text_secondary": "#334155",
        "text_muted": "#64748b",
        "text_dim": "#94a3b8",
        "kpi_value": "#0f172a",
        "kpi_label": "#475569",
        "kpi_sub": "#94a3b8",
        "sidebar_bg": "linear-gradient(180deg, #f1f5f9 0%, #f8fafc 100%)",
        "sidebar_border": "rgba(212,175,55,0.25)",
        "sidebar_label": "#475569",
        "gold": "#b8941f",
        "gold_light": "#d4af37",
        "land": "#e2e8f0",
        "ocean": "#f1f5f9",
        "coast": "#cbd5e1",
        "plotly_tpl": "plotly_white",
        "plotly_font": "#475569",
        "scrollbar_track": "#f1f5f9",
        "scrollbar_thumb": "#cbd5e1",
        "footer_color": "#94a3b8",
        "panel_tag_bg": "rgba(212,175,55,0.12)",
        "panel_tag_border": "rgba(212,175,55,0.3)",
        "expander_color": "#b8941f",
    }

# ─────────────────────────────────────────────
# CUSTOM CSS (themed)
# ─────────────────────────────────────────────
st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700;800;900&family=JetBrains+Mono:wght@400;500;600&display=swap');

*, *::before, *::after {{ box-sizing: border-box; }}

.stApp {{
    background: {T['bg']};
    font-family: 'Outfit', sans-serif;
}}

.block-container {{
    padding-top: 1.5rem !important;
    padding-bottom: 0 !important;
    max-width: 100% !important;
}}

/* Sidebar */
section[data-testid="stSidebar"] {{
    background: {T['sidebar_bg']};
    border-right: 1px solid {T['sidebar_border']};
}}
section[data-testid="stSidebar"] .stMarkdown h3,
section[data-testid="stSidebar"] .stMarkdown h2 {{
    color: {T['gold']} !important;
    font-family: 'Outfit', sans-serif;
    font-weight: 700;
}}
section[data-testid="stSidebar"] label {{
    color: {T['sidebar_label']} !important;
    font-family: 'Outfit', sans-serif;
}}

/* Top Bar */
.top-bar {{
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 8px 0 20px 0;
    border-bottom: 1px solid {T['border']};
    margin-bottom: 24px;
}}
.top-bar-left h1 {{
    font-family: 'Outfit', sans-serif;
    font-weight: 900;
    font-size: 1.7rem;
    margin: 0;
    background: linear-gradient(135deg, {T['gold']} 0%, {T['gold_light']} 50%, {T['gold']} 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}}
.top-bar-left p {{
    color: {T['text_muted']};
    font-size: 0.8rem;
    margin: 2px 0 0 0;
    letter-spacing: 2px;
    text-transform: uppercase;
}}
.breadcrumb {{
    color: {T['text_muted']};
    font-size: 0.78rem;
    font-family: 'JetBrains Mono', monospace;
}}
.breadcrumb span {{ color: {T['gold']}; }}

/* KPI Cards */
.kpi-row {{
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 16px;
    margin-bottom: 24px;
}}
.kpi-card {{
    background: linear-gradient(135deg, {T['surface']} 0%, {T['surface2']} 100%);
    border: 1px solid {T['border']};
    border-radius: 18px;
    padding: 22px 20px;
    position: relative;
    overflow: hidden;
    transition: all 0.35s cubic-bezier(0.4, 0, 0.2, 1);
}}
.kpi-card:hover {{
    transform: translateY(-4px);
    border-color: {T['border_hover']};
    box-shadow: 0 12px 40px rgba(0,0,0,{'0.4' if is_dark else '0.08'});
}}
.kpi-card::before {{
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 3px;
    border-radius: 18px 18px 0 0;
}}
.kpi-card.cyan::before {{ background: linear-gradient(90deg, #00d4ff, #0099cc); }}
.kpi-card.gold::before {{ background: linear-gradient(90deg, #d4af37, #f5d76e); }}
.kpi-card.rose::before {{ background: linear-gradient(90deg, #ff4757, #ff6b81); }}
.kpi-card.violet::before {{ background: linear-gradient(90deg, #a855f7, #7c3aed); }}

.kpi-icon {{
    width: 46px; height: 46px;
    border-radius: 14px;
    display: flex; align-items: center; justify-content: center;
    font-size: 1.3rem;
    margin-bottom: 14px;
}}
.kpi-icon.cyan {{ background: rgba(0, 212, 255, 0.12); }}
.kpi-icon.gold {{ background: rgba(212, 175, 55, 0.12); }}
.kpi-icon.rose {{ background: rgba(255, 71, 87, 0.12); }}
.kpi-icon.violet {{ background: rgba(168, 85, 247, 0.12); }}

.kpi-value {{
    font-family: 'Outfit', sans-serif;
    font-weight: 800;
    font-size: 2rem;
    color: {T['kpi_value']};
    margin: 0;
    line-height: 1.1;
}}
.kpi-label {{
    font-size: 0.82rem;
    color: {T['kpi_label']};
    text-transform: uppercase;
    letter-spacing: 1.5px;
    font-weight: 600;
    margin-top: 6px;
}}
.kpi-sub {{
    font-size: 0.75rem;
    color: {T['kpi_sub']};
    margin-top: 4px;
    font-family: 'JetBrains Mono', monospace;
}}

/* Section Title */
.section-title {{
    font-family: 'Outfit', sans-serif;
    font-weight: 700;
    font-size: 1.05rem;
    color: {T['text_primary']};
    margin: 0 0 4px 0;
    display: flex;
    align-items: center;
    gap: 8px;
}}
.section-title .dot {{
    width: 8px; height: 8px;
    border-radius: 50%;
    display: inline-block;
}}
.section-title .dot.live {{
    background: #ff4757;
    box-shadow: 0 0 8px rgba(255,71,87,0.6);
    animation: pulse-dot 1.5s infinite;
}}

/* Chart Panels */
.panel {{
    background: linear-gradient(145deg, {T['surface']} 0%, {T['surface2']} 100%);
    border: 1px solid {T['border']};
    border-radius: 16px;
    padding: 20px;
    margin-bottom: 16px;
}}
.panel:hover {{ border-color: {T['border_hover']}; }}
.panel-header {{
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 12px;
}}
.panel-tag {{
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.65rem;
    color: {T['gold']};
    background: {T['panel_tag_bg']};
    padding: 3px 10px;
    border-radius: 20px;
    border: 1px solid {T['panel_tag_border']};
}}

/* Animations */
@keyframes pulse-dot {{
    0%, 100% {{ opacity: 1; box-shadow: 0 0 6px rgba(255,71,87,0.6); }}
    50% {{ opacity: 0.4; box-shadow: 0 0 12px rgba(255,71,87,0.9); }}
}}
@keyframes pulse-map {{
    0%, 100% {{ opacity: 0.9; }}
    50% {{ opacity: 0.35; }}
}}

/* Plotly map dot pulse */
.js-plotly-plot .scattergeo .point {{
    animation: pulse-map 2s ease-in-out infinite;
}}

/* Scrollbar */
::-webkit-scrollbar {{ width: 6px; }}
::-webkit-scrollbar-track {{ background: {T['scrollbar_track']}; }}
::-webkit-scrollbar-thumb {{ background: {T['scrollbar_thumb']}; border-radius: 3px; }}

/* Expander */
.streamlit-expanderHeader {{
    font-family: 'Outfit', sans-serif !important;
    font-weight: 600 !important;
    color: {T['expander_color']} !important;
}}
</style>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────────
# DATABRICKS
# ─────────────────────────────────────────────
@st.cache_resource(show_spinner=False)
def get_databricks_connection():
    try:
        return sql.connect(
            server_hostname=st.secrets["databricks"]["server_hostname"],
            http_path=st.secrets["databricks"]["http_path"],
            access_token=st.secrets["databricks"]["access_token"],
            _tls_verify_hostname=False,
            _tls_trust_all=True
        )
    except Exception as e:
        st.error(f"Connection Error: {e}")
        return None

@st.cache_data(ttl=600, show_spinner=False)
def fetch_data(_connection, query):
    try:
        with _connection.cursor() as cursor:
            cursor.execute(query)
            result = cursor.fetchall()
            columns = [desc[0] for desc in cursor.description]
            return pd.DataFrame(result, columns=columns)
    except Exception as e:
        st.error(f"Query Error: {e}")
        return pd.DataFrame()


# ─────────────────────────────────────────────
# HELPERS
# ─────────────────────────────────────────────
def format_currency(val):
    if val >= 1e9:   return f"${val/1e9:.2f}B"
    if val >= 1e6:   return f"${val/1e6:.2f}M"
    if val >= 1e3:   return f"${val/1e3:.1f}K"
    return f"${val:.0f}"

def format_number(val):
    if val >= 1e6:   return f"{val/1e6:.2f}M"
    if val >= 1e3:   return f"{val/1e3:.1f}K"
    return f"{val:,.0f}"

COUNTRY_COORDS = {
    "United States": (39.8,-98.5), "United Kingdom": (54,-2),
    "Germany": (51.2,10.4), "France": (46.6,2.2),
    "China": (35.9,104.2), "Japan": (36.2,138.3),
    "India": (20.6,79), "Brazil": (-14.2,-51.9),
    "Australia": (-25.3,133.8), "Canada": (56.1,-106.3),
    "Russia": (61.5,105.3), "South Korea": (35.9,127.8),
    "Mexico": (23.6,-102.6), "Italy": (41.9,12.5),
    "Spain": (40.5,-3.7), "Netherlands": (52.1,5.3),
    "Sweden": (60.1,18.6), "Switzerland": (46.8,8.2),
    "Israel": (31,34.8), "Singapore": (1.4,103.8),
    "South Africa": (-30.6,22.9), "Nigeria": (9.1,8.7),
    "Argentina": (-38.4,-63.6), "Colombia": (4.6,-74.1),
    "Indonesia": (-0.8,113.9), "Turkey": (39,35.2),
    "Saudi Arabia": (23.9,45.1), "UAE": (23.4,53.8),
    "Poland": (51.9,19.1), "Norway": (60.5,8.5),
    "Egypt": (26.8,30.8), "Thailand": (15.9,100.9),
    "Vietnam": (14.1,108.3), "Philippines": (12.9,121.8),
    "Pakistan": (30.4,69.3), "Bangladesh": (23.7,90.4),
    "Malaysia": (4.2,101.9), "Chile": (-35.7,-71.5),
    "Peru": (-9.2,-75), "Ukraine": (48.4,31.2),
    "Romania": (45.9,25), "Czech Republic": (49.8,15.5),
    "Ireland": (53.1,-7.7), "New Zealand": (-40.9,174.9),
    "Denmark": (56.3,9.5), "Finland": (61.9,25.7),
    "Austria": (47.5,14.6), "Belgium": (50.5,4.5),
    "Portugal": (39.4,-8.2), "Greece": (39.1,21.8),
    "Hong Kong": (22.4,114.1), "Taiwan": (23.7,121),
    "Kenya": (-0.02,37.9), "Ghana": (7.9,-1),
    "Morocco": (31.8,-7.1), "Iran": (32.4,53.7),
}


# ─────────────────────────────────────────────
# PLOTLY BASE LAYOUT (no margin — set per chart)
# ─────────────────────────────────────────────
def get_plotly_base():
    return dict(
        template=T['plotly_tpl'],
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        font=dict(family="Outfit, sans-serif", color=T['plotly_font']),
    )


# ─────────────────────────────────────────────
# MAIN
# ─────────────────────────────────────────────
def main():
    # Top Bar
    st.markdown(f"""
    <div class="top-bar">
        <div class="top-bar-left">
            <h1>🛡️ Cyber Incidents</h1>
            <p>Control Panel — Gold Layer Analytics</p>
        </div>
        <div class="breadcrumb"><span>⌂</span> Home &gt; <span>Dashboard</span></div>
    </div>
    """, unsafe_allow_html=True)

    with st.spinner("Establishing secure connection..."):
        conn = get_databricks_connection()
    if not conn:
        st.stop()

    # Sidebar controls
    st.sidebar.markdown("---")
    st.sidebar.markdown("### ⚡ Controls")
    if st.sidebar.button("🔄 Refresh Data", use_container_width=True):
        st.cache_data.clear()
    st.sidebar.markdown("---")

    query = "SELECT * FROM workspace.gold.incidents_master_gold LIMIT 5000"
    with st.spinner("Loading analytics..."):
        df = fetch_data(conn, query)
    if df.empty:
        st.warning("No data in workspace.gold.incidents_master_gold")
        st.stop()

    # Type conversions
    for col in ['company_revenue_usd','employee_count','data_compromised_records','total_loss_usd','ransom_demanded_usd']:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)

    # Filters
    st.sidebar.markdown("### 🎯 Filters")
    if 'incident_date' in df.columns:
        df['year'] = pd.to_datetime(df['incident_date'], errors='coerce').dt.year
        years = ['All'] + sorted(df['year'].dropna().unique().tolist(), reverse=True)
        sel_year = st.sidebar.selectbox("Incident Year", years)
        if sel_year != 'All':
            df = df[df['year'] == sel_year]

    if 'attack_vector_primary' in df.columns:
        vectors = ['All'] + sorted(df['attack_vector_primary'].dropna().unique().tolist())
        sel_vec = st.sidebar.selectbox("Attack Vector", vectors)
        if sel_vec != 'All':
            df = df[df['attack_vector_primary'] == sel_vec]

    if 'country_name' in df.columns:
        countries = ['All'] + sorted(df['country_name'].dropna().unique().tolist())
        sel_country = st.sidebar.selectbox("Country", countries)
        if sel_country != 'All':
            df = df[df['country_name'] == sel_country]

    # KPIs
    total_incidents = len(df)
    total_loss = df['total_loss_usd'].sum() if 'total_loss_usd' in df.columns else 0
    total_records = df['data_compromised_records'].sum() if 'data_compromised_records' in df.columns else 0
    avg_days = 0
    if 'incident_date' in df.columns and 'disclosure_date' in df.columns:
        df['incident_date'] = pd.to_datetime(df['incident_date'], errors='coerce')
        df['disclosure_date'] = pd.to_datetime(df['disclosure_date'], errors='coerce')
        df['days_to_disclosure'] = (df['disclosure_date'] - df['incident_date']).dt.days
        avg_days = df['days_to_disclosure'].mean()
        if pd.isna(avg_days):
            avg_days = 0
    unique_countries = df['country_name'].nunique() if 'country_name' in df.columns else 0

    st.markdown(f"""
    <div class="kpi-row">
        <div class="kpi-card cyan">
            <div class="kpi-icon cyan">🔒</div>
            <div class="kpi-value">{format_number(total_incidents)}</div>
            <div class="kpi-label">Total Incidents</div>
            <div class="kpi-sub">Recorded breaches</div>
        </div>
        <div class="kpi-card gold">
            <div class="kpi-icon gold">💰</div>
            <div class="kpi-value">{format_currency(total_loss)}</div>
            <div class="kpi-label">Financial Loss</div>
            <div class="kpi-sub">Direct + Recovery + Fines</div>
        </div>
        <div class="kpi-card rose">
            <div class="kpi-icon rose">📊</div>
            <div class="kpi-value">{format_number(total_records)}</div>
            <div class="kpi-label">Records Leaked</div>
            <div class="kpi-sub">Compromised data points</div>
        </div>
        <div class="kpi-card violet">
            <div class="kpi-icon violet">⏱️</div>
            <div class="kpi-value">{avg_days:.0f} Days</div>
            <div class="kpi-label">Avg Disclosure</div>
            <div class="kpi-sub">Time to public report</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # ═══ ROW 1: MAP + SCATTER ═══
    col_map, col_scatter = st.columns([1.3, 1])

    with col_map:
        st.markdown("""
        <div class="panel"><div class="panel-header">
            <div class="section-title"><span class="dot live"></span> Live Threat Map</div>
            <div class="panel-tag">REAL-TIME</div>
        </div></div>""", unsafe_allow_html=True)

        if 'country_name' in df.columns:
            cc = df['country_name'].value_counts().reset_index()
            cc.columns = ['country_name', 'incident_count']

            if is_dark:
                map_colorscale = [[0,"#0a0e17"],[0.2,"#1a1a3e"],[0.5,"#6b2020"],[0.8,"#c0392b"],[1,"#ff4757"]]
            else:
                map_colorscale = [[0,"#fef2f2"],[0.2,"#fecaca"],[0.5,"#f87171"],[0.8,"#dc2626"],[1,"#991b1b"]]

            fig_map = px.choropleth(
                cc, locations="country_name", locationmode="country names",
                color="incident_count", hover_name="country_name",
                color_continuous_scale=map_colorscale,
            )
            fig_map.update_layout(
                **get_plotly_base(),
                geo=dict(
                    showframe=False, showcoastlines=True,
                    coastlinecolor=T['coast'],
                    projection_type='natural earth',
                    bgcolor='rgba(0,0,0,0)',
                    landcolor=T['land'],
                    oceancolor=T['ocean'],
                    showocean=True, showlakes=False,
                    countrycolor=T['coast'],
                ),
                margin=dict(l=0, r=0, t=0, b=0),
                coloraxis_colorbar=dict(title="Incidents", len=0.5, y=0.5),
                height=420,
            )

            # Pulsing red dots
            lats, lons, texts, sizes = [], [], [], []
            for _, row in cc.iterrows():
                name, count = row['country_name'], row['incident_count']
                if name in COUNTRY_COORDS:
                    lat, lon = COUNTRY_COORDS[name]
                    lats.append(lat)
                    lons.append(lon)
                    texts.append(f"{name}: {count}")
                    sizes.append(min(max(count * 1.5, 6), 35))

            # Outer glow
            fig_map.add_trace(go.Scattergeo(
                lat=lats, lon=lons, mode='markers',
                marker=dict(size=[s*2.2 for s in sizes], color='rgba(255,71,87,0.08)', line=dict(width=0)),
                hoverinfo='skip', showlegend=False,
            ))
            # Mid glow
            fig_map.add_trace(go.Scattergeo(
                lat=lats, lon=lons, mode='markers',
                marker=dict(size=[s*1.4 for s in sizes], color='rgba(255,71,87,0.18)', line=dict(width=0)),
                hoverinfo='skip', showlegend=False,
            ))
            # Core dot
            fig_map.add_trace(go.Scattergeo(
                lat=lats, lon=lons, mode='markers+text',
                marker=dict(size=sizes, color='#ff4757', opacity=0.9,
                            line=dict(width=1, color='rgba(255,71,87,0.5)')),
                text=texts, textposition="top center",
                textfont=dict(size=9, color="#ff6b81", family="JetBrains Mono"),
                hoverinfo='text', showlegend=False,
            ))

            st.plotly_chart(fig_map, use_container_width=True)

    with col_scatter:
        st.markdown("""
        <div class="panel"><div class="panel-header">
            <div class="section-title">💸 Revenue vs Loss</div>
            <div class="panel-tag">CORRELATION</div>
        </div></div>""", unsafe_allow_html=True)

        if 'company_revenue_usd' in df.columns and 'total_loss_usd' in df.columns:
            dfc = df[df['company_revenue_usd'] > 0].copy()
            fig_sc = px.scatter(
                dfc, x='company_revenue_usd', y='total_loss_usd',
                color='attack_vector_primary' if 'attack_vector_primary' in df.columns else None,
                hover_name='company_name' if 'company_name' in df.columns else None,
                size='data_compromised_records' if 'data_compromised_records' in df.columns else None,
                log_x=True, log_y=True,
                labels={'company_revenue_usd': 'Revenue (USD)', 'total_loss_usd': 'Loss (USD)'},
                color_discrete_sequence=["#00d4ff","#d4af37","#ff4757","#a855f7","#22d3ee","#f59e0b","#ec4899","#10b981"],
            )
            fig_sc.update_layout(
                **get_plotly_base(),
                margin=dict(l=20, r=20, t=10, b=20),
                height=420,
                legend=dict(
                    orientation="h", yanchor="bottom", y=-0.25,
                    xanchor="center", x=0.5,
                    font=dict(size=10, color=T['plotly_font']),
                    bgcolor="rgba(0,0,0,0)",
                ),
            )
            fig_sc.update_traces(marker=dict(line=dict(width=0.5, color='rgba(128,128,128,0.2)')))
            st.plotly_chart(fig_sc, use_container_width=True)

    # ═══ ROW 2: BAR + DONUT ═══
    col_bar, col_donut = st.columns(2)

    with col_bar:
        st.markdown("""
        <div class="panel"><div class="panel-header">
            <div class="section-title">🏢 Top Targets</div>
            <div class="panel-tag">BY INCIDENTS</div>
        </div></div>""", unsafe_allow_html=True)

        if 'company_name' in df.columns:
            top = df.groupby('company_name').agg(
                incidents=('company_name', 'count'),
                loss=('total_loss_usd', 'sum')
            ).reset_index().sort_values('incidents', ascending=False).head(10)

            fig_b = px.bar(
                top, x='incidents', y='company_name', orientation='h',
                color='loss',
                color_continuous_scale=["#1a1a2e","#d4af37","#f5d76e"] if is_dark else ["#fef9c3","#d4af37","#92400e"],
                labels={'incidents': 'Incidents', 'company_name': '', 'loss': 'Total Loss'},
            )
            fig_b.update_layout(
                **get_plotly_base(),
                margin=dict(l=10, r=10, t=10, b=10),
                yaxis=dict(categoryorder='total ascending'),
                height=380,
            )
            st.plotly_chart(fig_b, use_container_width=True)

    with col_donut:
        st.markdown("""
        <div class="panel"><div class="panel-header">
            <div class="section-title">🦠 Attack Vectors</div>
            <div class="panel-tag">DISTRIBUTION</div>
        </div></div>""", unsafe_allow_html=True)

        if 'attack_vector_primary' in df.columns:
            atk = df['attack_vector_primary'].value_counts().reset_index()
            atk.columns = ['vector', 'count']
            fig_d = px.pie(
                atk, names='vector', values='count', hole=0.6,
                color_discrete_sequence=["#00d4ff","#d4af37","#ff4757","#a855f7","#10b981","#f59e0b","#ec4899","#6366f1"],
            )
            fig_d.update_traces(
                textposition='inside', textinfo='percent',
                textfont=dict(size=11, family="Outfit"),
            )
            fig_d.update_layout(
                **get_plotly_base(),
                margin=dict(l=10, r=10, t=10, b=10),
                showlegend=True, height=380,
                legend=dict(
                    font=dict(size=9, color=T['plotly_font']),
                    bgcolor="rgba(0,0,0,0)",
                    orientation="h", yanchor="bottom", y=-0.3,
                    xanchor="center", x=0.5,
                ),
            )
            st.plotly_chart(fig_d, use_container_width=True)

    # Raw Data
    st.markdown("<br>", unsafe_allow_html=True)
    with st.expander("🔍 Filtered Data — Raw View"):
        st.dataframe(df, use_container_width=True, height=400)

    # Footer
    st.markdown(f"""
    <div style="text-align:center; padding:30px 0 10px; border-top:1px solid {T['border']}; margin-top:30px;">
        <span style="font-family:'JetBrains Mono',monospace; font-size:0.7rem; color:{T['footer_color']};">
            CYBER INCIDENTS CONTROL PANEL • GOLD LAYER • DATABRICKS
        </span>
    </div>""", unsafe_allow_html=True)


if __name__ == "__main__":
    main()
