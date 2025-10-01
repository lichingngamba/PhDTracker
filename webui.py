import streamlit as st
from utils import crawler as PhDTracker
from datetime import datetime
import pandas as pd

# Streamlit App Configuration
st.set_page_config(
    page_title="PhD Admission Tracker - Bangalore",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        padding: 2rem;
        border-radius: 10px;
        color: white;
        margin-bottom: 2rem;
    }
    .stats-card {
        background: #f0f2f6;
        padding: 1rem;
        border-radius: 8px;
        border-left: 4px solid #667eea;
    }
    .urgent-deadline {
        background: #ffebee;
        border: 1px solid #f44336;
        padding: 1rem;
        border-radius: 8px;
        margin: 1rem 0;
    }
    .success-message {
        background: #e8f5e8;
        border: 1px solid #4caf50;
        padding: 1rem;
        border-radius: 8px;
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)

# App Header
st.markdown("""
<div class="main-header">
    <h1>🎓 PhD Admission Tracker - Bangalore Universities</h1>
    <p>Real-time tracking of part-time PhD programs in Computer Science & NLP</p>
</div>
""", unsafe_allow_html=True)

# Initialize session state
if 'tracker' not in st.session_state:
    st.session_state.tracker = PhDTracker
if 'results' not in st.session_state:
    st.session_state.results = []
if 'last_crawl_time' not in st.session_state:
    st.session_state.last_crawl_time = None

# Sidebar
with st.sidebar:
    st.header("🔧 Controls")
    
    # Run crawler button
    if st.button("🚀 Run Crawler", type="primary", use_container_width=True):
        with st.spinner("Crawling universities..."):
            st.session_state.tracker.crawl_all
            st.session_state.results = st.session_state.tracker.display_results
            st.session_state.last_crawl_time = datetime.now()
        
        st.success("✅ Crawling completed!")
        st.rerun()
    
    # Display last crawl time
    if st.session_state.last_crawl_time:
        st.info(f"Last crawl: {st.session_state.last_crawl_time.strftime('%Y-%m-%d %H:%M:%S')}")


# Main content
if st.session_state.results:
    # Quick alerts
    current_date = datetime.now()
    urgent_deadlines = []
    
    st.markdown(
        st.session_state.results, unsafe_allow_html=True
                )
        

else:
    # Welcome screen
    st.markdown("""
    ## 👋 Welcome to the PhD Admission Tracker
    
    This application helps you track part-time PhD admission deadlines across Bangalore universities.
    
    ### 🚀 Getting Started
    1. Click the **"🚀 Run Crawler"** button in the sidebar to start crawling university websites
    2. The crawler will automatically check admission pages and extract deadline information
    3. View results in the tabs above once crawling is complete
    
    ### 🎯 Features
    - **Real-time crawling** of university admission pages
    - **Automatic deadline extraction** using advanced text processing
    - **Part-time program identification** for working professionals
    - **Status tracking** (Open/Closed/Upcoming applications)
    - **Downloadable results** in CSV format
    
    ### 🏛️ Universities Covered
    - IISc Bangalore (External Registration Programme)
    - REVA University
    - PES University  
    - Christ University
    - Bangalore University
    - CMR Institute of Technology
    - Jain University
    - Dayananda Sagar University
    
    **Click "🚀 Run Crawler" in the sidebar to begin!**
    """)
    

# Footer
st.markdown("---")
st.markdown("**📝 Note:** This tracker crawls public university websites. Always verify information directly with universities before applying.")