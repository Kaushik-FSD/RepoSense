import streamlit as st
import requests
from config import API_BASE_URL


def render():
    st.title("RepoSense")
    st.markdown("#### AI-powered assistant for backend engineers")
    st.divider()

    st.subheader("Ingest a Repository")

    github_url = st.text_input("GitHub Repository URL", placeholder="https://github.com/user/repo")
    collection_name = st.text_input("Collection Name", placeholder="my-repo")
    github_token = st.text_input("GitHub Token (optional, for private repos)", type="password")

    if st.button("Ingest Repository", type="primary"):
        if not github_url or not collection_name:
            st.error("Please provide both GitHub URL and collection name.")
            return

        with st.spinner("Cloning and ingesting repository..."):
            payload = {
                "github_url": github_url,
                "collection_name": collection_name,
            }
            if github_token:
                payload["github_token"] = github_token

            try:
                response = requests.post(f"{API_BASE_URL}/repo/ingest", json=payload)
                if response.status_code == 200:
                    data = response.json()
                    st.success(f"Ingested {data['message']}")
                    # store in session so assistant page knows which collection to use
                    st.session_state["collection_name"] = collection_name
                    st.session_state["ingested"] = True
                    st.rerun()
                else:
                    st.error(f"Error: {response.json().get('detail', 'Something went wrong')}")
            except Exception as e:
                st.error(f"Could not connect to API: {str(e)}")