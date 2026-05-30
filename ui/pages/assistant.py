import streamlit as st
import requests
from config import API_BASE_URL


def render():
    collection_name = st.session_state.get("collection_name", "")

    st.title("RepoSense")
    st.markdown(f"Collection: `{collection_name}`")
    st.divider()

    tab1, tab2, tab3, tab4 = st.tabs(["Repo Assistant", "PR Analyzer", "Log Analyzer", "Release Notes"])

    # --- Tab 1: Repo Assistant ---
    with tab1:
        st.subheader("Ask about the repository")
        question = st.text_input("Your question", placeholder="How does authentication work?")
        if st.button("Ask", type="primary", key="ask_btn"):
            if not question:
                st.error("Please enter a question.")
            else:
                with st.spinner("Thinking..."):
                    response = requests.post(f"{API_BASE_URL}/repo/ask", json={
                        "question": question,
                        "collection_name": collection_name
                    })
                    if response.status_code == 200:
                        data = response.json()["result"]
                        st.markdown(f"**Answer:** {data['answer']}")
                        st.markdown(f"**Confidence:** `{data['confidence']}`")
                        st.markdown(f"**Relevant Files:** {', '.join(data['relevant_files'])}")
                        if data["follow_up_suggestions"]:
                            st.markdown("**Follow-up suggestions:**")
                            for s in data["follow_up_suggestions"]:
                                st.markdown(f"- {s}")
                    else:
                        st.error(response.json().get("detail", "Something went wrong"))

    # --- Tab 2: PR Analyzer ---
    with tab2:
        st.subheader("Analyze a Pull Request")
        pr_url = st.text_input("PR URL", placeholder="https://github.com/user/repo/pull/1")
        if st.button("Analyze PR", type="primary", key="pr_btn"):
            if not pr_url:
                st.error("Please enter a PR URL.")
            else:
                with st.spinner("Fetching and analyzing PR..."):
                    response = requests.post(f"{API_BASE_URL}/pr/analyze", json={
                        "pr_url": pr_url,
                        "collection_name": collection_name
                    })
                    if response.status_code == 200:
                        data = response.json()["result"]
                        st.markdown(f"**Summary:** {data['summary']}")
                        st.markdown(f"**Change Type:** `{data['change_type']}`")
                        st.markdown(f"**Risk Level:** `{data['risk_level']}`")
                        if data["risk_reasons"]:
                            st.markdown("**Risk Reasons:**")
                            for r in data["risk_reasons"]:
                                st.markdown(f"- {r}")
                        if data["key_changes"]:
                            st.markdown("**Key Changes:**")
                            for kc in data["key_changes"]:
                                st.markdown(f"- `{kc['file']}` — {kc['change']}")
                        if data["review_suggestions"]:
                            st.markdown("**Review Suggestions:**")
                            for s in data["review_suggestions"]:
                                st.markdown(f"- {s}")
                    else:
                        st.error(response.json().get("detail", "Something went wrong"))

    # --- Tab 3: Log Analyzer ---
    with tab3:
        st.subheader("Analyze Application Logs")
        logs = st.text_area("Paste your logs here", height=200)
        if st.button("Analyze Logs", type="primary", key="logs_btn"):
            if not logs:
                st.error("Please paste some logs.")
            else:
                with st.spinner("Analyzing logs..."):
                    response = requests.post(f"{API_BASE_URL}/logs/analyze", json={"logs": logs})
                    if response.status_code == 200:
                        data = response.json()["result"]
                        st.markdown(f"**Summary:** {data['summary']}")
                        st.markdown(f"**Total Errors:** `{data['error_count']}`")
                        if data["errors"]:
                            st.markdown("**Errors:**")
                            for e in data["errors"]:
                                st.markdown(f"- `{e['severity'].upper()}` — {e['message']} *(fix: {e['suggested_fix']})*")
                        if data["probable_root_causes"]:
                            st.markdown("**Probable Root Causes:**")
                            for c in data["probable_root_causes"]:
                                st.markdown(f"- {c}")
                        if data["recommended_actions"]:
                            st.markdown("**Recommended Actions:**")
                            for a in data["recommended_actions"]:
                                st.markdown(f"- {a}")
                    else:
                        st.error(response.json().get("detail", "Something went wrong"))

    # --- Tab 4: Release Notes ---
    with tab4:
        st.subheader("Generate Release Notes")
        version = st.text_input("Version (optional)", placeholder="v1.2.0")
        commits_input = st.text_area("Paste commit messages (one per line)", height=150)
        if st.button("Generate", type="primary", key="release_btn"):
            if not commits_input:
                st.error("Please enter some commits.")
            else:
                with st.spinner("Generating release notes..."):
                    commits = [c.strip() for c in commits_input.strip().splitlines() if c.strip()]
                    response = requests.post(f"{API_BASE_URL}/release/generate", json={
                        "commits": commits,
                        "version": version or None
                    })
                    if response.status_code == 200:
                        data = response.json()
                        result = data["result"]
                        if data.get("version"):
                            st.markdown(f"### {data['version']}")
                        st.markdown(f"**Summary:** {result['version_summary']}")
                        if result["features"]:
                            st.markdown("**Features:**")
                            for f in result["features"]:
                                st.markdown(f"- {f}")
                        if result["bug_fixes"]:
                            st.markdown("**Bug Fixes:**")
                            for f in result["bug_fixes"]:
                                st.markdown(f"- {f}")
                        if result["improvements"]:
                            st.markdown("**Improvements:**")
                            for f in result["improvements"]:
                                st.markdown(f"- {f}")
                        if result["breaking_changes"]:
                            st.markdown("**Breaking Changes:**")
                            for f in result["breaking_changes"]:
                                st.markdown(f"- {f}")
                    else:
                        st.error(response.json().get("detail", "Something went wrong"))