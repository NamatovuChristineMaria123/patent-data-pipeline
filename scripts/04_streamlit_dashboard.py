"""
Streamlit Dashboard for Patent Data Analysis
Run with: streamlit run scripts/04_streamlit_dashboard.py
"""

import streamlit as st
import duckdb
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import os

# Page configuration
st.set_page_config(
    page_title="Patent Intelligence Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS with white background and sky blue theme
st.markdown("""
<style>
    /* Import Font Awesome */
    @import url('https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css');
    
    /* Main background */
    .stApp {
        background: linear-gradient(135deg, #ffffff 0%, #f0f9ff 100%);
    }
    
    /* Header styling */
    .main-header {
        text-align: center;
        padding: 30px;
        background: linear-gradient(135deg, #38bdf8 0%, #0284c7 100%);
        border-radius: 20px;
        margin-bottom: 25px;
        box-shadow: 0 10px 25px -5px rgba(0,0,0,0.1);
    }
    
    .main-header h1 {
        color: white;
        font-size: 2.5em;
        margin: 0;
        font-weight: 600;
    }
    
    .main-header p {
        color: rgba(255,255,255,0.95);
        margin: 10px 0 0 0;
        font-size: 1.1em;
    }
    
    /* KPI Cards */
    .kpi-card {
        padding: 20px;
        border-radius: 15px;
        text-align: center;
        box-shadow: 0 4px 6px -1px rgba(0,0,0,0.1);
        transition: transform 0.3s, box-shadow 0.3s;
        background: white;
        border: 1px solid #e2e8f0;
    }
    
    .kpi-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 20px 25px -5px rgba(0,0,0,0.1);
    }
    
    .kpi-icon {
        font-size: 2.5em;
        margin-bottom: 10px;
    }
    
    .kpi-value {
        font-size: 2em;
        font-weight: bold;
        margin: 10px 0;
        color: #0f172a;
    }
    
    .kpi-label {
        color: #64748b;
        font-size: 0.9em;
        font-weight: 500;
    }
    
    /* Sidebar styling */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #f8fafc 0%, #e0f2fe 100%);
        border-right: 1px solid #cbd5e1;
    }
    
    .sidebar-header {
        background: linear-gradient(135deg, #38bdf8 0%, #0284c7 100%);
        padding: 20px;
        border-radius: 12px;
        text-align: center;
        margin-bottom: 20px;
    }
    
    .sidebar-header h2 {
        color: white;
        margin: 0;
        font-size: 1.3em;
    }
    
    .sidebar-header i {
        font-size: 2em;
        color: white;
        margin-bottom: 10px;
    }
    
    .info-box {
        background: linear-gradient(135deg, #e0f2fe 0%, #bae6fd 100%);
        padding: 15px;
        border-radius: 12px;
        color: #0369a1;
        text-align: center;
        border: 1px solid #7dd3fc;
    }
    
    /* Section titles */
    .section-title {
        font-size: 1.5em;
        font-weight: 600;
        margin: 25px 0 15px 0;
        color: #0f172a;
        border-left: 5px solid #38bdf8;
        padding-left: 15px;
    }
    
    .section-title i {
        margin-right: 10px;
        color: #38bdf8;
    }
    
    /* Footer */
    .footer {
        text-align: center;
        padding: 25px;
        background: linear-gradient(135deg, #f8fafc 0%, #e0f2fe 100%);
        border-radius: 15px;
        color: #0f172a;
        margin-top: 30px;
        border: 1px solid #cbd5e1;
    }
    
    .footer a {
        color: #0284c7;
        text-decoration: none;
        font-weight: 500;
    }
    
    .footer a:hover {
        text-decoration: underline;
    }
    
    /* Metric styling */
    [data-testid="stMetricValue"] {
        font-size: 1.5em;
        font-weight: bold;
        color: #0284c7;
    }
    
    /* Button styling */
    .stButton > button {
        background: linear-gradient(135deg, #38bdf8 0%, #0284c7 100%);
        color: white;
        border: none;
        border-radius: 8px;
        padding: 8px 16px;
        font-weight: 500;
    }
    
    .stButton > button:hover {
        background: linear-gradient(135deg, #0284c7 0%, #0369a1 100%);
        color: white;
    }
    
    /* Slider styling */
    .stSlider [data-baseweb="slider"] {
        accent-color: #38bdf8;
    }
    
    /* Selectbox styling */
    .stSelectbox [data-baseweb="select"] {
        border-color: #cbd5e1;
    }
    
    /* Dataframe styling */
    .stDataFrame {
        border: 1px solid #e2e8f0;
        border-radius: 10px;
    }
</style>
""", unsafe_allow_html=True)

# Header with gradient
st.markdown("""
<div class="main-header">
    <i class="fas fa-chart-line" style="font-size: 3em; color: white; margin-bottom: 10px;"></i>
    <h1>Global Patent Intelligence Dashboard</h1>
    <p><i class="fas fa-database"></i> Real-time patent analytics from USPTO PatentsView data (1976-2025)</p>
</div>
""", unsafe_allow_html=True)

# Database connection - FIXED: Create connection once and keep it open
BASE_DIR = r"D:\patent_data_pipeline"
DB_PATH = os.path.join(BASE_DIR, "database", "patent_data.duckdb")

@st.cache_resource
def get_connection():
    """Get database connection - cached to avoid closing"""
    return duckdb.connect(DB_PATH)

# Create connection (this stays open)
conn = get_connection()

# Sidebar
st.sidebar.markdown("""
<div class="sidebar-header">
    <i class="fas fa-sliders-h"></i>
    <h2>Dashboard Filters</h2>
</div>
""", unsafe_allow_html=True)

# Get year range - FIXED: Use the connection directly
try:
    years_df = conn.execute("SELECT MIN(year) as min_year, MAX(year) as max_year FROM patents WHERE year > 0 AND year IS NOT NULL").fetchdf()
    min_year = int(years_df['min_year'].iloc[0]) if not years_df['min_year'].isna().iloc[0] else 1976
    max_year = int(years_df['max_year'].iloc[0]) if not years_df['max_year'].isna().iloc[0] else 2025
except Exception as e:
    st.error(f"Error loading year range: {e}")
    min_year, max_year = 1976, 2025

year_range = st.sidebar.slider(
    "Select Year Range",
    min_value=min_year,
    max_value=max_year,
    value=(2015, max_year),
    help="Filter patents by grant year"
)

# Country filter
countries_df = conn.execute("""
    SELECT DISTINCT country FROM inventors 
    WHERE country != 'Unknown' AND country IS NOT NULL AND country != ''
    ORDER BY country
""").fetchdf()
country_options = ["All Countries"] + countries_df['country'].tolist()
selected_country = st.sidebar.selectbox("Select Country", country_options)

st.sidebar.markdown("---")

st.sidebar.markdown("""
<div class="info-box">
    <i class="fas fa-lightbulb" style="font-size: 1.5em;"></i>
    <p style="margin: 10px 0 0 0; font-weight: 500;">💡 Hover over charts for interactive details!</p>
</div>
""", unsafe_allow_html=True)

# Main content - KPI Cards
st.markdown('<div class="section-title"><i class="fas fa-chart-simple"></i> Key Performance Indicators</div>', unsafe_allow_html=True)

# Get KPIs
if selected_country == "All Countries":
    total_patents_df = conn.execute(f"SELECT COUNT(*) as total FROM patents WHERE year BETWEEN {year_range[0]} AND {year_range[1]}").fetchdf()
    total_patents = total_patents_df['total'].iloc[0] if not total_patents_df.empty else 0
    
    total_inventors_df = conn.execute("SELECT COUNT(DISTINCT inventor_id) as total FROM inventors").fetchdf()
    total_inventors = total_inventors_df['total'].iloc[0] if not total_inventors_df.empty else 0
    
    total_companies_df = conn.execute("SELECT COUNT(DISTINCT company_id) as total FROM companies").fetchdf()
    total_companies = total_companies_df['total'].iloc[0] if not total_companies_df.empty else 0
    
    total_countries_df = conn.execute("SELECT COUNT(DISTINCT country) as total FROM inventors WHERE country != 'Unknown' AND country IS NOT NULL").fetchdf()
    total_countries = total_countries_df['total'].iloc[0] if not total_countries_df.empty else 0
else:
    total_patents_df = conn.execute(f"""
        SELECT COUNT(DISTINCT r.patent_id) as total
        FROM relationships r
        JOIN inventors i ON r.inventor_id = i.inventor_id
        WHERE i.country = '{selected_country}'
        AND r.patent_id IN (SELECT patent_id FROM patents WHERE year BETWEEN {year_range[0]} AND {year_range[1]})
    """).fetchdf()
    total_patents = total_patents_df['total'].iloc[0] if not total_patents_df.empty else 0
    
    total_inventors_df = conn.execute(f"SELECT COUNT(DISTINCT inventor_id) as total FROM inventors WHERE country = '{selected_country}'").fetchdf()
    total_inventors = total_inventors_df['total'].iloc[0] if not total_inventors_df.empty else 0
    
    total_companies_df = conn.execute("SELECT COUNT(DISTINCT company_id) as total FROM companies").fetchdf()
    total_companies = total_companies_df['total'].iloc[0] if not total_companies_df.empty else 0
    
    total_countries = 1

# Display KPI cards with sky blue theme
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.markdown(f"""
    <div class="kpi-card">
        <div class="kpi-icon"><i class="fas fa-file-alt" style="color: #38bdf8;"></i></div>
        <div class="kpi-value">{total_patents:,}</div>
        <div class="kpi-label">Total Patents</div>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown(f"""
    <div class="kpi-card">
        <div class="kpi-icon"><i class="fas fa-users" style="color: #38bdf8;"></i></div>
        <div class="kpi-value">{total_inventors:,}</div>
        <div class="kpi-label">Unique Inventors</div>
    </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown(f"""
    <div class="kpi-card">
        <div class="kpi-icon"><i class="fas fa-building" style="color: #38bdf8;"></i></div>
        <div class="kpi-value">{total_companies:,}</div>
        <div class="kpi-label">Companies</div>
    </div>
    """, unsafe_allow_html=True)

with col4:
    st.markdown(f"""
    <div class="kpi-card">
        <div class="kpi-icon"><i class="fas fa-globe-americas" style="color: #38bdf8;"></i></div>
        <div class="kpi-value">{total_countries}</div>
        <div class="kpi-label">Countries</div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("---")

# Row 1: Two charts side by side
col1, col2 = st.columns(2)

with col1:
    st.markdown('<div class="section-title"><i class="fas fa-trophy"></i> Top 10 Inventors</div>', unsafe_allow_html=True)
    if selected_country == "All Countries":
        top_inventors = conn.execute(f"""
            SELECT i.name, COUNT(DISTINCT r.patent_id) as patent_count
            FROM inventors i
            JOIN relationships r ON i.inventor_id = r.inventor_id
            WHERE r.patent_id IN (SELECT patent_id FROM patents WHERE year BETWEEN {year_range[0]} AND {year_range[1]})
            GROUP BY i.inventor_id, i.name
            ORDER BY patent_count DESC
            LIMIT 10
        """).fetchdf()
    else:
        top_inventors = conn.execute(f"""
            SELECT i.name, COUNT(DISTINCT r.patent_id) as patent_count
            FROM inventors i
            JOIN relationships r ON i.inventor_id = r.inventor_id
            WHERE i.country = '{selected_country}'
            AND r.patent_id IN (SELECT patent_id FROM patents WHERE year BETWEEN {year_range[0]} AND {year_range[1]})
            GROUP BY i.inventor_id, i.name
            ORDER BY patent_count DESC
            LIMIT 10
        """).fetchdf()
    
    if not top_inventors.empty:
        fig = px.bar(top_inventors, x='patent_count', y='name', orientation='h',
                     title='Top Inventors by Patent Count', 
                     color='patent_count',
                     color_continuous_scale='Blues',
                     text='patent_count')
        # IMPROVED: Better text visibility
        fig.update_traces(texttemplate='%{text:,}', textposition='outside',
                          textfont=dict(size=14, color='#1e3a8a', family='Arial Black'))
        fig.update_layout(height=500, title_x=0.5, 
                          font=dict(size=13, color='#0f172a'),
                          xaxis_title="Patent Count", 
                          yaxis_title="Inventor Name",
                          xaxis=dict(title_font=dict(size=13, color='#1e3a8a'), 
                                    tickfont=dict(size=11, color='#334155')),
                          yaxis=dict(title_font=dict(size=13, color='#1e3a8a'), 
                                    tickfont=dict(size=11, color='#334155')),
                          plot_bgcolor='white', paper_bgcolor='white')
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No data for selected filters")

with col2:
    st.markdown('<div class="section-title"><i class="fas fa-building"></i> Top 10 Companies</div>', unsafe_allow_html=True)
    if selected_country == "All Countries":
        top_companies = conn.execute(f"""
            SELECT c.name, COUNT(DISTINCT r.patent_id) as patent_count
            FROM companies c
            JOIN relationships r ON c.company_id = r.company_id
            WHERE r.patent_id IN (SELECT patent_id FROM patents WHERE year BETWEEN {year_range[0]} AND {year_range[1]})
            GROUP BY c.company_id, c.name
            ORDER BY patent_count DESC
            LIMIT 10
        """).fetchdf()
    else:
        top_companies = conn.execute(f"""
            SELECT c.name, COUNT(DISTINCT r.patent_id) as patent_count
            FROM companies c
            JOIN relationships r ON c.company_id = r.company_id
            WHERE c.country = '{selected_country}'
            AND r.patent_id IN (SELECT patent_id FROM patents WHERE year BETWEEN {year_range[0]} AND {year_range[1]})
            GROUP BY c.company_id, c.name
            ORDER BY patent_count DESC
            LIMIT 10
        """).fetchdf()
    
    if not top_companies.empty:
        fig = px.bar(top_companies, x='patent_count', y='name', orientation='h',
                     title='Top Companies by Patent Count',
                     color='patent_count',
                     color_continuous_scale='Blues',
                     text='patent_count')
        # IMPROVED: Better text visibility
        fig.update_traces(texttemplate='%{text:,}', textposition='outside',
                          textfont=dict(size=14, color='#1e3a8a', family='Arial Black'))
        fig.update_layout(height=500, title_x=0.5,
                          font=dict(size=13, color='#0f172a'),
                          xaxis_title="Patent Count", 
                          yaxis_title="Company Name",
                          xaxis=dict(title_font=dict(size=13, color='#1e3a8a'), 
                                    tickfont=dict(size=11, color='#334155')),
                          yaxis=dict(title_font=dict(size=13, color='#1e3a8a'), 
                                    tickfont=dict(size=11, color='#334155')),
                          plot_bgcolor='white', paper_bgcolor='white')
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No data for selected filters")

st.markdown("---")

# Row 2: Patent Trends
st.markdown('<div class="section-title"><i class="fas fa-chart-line"></i> Patent Trends Over Time</div>', unsafe_allow_html=True)

if selected_country == "All Countries":
    trends = conn.execute(f"""
        SELECT year, COUNT(*) as patent_count
        FROM patents
        WHERE year BETWEEN {year_range[0]} AND {year_range[1]} AND year IS NOT NULL
        GROUP BY year
        ORDER BY year
    """).fetchdf()
else:
    trends = conn.execute(f"""
        SELECT p.year, COUNT(DISTINCT r.patent_id) as patent_count
        FROM patents p
        JOIN relationships r ON p.patent_id = r.patent_id
        JOIN inventors i ON r.inventor_id = i.inventor_id
        WHERE i.country = '{selected_country}'
        AND p.year BETWEEN {year_range[0]} AND {year_range[1]}
        GROUP BY p.year
        ORDER BY p.year
    """).fetchdf()

if not trends.empty:
    fig = px.area(trends, x='year', y='patent_count', 
                  title='Patent Grants Over Time',
                  color_discrete_sequence=['#38bdf8'],
                  markers=True)
    # IMPROVED: Better line and marker visibility
    fig.update_traces(line=dict(width=3, color='#0284c7'), 
                      marker=dict(size=8, color='#0369a1', symbol='circle'),
                      fillcolor='rgba(56, 189, 248, 0.3)')
    fig.update_layout(height=450, title_x=0.5, 
                      xaxis_title="Year", 
                      yaxis_title="Number of Patents",
                      plot_bgcolor='white', paper_bgcolor='white',
                      font=dict(size=13, color='#0f172a'),
                      xaxis=dict(tickangle=-45, tickfont=dict(size=10, color='#334155'), 
                                title_font=dict(size=13, color='#1e3a8a')),
                      yaxis=dict(tickfont=dict(size=11, color='#334155'),
                                title_font=dict(size=13, color='#1e3a8a')))
    st.plotly_chart(fig, use_container_width=True)
else:
    st.info("No data for selected filters")

st.markdown("---")

# Row 3: Country Distribution
col1, col2 = st.columns(2)

with col1:
    st.markdown('<div class="section-title"><i class="fas fa-globe"></i> Patent Distribution by Country</div>', unsafe_allow_html=True)
    country_dist = conn.execute(f"""
        SELECT 
            i.country,
            COUNT(DISTINCT r.patent_id) as patent_count
        FROM inventors i
        JOIN relationships r ON i.inventor_id = r.inventor_id
        WHERE i.country != 'Unknown' AND i.country IS NOT NULL AND i.country != ''
        AND r.patent_id IN (SELECT patent_id FROM patents WHERE year BETWEEN {year_range[0]} AND {year_range[1]})
        GROUP BY i.country
        ORDER BY patent_count DESC
        LIMIT 12
    """).fetchdf()
    
    if not country_dist.empty:
        fig = px.bar(country_dist, x='country', y='patent_count', 
                     title='Top 12 Countries by Patents',
                     color='patent_count',
                     color_continuous_scale='Blues',
                     text='patent_count')
        # IMPROVED: Better text visibility on bars
        fig.update_traces(texttemplate='%{text:,}', textposition='outside',
                          textfont=dict(size=12, color='#1e3a8a', family='Arial Black'))
        fig.update_layout(height=500, title_x=0.5,
                          xaxis_title="Country", 
                          yaxis_title="Patent Count",
                          xaxis=dict(tickangle=-45, tickfont=dict(size=10, color='#334155'),
                                    title_font=dict(size=13, color='#1e3a8a')),
                          yaxis=dict(tickfont=dict(size=11, color='#334155'),
                                    title_font=dict(size=13, color='#1e3a8a')),
                          plot_bgcolor='white', paper_bgcolor='white')
        st.plotly_chart(fig, use_container_width=True)

with col2:
    st.markdown('<div class="section-title"><i class="fas fa-chart-pie"></i> Patent Share by Country</div>', unsafe_allow_html=True)
    if not country_dist.empty:
        # IMPROVED: Better pie chart colors (vibrant)
        vibrant_colors = ['#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4', '#FFEAA7', '#DDA0DD', '#98D8C8', '#F7DC6F']
        fig = px.pie(country_dist.head(8), values='patent_count', names='country',
                     title='Top 8 Countries Patent Share',
                     color_discrete_sequence=vibrant_colors,
                     hole=0.3)
        fig.update_traces(textposition='inside', textinfo='percent+label',
                          textfont=dict(size=13, color='white', family='Arial Black'),
                          insidetextfont=dict(size=13, color='white'),
                          marker=dict(line=dict(color='white', width=2)))
        fig.update_layout(height=500, title_x=0.5,
                          plot_bgcolor='white', paper_bgcolor='white',
                          font=dict(size=13, color='#0f172a'))
        st.plotly_chart(fig, use_container_width=True)

st.markdown("---")

# Row 4: Innovation Heatmap
st.markdown('<div class="section-title"><i class="fas fa-fire"></i> Innovation Heatmap: Patents by Year and Country</div>', unsafe_allow_html=True)

top10_countries = country_dist.head(10)['country'].tolist() if not country_dist.empty else []
if top10_countries:
    country_list = "', '".join(top10_countries)
    heatmap_data = conn.execute(f"""
        SELECT 
            p.year,
            i.country,
            COUNT(DISTINCT r.patent_id) as patent_count
        FROM patents p
        JOIN relationships r ON p.patent_id = r.patent_id
        JOIN inventors i ON r.inventor_id = i.inventor_id
        WHERE i.country IN ('{country_list}')
        AND p.year BETWEEN {year_range[0]} AND {year_range[1]}
        GROUP BY p.year, i.country
        ORDER BY p.year, i.country
    """).fetchdf()
    
    if not heatmap_data.empty:
        # IMPROVED: Transposed heatmap (countries on Y, years on X) for better readability
        pivot_data = heatmap_data.pivot(index='country', columns='year', values='patent_count').fillna(0)
        fig = px.imshow(pivot_data,
                        title='Patent Activity Heatmap',
                        color_continuous_scale='Blues',
                        aspect='auto',
                        text_auto='.0f',
                        labels=dict(x='Year', y='Country', color='Patents'))
        # IMPROVED: Better text visibility in heatmap cells
        fig.update_traces(textfont=dict(size=11, color='black', family='Arial Black'))
        fig.update_layout(height=550, title_x=0.5,
                          xaxis=dict(tickangle=-45, tickfont=dict(size=10, color='#334155'),
                                    title_font=dict(size=13, color='#1e3a8a')),
                          yaxis=dict(tickfont=dict(size=11, color='#334155'),
                                    title_font=dict(size=13, color='#1e3a8a')),
                          plot_bgcolor='white', paper_bgcolor='white')
        st.plotly_chart(fig, use_container_width=True)

st.markdown("---")

# Row 5: Sample Data
st.markdown('<div class="section-title"><i class="fas fa-table"></i> Recent Patent Sample</div>', unsafe_allow_html=True)
st.info("📋 Showing a sample of recent patents (limited to 100 rows for performance)")

sample_data = conn.execute("""
    SELECT 
        p.patent_id,
        SUBSTRING(p.title, 1, 60) as title_preview,
        i.name as inventor_name,
        c.name as company_name,
        p.year
    FROM patents p
    JOIN relationships r ON p.patent_id = r.patent_id
    JOIN inventors i ON r.inventor_id = i.inventor_id
    JOIN companies c ON r.company_id = c.company_id
    WHERE p.year IS NOT NULL
    ORDER BY p.year DESC
    LIMIT 100
""").fetchdf()

if not sample_data.empty:
    st.dataframe(sample_data, use_container_width=True, height=400)

# Footer
st.markdown("""
<div class="footer">
    <i class="fas fa-chart-line"></i> <strong>Patent Intelligence Dashboard</strong> | 
    <i class="fas fa-database"></i> Data Source: <a href="https://patentsview.org/">USPTO PatentsView</a> | 
    <i class="fas fa-cube"></i> Powered by <strong>DuckDB</strong> & <strong>Streamlit</strong> | 
    <i class="fas fa-chart-simple"></i> Built for Patent Data Analysis
</div>
""", unsafe_allow_html=True)