"""
Streamlit Dashboard for Clinical Trial Site Evaluation
"""
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from typing import List
import sys
from pathlib import Path

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent.parent))

from src.database.models import SiteMaster, ClinicalTrial, TrialLocation, get_session
from src.metrics.calculator import MetricsCalculator
from src.ml.clustering import SiteRecommender


# Page configuration
st.set_page_config(
    page_title="Clinical Trial Site Evaluation",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
    <style>
    .main {
        padding: 0rem 1rem;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 20px;
        border-radius: 10px;
        margin: 10px 0;
    }
    </style>
""", unsafe_allow_html=True)


@st.cache_resource
def get_db_session():
    """Get database session"""
    try:
        return get_session()
    except Exception as e:
        st.error(f"Database connection error: {e}")
        return None


@st.cache_data(ttl=300)
def load_sites_data():
    """Load sites data from database"""
    session = get_db_session()
    if session is None:
        return pd.DataFrame()
    
    try:
        sites = session.query(SiteMaster).all()
    except Exception as e:
        st.error(f"Error loading sites data: {e}")
        return pd.DataFrame()
    
    data = []
    for site in sites:
        data.append({
            "Site Name": site.site_name,
            "City": site.city,
            "Country": site.country,
            "Total Studies": site.total_studies,
            "Completed": site.completed_studies,
            "Ongoing": site.ongoing_studies,
            "Terminated": site.terminated_studies,
            "Completion %": round(site.completion_ratio * 100, 1) if site.completion_ratio else 0,
            "Data Quality": round(site.data_quality_score, 2) if site.data_quality_score else 0,
            "Experience Index": site.experience_index or 0,
            "Avg Phase": round(site.avg_phase, 1) if site.avg_phase else None,
            "Therapeutic Areas": site.therapeutic_areas or ""
        })
    
    return pd.DataFrame(data)


@st.cache_data(ttl=300)
def load_trials_data():
    """Load trials data from database"""
    session = get_db_session()
    if session is None:
        return 0
    
    try:
        trials = session.query(ClinicalTrial).all()
        return len(trials)
    except Exception as e:
        st.error(f"Error loading trials data: {e}")
        return 0


def main():
    """Main dashboard function"""
    
    # Header
    st.title("🏥 Clinical Trial Site Evaluation Dashboard")
    st.markdown("---")
    
    # Sidebar
    with st.sidebar:
        st.header("⚙️ Filters")
        
        # Load data
        df = load_sites_data()
        
        if df.empty:
            st.warning("No data available. Please run data extraction first.")
            return
        
        # Country filter
        countries = ["All"] + sorted(df["Country"].unique().tolist())
        selected_country = st.selectbox("Country", countries)
        
        # Minimum studies filter
        min_studies = st.slider("Minimum Total Studies", 0, int(df["Total Studies"].max()), 0)
        
        # Therapeutic area filter
        therapeutic_areas = set()
        for areas in df["Therapeutic Areas"]:
            if areas:
                therapeutic_areas.update([a.strip() for a in areas.split(",")])
        
        therapeutic_areas = ["All"] + sorted(list(therapeutic_areas))
        selected_area = st.selectbox("Therapeutic Area", therapeutic_areas)
        
        st.markdown("---")
        st.header("🎯 Site Recommender")
        
        # Recommendation inputs
        target_condition = st.text_input("Target Condition", "cancer")
        target_phase = st.selectbox("Target Phase", 
            ["Phase 1", "Phase 2", "Phase 3", "Phase 4"])
        target_country = st.selectbox("Target Country", ["Any"] + sorted(df["Country"].unique().tolist()))
        
        if st.button("🔍 Find Best Sites"):
            with st.spinner("Calculating recommendations..."):
                recommender = SiteRecommender()
                recommendations = recommender.recommend_sites(
                    target_conditions=[target_condition],
                    target_phase=target_phase,
                    target_country=None if target_country == "Any" else target_country,
                    top_n=10
                )
                recommender.close()
                
                st.success("Top 10 Recommended Sites:")
                for i, (site, score) in enumerate(recommendations, 1):
                    st.write(f"{i}. {site} - Score: {score}")
    
    # Filter data
    filtered_df = df.copy()
    if selected_country != "All":
        filtered_df = filtered_df[filtered_df["Country"] == selected_country]
    if min_studies > 0:
        filtered_df = filtered_df[filtered_df["Total Studies"] >= min_studies]
    if selected_area != "All":
        filtered_df = filtered_df[filtered_df["Therapeutic Areas"].str.contains(selected_area, na=False)]
    
    # Overview metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Sites", len(filtered_df))
    with col2:
        st.metric("Total Trials", load_trials_data())
    with col3:
        avg_completion = filtered_df["Completion %"].mean()
        st.metric("Avg Completion Rate", f"{avg_completion:.1f}%")
    with col4:
        avg_quality = filtered_df["Data Quality"].mean()
        st.metric("Avg Data Quality", f"{avg_quality:.2f}")
    
    st.markdown("---")
    
    # Tabs
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "📊 Overview", "🗺️ Global Map", "🏆 Leaderboard", 
        "📈 Analytics", "📋 Site Details"
    ])
    
    with tab1:
        st.header("Overview")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Top countries by number of sites
            st.subheader("Top Countries by Number of Sites")
            country_counts = filtered_df["Country"].value_counts().head(10)
            fig = px.bar(
                x=country_counts.values,
                y=country_counts.index,
                orientation='h',
                labels={'x': 'Number of Sites', 'y': 'Country'},
                color=country_counts.values,
                color_continuous_scale='Blues'
            )
            fig.update_layout(showlegend=False, height=400)
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            # Study status distribution
            st.subheader("Study Status Distribution")
            status_data = {
                'Status': ['Completed', 'Ongoing', 'Terminated'],
                'Count': [
                    filtered_df['Completed'].sum(),
                    filtered_df['Ongoing'].sum(),
                    filtered_df['Terminated'].sum()
                ]
            }
            fig = px.pie(
                status_data,
                values='Count',
                names='Status',
                color='Status',
                color_discrete_map={
                    'Completed': '#2ecc71',
                    'Ongoing': '#3498db',
                    'Terminated': '#e74c3c'
                }
            )
            fig.update_layout(height=400)
            st.plotly_chart(fig, use_container_width=True)
        
        # Completion rate vs data quality scatter
        st.subheader("Completion Rate vs Data Quality")
        fig = px.scatter(
            filtered_df,
            x='Data Quality',
            y='Completion %',
            size='Total Studies',
            color='Country',
            hover_name='Site Name',
            labels={'Completion %': 'Completion Rate (%)', 'Data Quality': 'Data Quality Score'}
        )
        fig.update_layout(height=500)
        st.plotly_chart(fig, use_container_width=True)
    
    with tab2:
        st.header("Global Site Distribution")
        
        # Prepare map data
        map_data = filtered_df.groupby('Country').agg({
            'Site Name': 'count',
            'Total Studies': 'sum',
            'Completion %': 'mean'
        }).reset_index()
        map_data.columns = ['Country', 'Sites', 'Total Studies', 'Avg Completion %']
        
        # World map
        fig = px.choropleth(
            map_data,
            locations='Country',
            locationmode='country names',
            color='Sites',
            hover_name='Country',
            hover_data=['Total Studies', 'Avg Completion %'],
            color_continuous_scale='YlOrRd',
            title='Number of Clinical Trial Sites by Country'
        )
        fig.update_layout(height=600)
        st.plotly_chart(fig, use_container_width=True)
    
    with tab3:
        st.header("🏆 Top Performing Sites")
        
        # Sort by completion rate
        leaderboard = filtered_df.sort_values('Completion %', ascending=False).head(20)
        
        # Display as table with styling
        st.dataframe(
            leaderboard[[
                'Site Name', 'Country', 'Total Studies', 
                'Completed', 'Completion %', 'Data Quality'
            ]],
            use_container_width=True,
            height=600
        )
        
        # Top performers chart
        st.subheader("Top 10 Sites by Completion Rate")
        top_10 = leaderboard.head(10)
        fig = px.bar(
            top_10,
            x='Completion %',
            y='Site Name',
            orientation='h',
            color='Data Quality',
            color_continuous_scale='Greens',
            labels={'Completion %': 'Completion Rate (%)'}
        )
        fig.update_layout(height=500, yaxis={'categoryorder': 'total ascending'})
        st.plotly_chart(fig, use_container_width=True)
    
    with tab4:
        st.header("📈 Advanced Analytics")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Data quality distribution
            st.subheader("Data Quality Distribution")
            fig = px.histogram(
                filtered_df,
                x='Data Quality',
                nbins=20,
                labels={'Data Quality': 'Data Quality Score'},
                color_discrete_sequence=['#3498db']
            )
            fig.update_layout(height=400)
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            # Experience index distribution
            st.subheader("Experience Index Distribution")
            fig = px.histogram(
                filtered_df,
                x='Experience Index',
                nbins=20,
                labels={'Experience Index': 'Experience Index (Total Studies)'},
                color_discrete_sequence=['#9b59b6']
            )
            fig.update_layout(height=400)
            st.plotly_chart(fig, use_container_width=True)
        
        # Correlation heatmap
        st.subheader("Metrics Correlation")
        corr_cols = ['Total Studies', 'Completed', 'Ongoing', 'Terminated', 
                     'Completion %', 'Data Quality', 'Experience Index']
        corr_data = filtered_df[corr_cols].corr()
        
        fig = px.imshow(
            corr_data,
            labels=dict(color="Correlation"),
            x=corr_cols,
            y=corr_cols,
            color_continuous_scale='RdBu',
            zmin=-1,
            zmax=1
        )
        fig.update_layout(height=600)
        st.plotly_chart(fig, use_container_width=True)
    
    with tab5:
        st.header("📋 Detailed Site Information")
        
        # Site selector
        site_names = filtered_df["Site Name"].tolist()
        selected_site = st.selectbox("Select a site", site_names)
        
        if selected_site:
            site_info = filtered_df[filtered_df["Site Name"] == selected_site].iloc[0]
            
            # Display site details
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric("Total Studies", site_info["Total Studies"])
                st.metric("Completed Studies", site_info["Completed"])
            
            with col2:
                st.metric("Ongoing Studies", site_info["Ongoing"])
                st.metric("Terminated Studies", site_info["Terminated"])
            
            with col3:
                st.metric("Completion Rate", f"{site_info['Completion %']:.1f}%")
                st.metric("Data Quality Score", f"{site_info['Data Quality']:.2f}")
            
            st.markdown("---")
            
            # Therapeutic areas
            st.subheader("Therapeutic Areas")
            if site_info["Therapeutic Areas"]:
                areas = [a.strip() for a in site_info["Therapeutic Areas"].split(",")[:10]]
                st.write(", ".join(areas))
            else:
                st.write("Not available")
            
            # Get strengths and weaknesses
            st.subheader("Performance Analysis")
            
            session = get_db_session()
            site_record = session.query(SiteMaster).filter_by(
                site_name=selected_site
            ).first()
            
            if site_record:
                calculator = MetricsCalculator()
                analysis = calculator.generate_strengths_weaknesses(site_record)
                calculator.close()
                
                col1, col2 = st.columns(2)
                
                with col1:
                    st.markdown("**Strengths:**")
                    if analysis["strengths"]:
                        for strength in analysis["strengths"]:
                            st.write(strength)
                    else:
                        st.write("No specific strengths identified")
                
                with col2:
                    st.markdown("**Weaknesses:**")
                    if analysis["weaknesses"]:
                        for weakness in analysis["weaknesses"]:
                            st.write(weakness)
                    else:
                        st.write("No specific weaknesses identified")


if __name__ == "__main__":
    main()
