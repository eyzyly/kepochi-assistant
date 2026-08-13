import pandas as pd

from kepochi.llm import chat_json

SYSTEM_PROMPT = """You generate realistic synthetic family data for a Jeopardy-style trivia game.
Create 5 fictional individuals belonging to the same extended family (mix of generations:
grandparents, parents, aunts/uncles, nephews/nieces). For each person, provide demographics
and 5 personal Q&A responses (favourite football club, favourite meal, favourite toy, favourite
video game or movie, and one more of your choosing). Questions do not need to be standardized
across people - tailor them to each person's demographics (e.g. a 6 year old gets asked about
favourite toy, not favourite football club).

Return strict JSON with this shape:
{
  "demographics": [
    {"person_id": "P1", "name": "...", "age": 34, "gender": "...",
     "country_of_birth": "...", "ethnicity": "...", "current_city": "..."}
  ],
  "responses": [
    {"person_id": "P1", "question_id": "Q1", "question": "...", "answer": "..."}
  ]
}

Each person must have exactly 5 responses (25 rows total in "responses").
"""


def generate_synthetic_data(context_prompt=""):
    user_prompt = context_prompt or "Generate a typical extended family."
    data = chat_json(SYSTEM_PROMPT, user_prompt)
    demographics = pd.DataFrame(data["demographics"])
    responses = pd.DataFrame(data["responses"])
    return demographics, responses


def save_synthetic_data(demographics, responses, out_dir="data"):
    demographics.to_csv(f"{out_dir}/demographics.csv", index=False)
    responses.to_csv(f"{out_dir}/responses.csv", index=False)
