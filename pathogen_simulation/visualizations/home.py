import streamlit as st

def display_home_page():
    """Display the home page content"""
    # Main title with custom styling
    st.markdown("""
        <h1 style='text-align: center; color: #1E88E5; font-size: 4rem; margin-bottom: 2rem;'>
            PathFlow
        </h1>
    """, unsafe_allow_html=True)
    
    # Description section
    st.markdown("""
        <div style='text-align: center; padding: 2rem; background-color: #f8f9fa; border-radius: 10px; margin-bottom: 2rem;'>
            <p style='font-size: 1.2rem; color: #424242; line-height: 1.6;'>
                PathFlow is a comprehensive platform for simulating and analyzing the spread of infectious diseases across global populations. 
                Utilizing advanced mathematical models and real-world data, it provides insights into disease progression, healthcare system impacts, 
                and intervention effectiveness.
            </p>
        </div>
    """, unsafe_allow_html=True)
    
    # Feature cards
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
            <div style='padding: 1.5rem; background-color: white; border-radius: 10px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); height: 100%;'>
                <h3 style='color: #1E88E5;'>Key Features</h3>
                <ul style='color: #424242;'>
                    <li>Real-time disease spread visualization</li>
                    <li>Global impact assessment</li>
                    <li>Healthcare system load analysis</li>
                    <li>Variant tracking and monitoring</li>
                </ul>
            </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
            <div style='padding: 1.5rem; background-color: white; border-radius: 10px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); height: 100%;'>
                <h3 style='color: #1E88E5;'>Get Started</h3>
                <p style='color: #424242;'>
                    Navigate through different views using the sidebar menu to:
                    <ul>
                        <li>Simulate infection progression</li>
                        <li>Visualize global spread</li>
                        <li>Analyze healthcare impacts</li>
                        <li>Track disease variants</li>
                    </ul>
                </p>
            </div>
        """, unsafe_allow_html=True)