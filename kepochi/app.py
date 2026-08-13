import os
import sys

import pandas as pd
import streamlit as st

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, PROJECT_ROOT)
DATA_DIR = os.path.join(PROJECT_ROOT, "data")

from kepochi.game import build_game_csv, generate_questions, generate_topics
from kepochi.synthetic_data import generate_synthetic_data, save_synthetic_data

st.set_page_config(page_title="Kepochi", page_icon="🕹️")
st.title("🕹️ Kepochi — Family Jeopardy Generator")

if "demographics" not in st.session_state:
    st.session_state.demographics = None
    st.session_state.responses = None
if "topics" not in st.session_state:
    st.session_state.topics = None
if "selected_topics" not in st.session_state:
    st.session_state.selected_topics = []
if "questions_by_topic" not in st.session_state:
    st.session_state.questions_by_topic = {}

st.header("Step 1: Family data")
data_source = st.radio(
    "Data source",
    ["Generate synthetic data", "Load from CSV"],
    horizontal=True,
)

def _reset_downstream_state():
    st.session_state.topics = None
    st.session_state.selected_topics = []
    st.session_state.questions_by_topic = {}


if data_source == "Generate synthetic data":
    context_prompt = st.text_input("Optional context for the family (e.g. 'Malaysian family, 3 generations')")
    if st.button("Generate synthetic data"):
        with st.spinner("Generating synthetic family data..."):
            demographics, responses = generate_synthetic_data(context_prompt)
            st.session_state.demographics = demographics
            st.session_state.responses = responses
            save_synthetic_data(demographics, responses, out_dir=DATA_DIR)
            _reset_downstream_state()
else:
    demo_path = st.text_input("Demographics CSV path", value=os.path.join(DATA_DIR, "demographics.csv"))
    resp_path = st.text_input("Responses CSV path", value=os.path.join(DATA_DIR, "responses.csv"))
    if st.button("Load from CSV"):
        try:
            st.session_state.demographics = pd.read_csv(demo_path)
            st.session_state.responses = pd.read_csv(resp_path)
            _reset_downstream_state()
            st.success(f"Loaded {demo_path} and {resp_path}")
        except FileNotFoundError as e:
            st.error(f"Could not find file: {e.filename}")

if st.session_state.demographics is not None:
    st.subheader("Demographics")
    st.dataframe(st.session_state.demographics)
    st.subheader("Survey Responses")
    st.dataframe(st.session_state.responses)

    st.header("Step 2: Pick topics")
    if st.button("Generate 10 candidate topics"):
        with st.spinner("Generating topics..."):
            st.session_state.topics = generate_topics(
                st.session_state.demographics, st.session_state.responses
            )

    if st.session_state.topics:
        st.session_state.selected_topics = st.multiselect(
            "Select up to 5 topics for the game",
            st.session_state.topics,
            max_selections=5,
        )

    st.header("Step 3: Generate questions")
    if st.session_state.selected_topics and st.button("Generate questions for selected topics"):
        with st.spinner("Generating questions..."):
            questions_by_topic = {}
            for topic in st.session_state.selected_topics:
                questions_by_topic[topic] = generate_questions(
                    st.session_state.demographics, st.session_state.responses, topic
                )
            st.session_state.questions_by_topic = questions_by_topic

    for topic, questions in st.session_state.questions_by_topic.items():
        st.subheader(topic)
        st.table(pd.DataFrame(questions))

    st.header("Step 4: Export game CSV")
    if st.session_state.questions_by_topic and st.button("Build game.csv"):
        topics_with_questions = list(st.session_state.questions_by_topic.items())
        game_df = build_game_csv(topics_with_questions)
        game_path = os.path.join(DATA_DIR, "game.csv")
        game_df.to_csv(game_path, index=False)
        st.success(f"Saved to {game_path}")
        st.dataframe(game_df)
        st.download_button(
            "Download game.csv",
            game_df.to_csv(index=False),
            file_name="game.csv",
            mime="text/csv",
        )
