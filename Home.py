import streamlit as st

st.set_page_config(
    page_title="Data Contract Copilot",
    page_icon="🤖",
    layout="wide"
)

# Main title with style
st.markdown("""
    <h1 style='text-align: center; margin-bottom: 2rem;'>
        🤖 Data Contract Copilot
    </h1>
    """, unsafe_allow_html=True)

# Main description
st.markdown("""
    <div style='text-align: center; margin-bottom: 3rem;'>
        <p style='font-size: 1.2em; color: #666;'>
            Your intelligent assistant for data contract management
        </p>
    </div>
    """, unsafe_allow_html=True)

# Create three columns for main features
col1, col2, col3, col4, col5 = st.columns([3, 1.5, 3, 1.5, 3])

with col1:
    st.markdown("""
        ### 📝 Automatic Generation
        Create data contracts automatically from your CSV files and documentation
        using artificial intelligence.
    """)

with col3:
    st.markdown("""
        ### ✨ Intelligent Validation
        Validate your data against defined expectations and detect anomalies
        automatically.
    """)

with col5:
    st.markdown("""
        ### 🔄 Easy Integration
        Easily integrate data contracts into your data pipeline
        with Great Expectations.
    """)

# Separator
st.markdown("<hr>", unsafe_allow_html=True)

# Replace current quickstart section with this:
col1, col2, col3, col4, col5 = st.columns([2, 2.1, 0.5, 2.1, 2])

with col2.container(gap="large"):
    # Quick start for Generate
    st.markdown("""
        ## 🚀 Generate Configuration

        1. **Select "Generate Configuration"** in the sidebar
        2. **Upload your files:**
            - A CSV file with sample data
            - A documentation file (TXT/MD)
        3. **Configure your OpenAI** API key
        4. **Done!** The copilot will generate your data contract
    """, width="stretch")
    if st.button("🔄 Generate New Configuration", use_container_width=True):
        st.switch_page("pages/Generate_Configuration.py")

# Quick start for Load
with col4.container(gap="large"):
    st.markdown("""
        ## 📋 Load Configuration

        1. **Select "Load Configuration"** in the sidebar
        2. **Upload your files:**
            - A CSV file with data to validate
            - Your existing configuration (YAML/JSON)
        3. **Review the results** of the validation
        4. **Done!** You'll see your dataset analysis
    """)
    if st.button("📋 Load Existing Configuration", use_container_width=True):
        st.switch_page("pages/Load_Configuration.py")

# Footer with additional information
st.markdown("<hr>", unsafe_allow_html=True)
st.markdown("""
    <div style='text-align: center; margin-top: 2rem;'>
        <p>
            Developed with ❤️ using
            <a href="https://streamlit.io" target="_blank">Streamlit</a> and
            <a href="https://greatexpectations.io" target="_blank">Great Expectations</a>
        </p>
    </div>
    """, unsafe_allow_html=True)

# Sidebar
st.sidebar.success("Select an option to begin")
