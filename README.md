# Kepochi

An LLM-powered Jeopardy generator for family gatherings. Family members answer a short
survey about themselves; an LLM turns those answers into a custom Jeopardy board so relatives
can learn (or re-learn) fun facts about each other instead of retreating to their phones.

## Problem

At family gatherings, everyone — especially nephews, nieces, and their parents — tends to
retreat to their own screens instead of talking to each other. Extended family is often only
seen once a year, which makes it worse: there's little shared context to prompt conversation.

Kepochi ("busybody" in Malay) turns a short personal survey from each family member into a
Jeopardy-style trivia game, so playing the game itself becomes the icebreaker: kids learn about
their grandparents' era, parents learn what their kids are into, and everyone gets to be
"kepoh" (nosy) about each other in a fun, structured way.

## How it works

```
survey responses (CSV)  --\
                            >--  LLM  -->  topics  -->  LLM  -->  answers  -->  LLM  -->  clues  -->  game.csv
demographics (CSV)      --/
```

1. **Family data** — either generate synthetic demographics/survey data with an LLM (for
   testing), or load real survey responses from `demographics.csv` / `responses.csv`.
2. **Topics** — the LLM proposes 10 candidate Jeopardy categories grounded in the family data;
   the user picks up to 5.
3. **Answers, then clues** — for each selected topic, the LLM first proposes 5 distinct
   point-valued answers (200–1000) for the user to review/regenerate with feedback, then writes
   a Jeopardy-style descriptive clue for each confirmed answer, again with a feedback loop.
4. **Export** — once all topics are confirmed, the board is exported as `game.csv` in the
   schema expected by [JeopardyLabs](https://jeopardylabs.com)-style templates
   (`game_id, question_id, category, points, question, answer`).

See [kepochi/game.py](kepochi/game.py) for the prompts and [kepochi/app.py](kepochi/app.py) for
the Streamlit flow.

## Setup

Requires [uv](https://docs.astral.sh/uv/) and an OpenAI API key.

```
cp .env.template .env   # fill in OPENAI_API_KEY (loaded automatically via python-dotenv)
uv sync                 # installs pinned dependencies from uv.lock
```

## Run

```
uv run streamlit run kepochi/app.py
```

Walk through the app: choose synthetic or real family data -> pick 5 of 10 suggested topics ->
confirm answers then clues for each topic -> export `data/game.csv`.