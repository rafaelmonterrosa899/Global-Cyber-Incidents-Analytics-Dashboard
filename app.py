import streamlit as st
import pandas as pd
from databricks import sql
import plotly.express as px
import plotly.graph_objects as go
import time

# Configurations
st.set_page_config(page_title="Cyber Incidents Dashboard", page_icon="🛡️", layout="wide", initial_sidebar_state="expanded")

# --- Theme Toggle ---
if 'theme' not in st.session_state:
    st.session_state.theme = 'dark'

# Theme definitions
THEMES = {
    'dark': {
        'bg': '#0e1117',
        'card_bg': 'rgba(30, 35, 45, 0.7)',
        'card_border': 'rgba(255, 255, 255, 0.05)',
        'card_hover_border': 'rgba(79, 172, 254, 0.3)',
        'chart_bg': 'rgba(22, 27, 34, 0.5)',
        'chart_border': 'rgba(255, 255, 255, 0.05)',
        'header_color': '#ffffff',
        'sub_header': '#8b9bb4',
        'kpi_title': '#a0aec0',
        'kpi_value': '#ffffff',
        'kpi_value_gradient': 'linear-gradient(135deg, #ffffff 0%, #e2e8f0 100%)',
        'section_title': '#ffffff',
        'shadow': 'rgba(0, 0, 0, 0.2)',
        'shadow_hover': 'rgba(0, 0, 0, 0.3)',
        'plotly_template': 'plotly_dark',
        'plotly_bg': 'rgba(0,0,0,0)',
        'plotly_paper': 'rgba(0,0,0,0)',
        'geo_bg': 'rgba(0,0,0,0)',
    },
    'light': {
        'bg': '#f8f9fc',
        'card_bg': 'rgba(255, 255, 255, 0.95)',
        'card_border': 'rgba(0, 0, 0, 0.08)',
        'card_hover_border': 'rgba(37, 99, 235, 0.4)',
        'chart_bg': 'rgba(255, 255, 255, 0.9)',
        'chart_border': 'rgba(0, 0, 0, 0.06)',
        'header_color': '#1a202c',
        'sub_header': '#64748b',
        'kpi_title': '#64748b',
        'kpi_value': '#1e293b',
        'kpi_value_gradient': 'linear-gradient(135deg, #1e293b 0%, #334155 100%)',
        'section_title': '#1e293b',
        'shadow': 'rgba(0, 0, 0, 0.06)',
        'shadow_hover': 'rgba(0, 0, 0, 0.12)',
        'plotly_template': 'plotly_white',
        'plotly_bg': 'rgba(0,0,0,0)',
        'plotly_paper': 'rgba(0,0,0,0)',
        'geo_bg': 'rgba(0,0,0,0)',
    }
}

t = THEMES[st.session_state.theme]

# Custom CSS — dynamic based on theme
st.markdown(f"""
<style>
    /* Global Styles */
    .stApp {{
        background-color: {t['bg']};
    }}
    
    /* Headers */
    .dashboard-header {{
        color: {t['header_color']};
        font-weight: 900;
        font-size: 2.8rem;
        margin-bottom: 5px;
    }}
    .sub-header {{
        color: {t['sub_header']};
        font-size: 1.1rem;
        margin-bottom: 30px;
    }}

    /* Section Titles — white & bold */
    .stSubheader, h2, h3,
    [data-testid="stMarkdownContainer"] h2,
    [data-testid="stMarkdownContainer"] h3 {{
        color: {t['section_title']} !important;
        font-weight: 700 !important;
    }}

    /* KPI Cards */
    .kpi-container {{
        background: {t['card_bg']};
        border: 1px solid {t['card_border']};
        border-radius: 16px;
        padding: 24px;
        box-shadow: 0 10px 30px {t['shadow']};
        backdrop-filter: blur(10px);
        text-align: center;
        transition: all 0.3s ease;
        height: 140px;
        display: flex;
        flex-direction: column;
        justify-content: center;
        align-items: center;
    }}
    .kpi-container:hover {{
        transform: translateY(-5px);
        border-color: {t['card_hover_border']};
        box-shadow: 0 15px 35px {t['shadow_hover']};
    }}
    .kpi-title {{
        color: {t['kpi_title']};
        font-size: 1rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 1px;
        margin-bottom: 12px;
    }}
    .kpi-value {{
        font-size: 2.5rem;
        font-weight: 800;
        margin: 0;
        background: {t['kpi_value_gradient']};
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }}
    .kpi-subtitle {{
        color: #ef4444;
        font-size: 0.9rem;
        margin-top: 8px;
        font-weight: 500;
    }}
    
    /* Charts Container */
    .chart-box {{
        background: {t['chart_bg']};
        border: 1px solid {t['chart_border']};
        border-radius: 12px;
        padding: 15px;
        margin-top: 20px;
    }}
</style>
""", unsafe_allow_html=True)

# Databricks Connection Function
@st.cache_resource(show_spinner=False)
def get_databricks_connection():
    try:
        connection = sql.connect(
            server_hostname=st.secrets["databricks"]["server_hostname"],
            http_path=st.secrets["databricks"]["http_path"],
            access_token=st.secrets["databricks"]["access_token"],
            _tls_verify_hostname=False,
            _tls_trust_all=True
        )
        return connection
    except Exception as e:
        st.error(f"Error connecting to Databricks: {e}")
        return None

# Fetch Data Function
@st.cache_data(ttl=600, show_spinner=False)
def fetch_data(_connection, query):
    try:
        with _connection.cursor() as cursor:
            cursor.execute(query)
            result = cursor.fetchall()
            columns = [desc[0] for desc in cursor.description]
            return pd.DataFrame(result, columns=columns)
    except Exception as e:
        st.error(f"Error fetching data: {e}")
        return pd.DataFrame()

# Formatting Helper
def format_currency(val):
    if val >= 1_000_000_000:
        return f"${val/1_000_000_000:.2f}B"
    elif val >= 1_000_000:
        return f"${val/1_000_000:.2f}M"
    elif val >= 1_000:
        return f"${val/1_000:.2f}K"
    return f"${val:.2f}"

def format_number(val):
    if val >= 1_000_000:
        return f"{val/1_000_000:.2f}M"
    elif val >= 1_000:
        return f"{val/1_000:.2f}K"
    return f"{val:,.0f}"

# Main Application
def main():
    st.markdown('<h1 class="dashboard-header">Global Cyber Incidents Analytics</h1>', unsafe_allow_html=True)
    st.markdown('<p class="sub-header">Interactive Gold Layer Insights on Corporate Cybersecurity Breaches</p>', unsafe_allow_html=True)

    with st.spinner("Connecting securely to Databricks..."):
        conn = get_databricks_connection()
        
    if not conn:
        st.stop()
        
    # --- Sidebar Filters ---
    st.sidebar.markdown("### ⚙️ Dashboard Controls")
    
    # Theme Toggle
    theme_label = "🌙 Dark Mode" if st.session_state.theme == 'light' else "☀️ Light Mode"
    if st.sidebar.button(theme_label, use_container_width=True):
        st.session_state.theme = 'light' if st.session_state.theme == 'dark' else 'dark'
        st.rerun()
    
    if st.sidebar.button("🔄 Refresh Dataset", use_container_width=True):
        st.cache_data.clear()
        
    st.sidebar.markdown("---")
    
    # Base query
    query = "SELECT * FROM workspace.gold.incidents_master_gold LIMIT 5000"
    
    with st.spinner("Fetching Analytics Data..."):
        df = fetch_data(conn, query)
        
    if df.empty:
        st.warning("No data retrieved. Please ensure the workspace.gold.incidents_master_gold table exists and has data.")
        st.stop()
        
    # Convert types if necessary
    numeric_columns = ['company_revenue_usd', 'employee_count', 'data_compromised_records', 'total_loss_usd', 'ransom_demanded_usd']
    for col in numeric_columns:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce')
            df[col] = df[col].fillna(0)
            
    # Interactive Sidebar Filters
    st.sidebar.subheader("🎯 Filters")
    
    # Year filter
    if 'incident_date' in df.columns:
        df['year'] = pd.to_datetime(df['incident_date']).dt.year
        years = ['All'] + sorted(df['year'].dropna().unique().tolist(), reverse=True)
        selected_year = st.sidebar.selectbox("Incident Year", years)
        if selected_year != 'All':
            df = df[df['year'] == selected_year]
            
    # Attack Vector Filter
    if 'attack_vector_primary' in df.columns:
        vectors = ['All'] + sorted(df['attack_vector_primary'].dropna().unique().tolist())
        selected_vector = st.sidebar.selectbox("Primary Attack Vector", vectors)
        if selected_vector != 'All':
            df = df[df['attack_vector_primary'] == selected_vector]

    # --- Dashboard Layout ---
    
    # 1. KPI Row
    kpi_col1, kpi_col2, kpi_col3, kpi_col4 = st.columns(4)
    
    total_incidents = len(df)
    total_loss = df['total_loss_usd'].sum() if 'total_loss_usd' in df.columns else 0
    total_records = df['data_compromised_records'].sum() if 'data_compromised_records' in df.columns else 0
    
    avg_days_to_disclosure = 0
    if 'incident_date' in df.columns and 'disclosure_date' in df.columns:
        df['incident_date'] = pd.to_datetime(df['incident_date'], errors='coerce')
        df['disclosure_date'] = pd.to_datetime(df['disclosure_date'], errors='coerce')
        df['days_to_disclosure'] = (df['disclosure_date'] - df['incident_date']).dt.days
        avg_days_to_disclosure = df['days_to_disclosure'].mean()
    
    with kpi_col1:
        st.markdown(f"""
        <div class="kpi-container">
            <div class="kpi-title">Recorded Incidents</div>
            <div class="kpi-value">{format_number(total_incidents)}</div>
        </div>
        """, unsafe_allow_html=True)
        
    with kpi_col2:
        st.markdown(f"""
        <div class="kpi-container">
            <div class="kpi-title">Total Financial Loss</div>
            <div class="kpi-value">{format_currency(total_loss)}</div>
            <div class="kpi-subtitle">Direct + Recovery + Fines</div>
        </div>
        """, unsafe_allow_html=True)
        
    with kpi_col3:
        st.markdown(f"""
        <div class="kpi-container">
            <div class="kpi-title">Records Compromised</div>
            <div class="kpi-value">{format_number(total_records)}</div>
        </div>
        """, unsafe_allow_html=True)
        
    with kpi_col4:
        st.markdown(f"""
        <div class="kpi-container">
            <div class="kpi-title">Avg Time to Disclosure</div>
            <div class="kpi-value">{avg_days_to_disclosure:.1f} Days</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # 2. Map and Main Relation Chart
    col_map, col_scatter = st.columns([1.2, 1])
    
    with col_map:
        st.markdown('<div class="chart-box">', unsafe_allow_html=True)
        st.subheader("🌍 Global Incident Distribution")
        if 'country_name' in df.columns:
            country_counts = df['country_name'].value_counts().reset_index()
            country_counts.columns = ['country_name', 'incident_count']
            
            fig_map = px.choropleth(
                country_counts,
                locations="country_name",
                locationmode="country names",
                color="incident_count",
                hover_name="country_name",
                color_continuous_scale=px.colors.sequential.Plasma,
                title="Total Attacks per Region",
                template=t['plotly_template']
            )
            fig_map.update_layout(
                geo=dict(showframe=False, showcoastlines=True, projection_type='equirectangular', bgcolor=t['geo_bg']),
                margin=dict(l=0, r=0, t=40, b=0),
                plot_bgcolor=t['plotly_bg'],
                paper_bgcolor=t['plotly_paper'],
                coloraxis_colorbar=dict(title="Incidents")
            )
            st.plotly_chart(fig_map, use_container_width=True)
        else:
            st.info("Country data not available in the dataset.")
        st.markdown('</div>', unsafe_allow_html=True)
            
    with col_scatter:
        st.markdown('<div class="chart-box">', unsafe_allow_html=True)
        st.subheader("💸 Revenue vs Financial Loss")
        if 'company_revenue_usd' in df.columns and 'total_loss_usd' in df.columns:
            df_chart = df[df['company_revenue_usd'] > 0]
            
            fig_scatter = px.scatter(
                df_chart,
                x='company_revenue_usd',
                y='total_loss_usd',
                color='attack_vector_primary' if 'attack_vector_primary' in df.columns else None,
                hover_name='company_name' if 'company_name' in df.columns else None,
                size='data_compromised_records' if 'data_compromised_records' in df.columns else None,
                log_x=True, log_y=True,
                title="Impact Relation (Log Scale)",
                template=t['plotly_template'],
                labels={'company_revenue_usd': 'Company Revenue (USD)', 'total_loss_usd': 'Total Loss (USD)'},
                color_discrete_sequence=px.colors.qualitative.Set3
            )
            fig_scatter.update_layout(
                plot_bgcolor=t['plotly_bg'],
                paper_bgcolor=t['plotly_paper'],
                margin=dict(l=20, r=20, t=40, b=20),
                legend=dict(orientation="h", yanchor="bottom", y=-0.3, xanchor="center", x=0.5)
            )
            st.plotly_chart(fig_scatter, use_container_width=True)
        else:
            st.info("Revenue or Loss data not available.")
        st.markdown('</div>', unsafe_allow_html=True)

    # 3. Bar Charts Row
    st.markdown("<br>", unsafe_allow_html=True)
    col_bar1, col_bar2 = st.columns(2)
    
    with col_bar1:
        st.markdown('<div class="chart-box">', unsafe_allow_html=True)
        st.subheader("🏢 Top Target Companies")
        if 'company_name' in df.columns:
            top_companies = df.groupby('company_name').agg({'total_loss_usd': 'sum', 'incident_id': 'count'}).reset_index()
            top_companies = top_companies.sort_values('incident_id', ascending=False).head(10)
            
            fig_bar1 = px.bar(
                top_companies,
                x='incident_id',
                y='company_name',
                orientation='h',
                color='total_loss_usd',
                color_continuous_scale=px.colors.sequential.Sunsetdark,
                title="Companies by Number of Incidents",
                template=t['plotly_template'],
                labels={'incident_id': 'Incident Count', 'company_name': '', 'total_loss_usd': 'Total Loss'}
            )
            fig_bar1.update_layout(
                yaxis={'categoryorder':'total ascending'},
                plot_bgcolor=t['plotly_bg'],
                paper_bgcolor=t['plotly_paper'],
                margin=dict(l=10, r=10, t=40, b=10)
            )
            st.plotly_chart(fig_bar1, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)
        
    with col_bar2:
        st.markdown('<div class="chart-box">', unsafe_allow_html=True)
        st.subheader("🦠 Primary Attack Vectors")
        if 'attack_vector_primary' in df.columns:
            attack_counts = df['attack_vector_primary'].value_counts().reset_index()
            attack_counts.columns = ['attack_vector_primary', 'count']
            
            fig_pie = px.pie(
                attack_counts,
                names='attack_vector_primary',
                values='count',
                hole=0.5,
                title="Incidents by Entry Method",
                template=t['plotly_template'],
                color_discrete_sequence=px.colors.qualitative.Pastel
            )
            fig_pie.update_traces(textposition='inside', textinfo='percent+label')
            fig_pie.update_layout(
                plot_bgcolor=t['plotly_bg'],
                paper_bgcolor=t['plotly_paper'],
                showlegend=False,
                margin=dict(l=10, r=10, t=40, b=10)
            )
            st.plotly_chart(fig_pie, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

    st.markdown("---")
    
    # Raw Data Expander
    with st.expander("🔍 Filtered Data Details"):
        st.dataframe(df, use_container_width=True)

if __name__ == "__main__":
    main()
