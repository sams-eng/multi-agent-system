"""
Streamlit UI for the multi-agent research system.

Run with:
    streamlit run app.py

The UI re-uses the agents from agents.py and runs the same four steps as
pipeline.py, but step by step so progress can be shown live.
pipeline.py itself is not modified and still works from the terminal.
"""

import time
import traceback

import streamlit as st

from agents import (
    build_search_agent,
    build_reader_agent,
    writer_chain,
    critic_chain,
)

# --------------------------------------------------------------------------
# Page setup
# --------------------------------------------------------------------------
st.set_page_config(
    page_title="Research Assistant",
    page_icon="🔎",
    layout="wide",
)

st.markdown(
    """
    <style>
        .block-container { max-width: 1100px; padding-top: 2.5rem; }
        h1 { letter-spacing: -0.02em; }
        .stTabs [data-baseweb="tab-list"] { gap: 1.25rem; }
        .stTabs [data-baseweb="tab"] { padding-left: 0; padding-right: 0; }
    </style>
    """,
    unsafe_allow_html=True,
)

# --------------------------------------------------------------------------
# Session state (keeps results alive across reruns, e.g. after a download click)
# --------------------------------------------------------------------------
if "result" not in st.session_state:
    st.session_state.result = None
if "topic" not in st.session_state:
    st.session_state.topic = ""
if "history" not in st.session_state:
    st.session_state.history = []  # list of {"topic": str, "state": dict, "seconds": float}


# --------------------------------------------------------------------------
# Pipeline (same logic as pipeline.py, with UI progress hooks)
# --------------------------------------------------------------------------
def run_pipeline_with_ui(topic: str) -> dict:
    """Run the four pipeline steps and report progress in the UI."""
    state = {}

    with st.status("Researching…", expanded=True) as status:
        # Step 1 - search
        status.update(label="Step 1 of 4: Searching the web…")
        st.write("🔎 Search agent is looking for sources.")
        search_agent = build_search_agent()
        search_out = search_agent.invoke(
            {
                "messages": [
                    (
                        "user",
                        f"Find recents, reliable and detailed information about: {topic}",
                    )
                ]
            }
        )
        state["search_results"] = search_out["messages"][-1].content
        st.write("✅ Search complete.")

        # Step 2 - reader
        status.update(label="Step 2 of 4: Reading the best source…")
        st.write("📖 Reader agent is scraping the most relevant page.")
        reader_agent = build_reader_agent()
        reader_out = reader_agent.invoke(
            {
                "messages": [
                    (
                        "user",
                        f"Based on the following search results about '{topic}', "
                        f"pick the most relevant URL and scrape it for deeper content.\n\n"
                        f"Search Results:\n{state['search_results'][:800]}",
                    )
                ]
            }
        )
        state["scraped_content"] = reader_out["messages"][-1].content
        st.write("✅ Source read.")

        # Step 3 - writer
        status.update(label="Step 3 of 4: Writing the report…")
        st.write("✍️ Writer is drafting the report.")
        research_combined = (
            f"SEARCH RESULT : \n {state['search_results']}\n\n"
            f"DETAILED SCRAPED CONTENT : \n{state['scraped_content']}"
        )
        state["report"] = writer_chain.invoke(
            {"topic": topic, "research": research_combined}
        )
        st.write("✅ Draft ready.")

        # Step 4 - critic
        status.update(label="Step 4 of 4: Reviewing the report…")
        st.write("🧐 Critic is reviewing the draft.")
        state["feedback"] = critic_chain.invoke({"report": state["report"]})
        st.write("✅ Review complete.")

        status.update(label="Research complete", state="complete", expanded=False)

    return state


def as_text(value) -> str:
    """Chain outputs can be str or a message object; normalise to text."""
    if value is None:
        return ""
    return value if isinstance(value, str) else getattr(value, "content", str(value))


# --------------------------------------------------------------------------
# Sidebar
# --------------------------------------------------------------------------
with st.sidebar:
    st.header("How it works")
    st.markdown(
        "1. **Search agent** finds current sources\n"
        "2. **Reader agent** scrapes the best one\n"
        "3. **Writer** drafts a report\n"
        "4. **Critic** reviews the draft"
    )

    st.divider()
    st.subheader("Previous searches")
    if not st.session_state.history:
        st.caption("Your completed searches will appear here.")
    else:
        for i, item in enumerate(reversed(st.session_state.history)):
            if st.button(item["topic"], key=f"hist_{i}", use_container_width=True):
                st.session_state.result = item["state"]
                st.session_state.topic = item["topic"]
                st.rerun()
        if st.button("Clear history", use_container_width=True):
            st.session_state.history = []
            st.session_state.result = None
            st.rerun()

# --------------------------------------------------------------------------
# Main area
# --------------------------------------------------------------------------
st.title("Research Assistant")
st.caption("Enter a topic and a team of agents will search, read, write and review a report.")

with st.form("research_form", clear_on_submit=False):
    topic_input = st.text_input(
        "Research topic",
        value=st.session_state.topic,
        placeholder="e.g. Latest advances in solid-state batteries",
    )
    submitted = st.form_submit_button("Start research", type="primary")

if submitted:
    topic = topic_input.strip()
    if not topic:
        st.warning("Enter a topic to research.")
    else:
        st.session_state.topic = topic
        st.session_state.result = None
        started = time.time()
        try:
            result = run_pipeline_with_ui(topic)
            elapsed = time.time() - started
            st.session_state.result = result
            st.session_state.history.append(
                {"topic": topic, "state": result, "seconds": elapsed}
            )
            st.toast(f"Finished in {elapsed:.0f}s", icon="✅")
        except Exception as exc:
            st.error(f"The research pipeline failed: {exc}")
            with st.expander("Error details"):
                st.code(traceback.format_exc())

# --------------------------------------------------------------------------
# Results
# --------------------------------------------------------------------------
result = st.session_state.result

if result:
    st.divider()
    st.subheader(f"Results: {st.session_state.topic}")

    report_tab, critic_tab, search_tab, scrape_tab = st.tabs(
        ["Report", "Critic feedback", "Search results", "Scraped content"]
    )

    report_text = as_text(result.get("report"))
    feedback_text = as_text(result.get("feedback"))

    with report_tab:
        st.markdown(report_text)
        safe_name = "".join(
            c if c.isalnum() or c in "-_ " else "" for c in st.session_state.topic
        ).strip().replace(" ", "_") or "report"
        st.download_button(
            "Download report (.md)",
            data=report_text,
            file_name=f"{safe_name}.md",
            mime="text/markdown",
        )

    with critic_tab:
        st.markdown(feedback_text)

    with search_tab:
        st.markdown(as_text(result.get("search_results")))

    with scrape_tab:
        st.markdown(as_text(result.get("scraped_content")))
else:
    st.info("Your report will appear here once the research finishes.")