# Kepochi

LLM-powered family Jeopardy generator. POC uses synthetic family data (no real survey
ingestion yet) to prove out the generation pipeline: demographics/responses -> topics ->
questions -> game.csv (matching `data/llm_capstone_output_sample.csv` schema).

## Setup

```
cp .envrc_template .envrc   # fill in OPENAI_API_KEY, then `source .envrc` or use direnv
pip install -e .
```

## Run

```
streamlit run kepochi/app.py
```

Walk through the app: generate synthetic data -> pick 5 of 10 suggested topics ->
generate questions -> export `data/game.csv`.
