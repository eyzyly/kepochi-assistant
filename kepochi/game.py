import random
import string

import pandas as pd

from kepochi.llm import chat_json

SYSTEM_PROMPT = """You are a master Jeopardy game maker. You will be given context about a group
of family members playing the game (their demographics and personal survey responses) and come
up with interesting questions. Questions need to be concise and easy for a 5 year old to understand
where possible, while still being interesting for adults.
"""

TOPICS_PROMPT_TEMPLATE = """Family context (demographics + survey responses):
{context}

Generate a list of 10 candidate Jeopardy topics based on this context. Each topic should be
something the family can learn about one another from (e.g. "Uncle Ben's Favourite Foods",
"Guess Whose Childhood Toy"). The topics should not be refer to a specific family member but rather a general theme around the question.
Topics must not be repetitive.

Return strict JSON: {{"topics": ["topic 1", "topic 2", ...]}}
"""

ANSWERS_PROMPT_TEMPLATE = """Family context (demographics + survey responses):
{context}

For the Jeopardy topic "{topic}", pick exactly 5 distinct answers worth 200, 400, 600, 800, 1000
points respectively. Each answer should be phrased in Jeopardy style ("Who is ...?" or
"What is ...?") and grounded in the survey responses/demographics above. Points should reflect
how well-known/obvious vs. obscure the answer is within the family context (200 = most obvious,
1000 = most obscure), not vocabulary difficulty.

The 5 answers must all be distinct — never repeat the same answer across difficulty levels
within a topic. If the survey responses don't give you 5 distinct answers on their own, draw on
other well-known things from the same era/category to fill the gaps (e.g. for a childhood toys
topic, alongside LEGO or Barbie you could also use Hot Wheels, Care Bears, or He-Man), while
keeping every answer plausibly tied to the family context. Do not refer to any individual family
member by name.
{feedback_section}
Return strict JSON:
{{"answers": [
  {{"points": 200, "answer": "Who is ...?"}},
  ...
]}}
"""

QUESTIONS_PROMPT_TEMPLATE = """Family context (demographics + survey responses):
{context}

For the Jeopardy topic "{topic}", write a CLUE for each of these confirmed answers:
{answers}

Clues must be written in real Jeopardy style — third-person descriptive statements that build up
to the answer, never a literal question and never simply restating a survey question. Like the
examples below:

  - "This famous football team wears blue and red, and their mascot is a fierce Southern Tiger."
    -> "What is JDT (Johor Darul Ta'zim)?"
  - "Known as \"The Pocket Rocketman,\" this amazing track cyclist won Olympic medals for
    Malaysia on his fast bicycle." -> "Who is Datuk Azizulhasni Awang?"
  - "This delicious drink is a mix of both coffee and milk tea combined in one cup."
    -> "What is Kopi Cham?"

Weave in specific, vivid, playful detail pulled from the survey responses and demographics
(nicknames, quirky facts, wordplay, humour) rather than generic phrasing. The clue for the
200-point answer should describe it almost directly, and each step up to 1000 should reveal less
and require piecing together more indirect hints. Clues should still be understandable to a
5 year old where possible, and must not refer to any individual family member by name.
{feedback_section}
Return strict JSON, preserving the given points and answers exactly, one clue per answer:
{{"questions": [
  {{"points": 200, "question": "...", "answer": "Who is ...?"}},
  ...
]}}
"""

FEEDBACK_SECTION_TEMPLATE = """
The previous attempt at this topic was:
{previous_questions}

The user gave the following feedback across revision rounds so far, in order. Make sure the
latest revision still satisfies all of it, not just the most recent round:
{feedback_history}
"""


def _build_context(demographics, responses):
    return (
        "Demographics:\n" + demographics.to_csv(index=False)
        + "\nSurvey responses:\n" + responses.to_csv(index=False)
    )


def generate_topics(demographics, responses):
    context = _build_context(demographics, responses)
    data = chat_json(SYSTEM_PROMPT, TOPICS_PROMPT_TEMPLATE.format(context=context))
    return data["topics"]


def _build_feedback_section(feedback_history, previous):
    if not feedback_history:
        return ""
    numbered_feedback = "\n".join(f"{i}. {f}" for i, f in enumerate(feedback_history, start=1))
    return FEEDBACK_SECTION_TEMPLATE.format(previous_questions=previous, feedback_history=numbered_feedback)


def generate_answers(demographics, responses, topic, feedback_history=None, previous_answers=None):
    context = _build_context(demographics, responses)
    feedback_section = _build_feedback_section(feedback_history, previous_answers)
    prompt = ANSWERS_PROMPT_TEMPLATE.format(context=context, topic=topic, feedback_section=feedback_section)
    data = chat_json(SYSTEM_PROMPT, prompt)
    return data["answers"]


def generate_clues(demographics, responses, topic, answers, feedback_history=None, previous_questions=None):
    context = _build_context(demographics, responses)
    feedback_section = _build_feedback_section(feedback_history, previous_questions)
    answers_block = "\n".join(f"- {a['points']} points: {a['answer']}" for a in answers)
    prompt = QUESTIONS_PROMPT_TEMPLATE.format(
        context=context, topic=topic, answers=answers_block, feedback_section=feedback_section
    )
    data = chat_json(SYSTEM_PROMPT, prompt)
    return data["questions"]


def _random_game_id():
    suffix = "".join(random.choices(string.ascii_lowercase + string.digits, k=4))
    return f"kepochi_game_{suffix}"


def build_game_csv(topics_with_questions, game_id=None):
    game_id = game_id or _random_game_id()
    """topics_with_questions: list of (topic, [questions]) tuples."""
    rows = []
    for topic, questions in topics_with_questions:
        for i, q in enumerate(questions, start=1):
            rows.append({
                "game_id": game_id,
                "question_id": f"Q{i}",
                "category": topic,
                "points": q["points"],
                "question": q["question"],
                "answer": q["answer"],
            })
    return pd.DataFrame(rows, columns=["game_id", "question_id", "category", "points", "question", "answer"])
