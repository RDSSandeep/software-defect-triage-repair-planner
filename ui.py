import streamlit as st
import requests
import pandas as pd

API_URL = "http://127.0.0.1:8000/api/bugs"

st.set_page_config(page_title="Bug Triage & Repair Planner", layout="centered", page_icon="🐞")

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

# ✅ TABS
tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
    "📝 Submit Bug Report",
    "🔍 View Bug Reports",
    "🎯 Assign Priority",
    "📄 Bug Summary Generator",
    "📊 Regression Analyzer",
    "🔗 Traceability"
])
# =========================
# UC3.1 - Submit Bug
# =========================
with tab1:
    st.header("Submit Bug Report")
    
    with st.form("bug_form", clear_on_submit=True):
        title = st.text_input("Bug Title *", placeholder="Brief summary of the issue")
        description = st.text_area("Bug Description *", placeholder="Detailed explanation of what went wrong")
        environment = st.text_input("Environment *", placeholder="e.g. Chrome 124 on macOS Sonoma, iOS 17.4")
        steps = st.text_area("Steps to Reproduce (optional)", placeholder="1. Open app\n2. Click login...\n3. See crash")
        
        submitted = st.form_submit_button("Submit Bug Report")
        
    if submitted:
        if not title.strip() or not description.strip() or not environment.strip():
            st.error("⚠️ Required fields missing!")
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
                    st.success(f"Bug Created: `{data['id']}`")
                    st.json(data)
                else:
                    st.error("Failed to create bug.")
            except requests.exceptions.ConnectionError:
                st.error("Backend not running.")

# =========================
# UC3.2 - View Bugs
# =========================
with tab2:
    st.header("Search & List Bug Reports")

    search_id = st.text_input("Search Bug by ID", placeholder="e.g. BUG-00001").strip()
    st.markdown("<div style='height: 28px;'></div>", unsafe_allow_html=True)
    search_clicked = st.button("Search")

    if search_id or search_clicked:
        if search_id:
            try:
                response = requests.get(f"{API_URL}/{search_id}")
                if response.status_code == 200:
                    bug = response.json()
                    st.success("Bug Found")
                    st.json(bug)
                elif response.status_code == 404:
                    st.error("Bug not found")
                else:
                    st.error("Error fetching bug")
            except:
                st.error("Backend not running")

    st.divider()
    st.subheader("All Bugs")

    try:
        response = requests.get(API_URL)
        if response.status_code == 200:
            bugs = response.json()
            if bugs:
                df = pd.DataFrame(bugs)
                st.dataframe(df, use_container_width=True)
            else:
                st.info("No bugs yet")
    except:
        st.error("Backend not running")

# =================================================
# UC3.3 & UC3.4 - Assign Priority + AI Suggest
# =================================================
with tab3:
    st.header("🎯 Assign Bug Priority")
    st.markdown("Use **AI Suggest** to auto-classify the priority, then confirm or override before saving.")

    # --- Session state for suggested priority ---
    if "suggested_priority" not in st.session_state:
        st.session_state.suggested_priority = None

    bug_id_input = st.text_input("Bug ID", placeholder="e.g. BUG-00001", key="uc33_bug_id")

    # ── AI Suggest section ──────────────────────────────────────────────────
    st.markdown("#### 🤖 AI Priority Suggestion")
    st.caption("Fetches bug details and applies rule-based classification to suggest a priority.")

    if st.button("🤖 Suggest Priority", use_container_width=True):
        bid = bug_id_input.strip()
        if not bid:
            st.error("Enter a Bug ID first.")
        else:
            try:
                # 1. Fetch the bug
                fetch_resp = requests.get(f"{API_URL}/{bid}")
                if fetch_resp.status_code == 404:
                    st.error(f"Bug `{bid}` not found.")
                elif fetch_resp.status_code != 200:
                    st.error("Failed to fetch bug details.")
                else:
                    bug_data = fetch_resp.json()

                    # 2. Classify
                    classify_resp = requests.post(
                        f"{API_URL}/classify",
                        json={
                            "title": bug_data.get("title"),
                            "description": bug_data.get("description"),
                            "environment": bug_data.get("environment"),
                            "steps": bug_data.get("steps"),
                        }
                    )

                    if classify_resp.status_code == 200:
                        suggestion = classify_resp.json()
                        p = suggestion["priority"]
                        r = suggestion["reason"]

                        # Store in session state to pre-fill selector
                        st.session_state.suggested_priority = p

                        # Styled suggestion card
                        colour_map = {
                            "Critical": "#ff4b4b",
                            "High":     "#ff8c00",
                            "Medium":   "#f0c040",
                            "Low":      "#4caf50",
                        }
                        colour = colour_map.get(p, "#888")
                        st.markdown(f"""
                        <div style="
                            border-left: 5px solid {colour};
                            background: rgba(128,128,128,0.06);
                            border-radius: 8px;
                            padding: 14px 18px;
                            margin: 10px 0 18px 0;">
                            <span style="font-size:1.3rem; font-weight:700; color:{colour};">
                                {p}
                            </span>
                            <p style="margin:6px 0 0 0; color: #ccc; font-size:0.9rem;">{r}</p>
                        </div>
                        """, unsafe_allow_html=True)
                    else:
                        st.error("Classification failed.")

            except requests.exceptions.ConnectionError:
                st.error("Backend not running.")

    # ── Manual assign section ───────────────────────────────────────────────
    st.markdown("#### ✏️ Confirm & Assign Priority")

    priority_options = ["Low", "Medium", "High", "Critical"]
    default_idx = 0
    if st.session_state.suggested_priority in priority_options:
        default_idx = priority_options.index(st.session_state.suggested_priority)

    priority_choice = st.selectbox(
        "Priority Level",
        priority_options,
        index=default_idx,
        key="uc33_priority_select"
    )

    if st.button("✅ Assign Priority", use_container_width=True):
        bid = bug_id_input.strip()
        if not bid:
            st.error("Bug ID required.")
        else:
            try:
                response = requests.patch(
                    f"{API_URL}/{bid}/priority",
                    json={"priority": priority_choice}
                )
                if response.status_code == 200:
                    data = response.json()
                    st.success(f"✅ Priority **{data['priority']}** assigned to `{data['id']}`")
                    st.json(data)
                    # Reset suggestion after successful assign
                    st.session_state.suggested_priority = None
                elif response.status_code == 404:
                    st.error(f"Bug `{bid}` not found.")
                else:
                    st.error("Failed to update priority.")
                    try:
                        st.json(response.json())
                    except Exception:
                        pass
            except requests.exceptions.ConnectionError:
                st.error("Backend not running.")

# =================================================
# UC5 & UC6 - BUG SUMMARY GENERATOR
# =================================================
with tab4:
    st.header("📄 Bug Summary Generator")

    bug_id = st.text_input("Enter Bug ID for Summary", key="summary_bug")

    if st.button("Generate Summary"):
        if not bug_id:
            st.error("Bug ID required")
        else:
            try:
                summary_res = requests.post(
                f"{API_URL}/summarize",
                json={"bug_id": bug_id}
                )

                st.write("STATUS:", summary_res.status_code)   # DEBUG LINE

                if summary_res.status_code == 200:
                    data = summary_res.json()

                    st.markdown(f"""
                <h4>🧠 Summary</h4>
                <p>{data.get("summary")}</p>

                <h4>⚠️ Impact</h4>
                <p>{data.get("impact")}</p>
                """, unsafe_allow_html=True)

                else:
                    st.error(summary_res.text)

            except Exception as e:
                st.error(f"Error: {str(e)}")

# =================================================
# UC7 - REGRESSION RISK ANALYZER
# =================================================
with tab5:
    st.header("📊 Regression Risk Analyzer")

    bug_id = st.text_input("Enter Bug ID for Regression Check", key="reg_bug")

    if st.button("Analyze Risk"):
        try:
            res = requests.post(f"{API_URL}/regression", json={"bug_id": bug_id})

            if res.status_code == 200:
                data = res.json()

                st.success("Analysis Complete")

                st.metric("Regression Risk", data["regression_risk"])
                st.caption(data["note"])
            else:
                st.error("Analysis failed")
        except:
            st.error("Backend not running")

# =================================================
# UC8 - TRACEABILITY REPORT
# =================================================
with tab6:
    st.header("🔗 Traceability Report")

    bug_id = st.text_input("Enter Bug ID for Traceability", key="trace_bug")

    if st.button("Generate Traceability Report"):
        try:
            res = requests.get(f"{API_URL}/traceability/{bug_id}")

            if res.status_code == 200:
                data = res.json()

                st.success("Traceability Generated")

                st.json(data)

                st.markdown("### Coverage")
                st.info(data["coverage"])
            else:
                st.error("Bug not found")

        except:
            st.error("Backend not running")