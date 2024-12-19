import streamlit as st

def links():
    with st.expander("Select your page"):
        st.page_link("streamlit_app.py", label="Home Page")
        st.page_link("pages/ivira_pod_insights.py", label="Pod Insights")