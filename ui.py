import streamlit as st
import requests
import pandas as pd

API_URL = "http://127.0.0.1:8000/api/bugs"

st.set_page_config(page_title="Bug Triage & Repair Planner", layout="centered", page_icon="🐞")

# Inject custom Google Font and general styling enhancements
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;600;700&display=swap');
html, body, [class*="css"] {
    font-family: 'Outfit', sans-serif;
}
.report-card {
    border-radius: 10px;
    padding: 20px;
    background-color: rgba(128, 128, 128, 0.05);
    border: 1px solid rgba(128, 128, 128, 0.1);
    margin-bottom: 15px;
}
.report-card h3 {
    margin-top: 0px;
}
</style>
""", unsafe_allow_html=True)

st.title("🐞 Bug Triage & Repair Planner")
st.markdown("Automated bug intake, lookup, and triage tracking system.")

tab1, tab2 = st.tabs(["📝 Submit Bug Report", "🔍 View Bug Reports"])

with tab1:
    st.header("Submit Bug Report")
    st.markdown("Fill out the details below to log a new defect report in the system.")
    
    with st.form("bug_form", clear_on_submit=True):
        title = st.text_input("Bug Title *", placeholder="Brief summary of the issue")
        description = st.text_area("Bug Description *", placeholder="Detailed explanation of what went wrong")
        environment = st.text_input("Environment *", placeholder="e.g. Chrome 124 on macOS Sonoma, iOS 17.4")
        steps = st.text_area("Steps to Reproduce (optional)", placeholder="1. Open app\n2. Click login...\n3. See crash")
        
        submitted = st.form_submit_button("Submit Bug Report")
        
    if submitted:
        if not title.strip() or not description.strip() or not environment.strip():
            st.error("⚠️ Title, Description, and Environment are required fields!")
        else:
            payload = {
                "title": title.strip(),
                "description": description.strip(),
                "environment": environment.strip(),
                "steps": steps.strip() if steps.strip() else None
            }
            try:
                response = requests.post(API_URL, json=payload)
                if response.status_code in (200, 201):
                    data = response.json()
                    st.success(f"✅ **Bug Logged Successfully!** Assigned ID: `{data['id']}`")
                    st.json(data)
                else:
                    st.error("❌ Failed to create bug report.")
                    try:
                        st.json(response.json())
                    except Exception:
                        st.write(response.text)
            except requests.exceptions.ConnectionError:
                st.error("❌ **Connection Error!** Make sure the FastAPI backend is running.")

with tab2:
    st.header("Search & List Bug Reports")
    
    col1, col2 = st.columns([3, 1])
    
    with col1:
        search_id = st.text_input("Search Bug by ID", placeholder="e.g. BUG-00001").strip()
    with col2:
        st.markdown("<div style='height: 28px;'></div>", unsafe_allow_html=True)
        search_clicked = st.button("Search", use_container_width=True)
        
    if search_id or search_clicked:
        if not search_id:
            st.warning("Please enter a Bug ID to search.")
        else:
            try:
                response = requests.get(f"{API_URL}/{search_id}")
                if response.status_code == 200:
                    bug = response.json()
                    st.markdown("### Bug Details")
                    with st.container():
                        st.markdown(f"""
                        <div class='report-card'>
                            <h3>{bug['id']}: {bug['title']}</h3>
                            <p><strong>Environment:</strong> <code>{bug['environment']}</code></p>
                            <p><strong>Created At:</strong> <i>{bug['created_at']}</i></p>
                            <p><strong>Description:</strong></p>
                            <blockquote style="margin-left: 20px; border-left: 3px solid #ff4b4b; padding-left: 10px; margin-top: 10px; margin-bottom: 10px;">
                                {bug['description']}
                            </blockquote>
                        </div>
                        """, unsafe_allow_html=True)
                        if bug.get('steps'):
                            st.markdown("**Steps to Reproduce:**")
                            st.code(bug['steps'])
                elif response.status_code == 404:
                    st.error(f"🔍 Bug with ID `{search_id}` was not found.")
                else:
                    st.error(f"❌ Error {response.status_code} occurred while fetching bug details.")
            except requests.exceptions.ConnectionError:
                st.error("❌ **Connection Error!** Make sure the FastAPI backend is running.")
                
    st.divider()
    st.subheader("All Persisted Bug Reports")
    
    # Auto-load list of bugs
    try:
        response = requests.get(API_URL)
        if response.status_code == 200:
            bugs = response.json()
            if not bugs:
                st.info("ℹ️ No bug reports have been submitted yet.")
            else:
                df = pd.DataFrame(bugs)
                cols = ['id', 'title', 'environment', 'created_at']
                st.dataframe(df[cols], use_container_width=True, hide_index=True)
                
                st.markdown("#### Expanded view")
                for bug in bugs:
                    with st.expander(f"🐞 **{bug['id']}**: {bug['title']} ({bug['environment']})"):
                        st.write(f"**Description:** {bug['description']}")
                        if bug.get('steps'):
                            st.write(f"**Steps to Reproduce:**")
                            st.code(bug['steps'])
                        st.caption(f"Created: {bug['created_at']}")
        else:
            st.error("❌ Failed to retrieve bug list from backend.")
    except requests.exceptions.ConnectionError:
        st.error("❌ **Connection Error!** Make sure the FastAPI backend is running.")