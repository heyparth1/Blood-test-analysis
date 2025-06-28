import streamlit as st
import requests
import json
import time
from typing import Optional

# Configuration
API_BASE_URL = "http://localhost:8000"

# Page configuration
st.set_page_config(
    page_title="Blood Test Analyzer",
    page_icon="🩸",
    layout="wide",
    initial_sidebar_state="expanded"
)

def check_api_health() -> Optional[dict]:
    """Check if the API is running and healthy"""
    try:
        response = requests.get(f"{API_BASE_URL}/health", timeout=5)
        return response.json() if response.status_code == 200 else None
    except:
        return None

def analyze_blood_test(file, query: str) -> Optional[dict]:
    """Send blood test file for analysis"""
    try:
        files = {"file": (file.name, file.getvalue(), "application/pdf")}
        data = {"query": query}
        
        with st.spinner("🔬 Analyzing your blood test... This may take 10-20 seconds"):
            response = requests.post(
                f"{API_BASE_URL}/analyze", 
                files=files, 
                data=data, 
                timeout=120
            )
        
        return response.json() if response.status_code == 200 else None
    except Exception as e:
        st.error(f"Error during analysis: {str(e)}")
        return None

def analyze_text_only(query: str) -> Optional[dict]:
    """Send text-only query for analysis"""
    try:
        data = {"query": query}
        
        with st.spinner("🤖 Processing your query... This may take 10-15 seconds"):
            response = requests.post(
                f"{API_BASE_URL}/analyze-text",
                json=data,
                timeout=60
            )
        
        return response.json() if response.status_code == 200 else None
    except Exception as e:
        st.error(f"Error during analysis: {str(e)}")
        return None

def get_recent_analyses() -> Optional[list]:
    """Get recent analyses from the API"""
    try:
        response = requests.get(f"{API_BASE_URL}/analyses/recent?limit=5", timeout=10)
        if response.status_code == 200:
            data = response.json()
            # Handle different possible API response formats
            if isinstance(data, list):
                return data
            elif isinstance(data, dict) and 'analyses' in data:
                return data['analyses']
            elif isinstance(data, dict) and 'data' in data:
                return data['data']
        return None
    except:
        return None

def display_analysis_result(result: dict):
    """Display analysis result in a nice format"""
    if not result:
        return
    
    # Header
    st.success("✅ Analysis Complete!")
    
    # Basic info
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Status", result.get("status", "Unknown"))
    with col2:
        if "processing_info" in result:
            processing_time = result["processing_info"].get("processing_time_seconds", 0)
            st.metric("Processing Time", f"{processing_time:.1f}s")
    with col3:
        if "file_processed" in result:
            st.metric("File Processed", result["file_processed"])
    
    # Analysis content
    st.subheader("📋 Comprehensive Medical Analysis")
    st.markdown(result.get("analysis", "No analysis available"))
    
    # Disclaimer
    st.warning("⚠️ " + result.get("disclaimer", "This analysis is for educational purposes only."))
    
    # Technical details in expander
    with st.expander("🔧 Technical Details"):
        st.json({
            "Request ID": result.get("request_id"),
            "Analysis ID": result.get("analysis_id"),
            "Analysis Approach": result.get("analysis_approach"),
            "Specialties Covered": result.get("specialties_covered"),
            "Processing Info": result.get("processing_info")
        })

# Main App
def main():
    # Header
    st.title("🩸 Professional Blood Test Analyzer")
    st.markdown("*Powered by AI-driven medical analysis with CrewAI optimization*")
    
    # Check API health
    health_status = check_api_health()
    
    # Sidebar
    with st.sidebar:
        st.header("📊 System Status")
        
        if health_status:
            st.success("✅ API is healthy")
            st.json({
                "Version": health_status.get("version"),
                "Total Analyses": health_status.get("system_status", {}).get("total_analyses", "N/A"),
                "Queue Length": health_status.get("system_status", {}).get("queue_length", "N/A")
            })
        else:
            st.error("❌ API is not responding")
            st.warning("Please ensure the FastAPI server is running on localhost:8000")
            st.code("cd blood-test-analyser-debug\npython main.py")
        
        st.divider()
        
        # Recent analyses
        st.header("📈 Recent Analyses")
        recent = get_recent_analyses()
        if recent and isinstance(recent, list) and len(recent) > 0:
            for analysis in recent[:3]:
                with st.container():
                    st.caption(f"🔬 {analysis.get('created_at', 'Unknown date')}")
                    st.text(f"File: {analysis.get('filename', 'N/A')}")
        else:
            st.info("No recent analyses found")
    
    # Main content area
    if not health_status:
        st.error("⚠️ Cannot connect to the analysis API. Please start the backend server first.")
        return
    
    # Tabs for different analysis types
    tab1, tab2 = st.tabs(["📄 File Analysis", "💬 Text Analysis"])
    
    with tab1:
        st.header("Upload Blood Test Report")
        
        # File upload
        uploaded_file = st.file_uploader(
            "Choose a PDF blood test report",
            type=['pdf'],
            help="Upload your blood test report in PDF format (max 10MB)"
        )
        
        # Query input
        query = st.text_area(
            "Analysis Request",
            value="Please provide a comprehensive analysis of my blood test results",
            height=100,
            help="Describe what specific analysis you'd like"
        )
        
        # Analyze button
        if st.button("🔬 Analyze Blood Test", type="primary", use_container_width=True):
            if uploaded_file is not None:
                result = analyze_blood_test(uploaded_file, query)
                if result:
                    display_analysis_result(result)
                else:
                    st.error("❌ Analysis failed. Please try again.")
            else:
                st.warning("⚠️ Please upload a blood test report first.")
    
    with tab2:
        st.header("Text-Only Analysis")
        st.info("📝 Get medical insights without uploading a file (uses sample data)")
        
        # Text query input
        text_query = st.text_area(
            "Your Query",
            value="What should I know about blood test interpretation?",
            height=150,
            help="Ask any question about blood tests, health markers, or medical analysis"
        )
        
        # Analyze button
        if st.button("🤖 Process Query", type="primary", use_container_width=True):
            if text_query.strip():
                result = analyze_text_only(text_query)
                if result:
                    display_analysis_result(result)
                else:
                    st.error("❌ Analysis failed. Please try again.")
            else:
                st.warning("⚠️ Please enter a query first.")
    
    # Footer
    st.divider()
    st.markdown("""
    <div style='text-align: center; color: #666; font-size: 0.8em;'>
        Professional Blood Test Analyzer • AI-Powered Medical Analysis<br>
        ⚠️ For educational purposes only - Always consult healthcare professionals
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main() 