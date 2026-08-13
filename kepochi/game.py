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

QUESTIONS_PROMPT_TEMPLATE = """Family context (demographics + survey responses):
{context}

Generate exactly 5 Jeopardy-style question/answer pairs for the topic "{topic}", worth 200, 400,
600, 800, 1000 points respectively, in real Jeopardy style like the examples below:

  - "This famous football team wears blue and red, and their mascot is a fierce Southern Tiger."
    -> "What is JDT (Johor Darul Ta'zim)?"
  - "Known as \"The Pocket Rocketman,\" this amazing track cyclist won Olympic medals for
    Malaysia on his fast bicycle." -> "Who is Datuk Azizulhasni Awang?"
  - "This delicious drink is a mix of both coffee and milk tea combined in one cup."
    -> "What is Kopi Cham?"

The "question" field is the CLUE, written as a third-person descriptive statement, never as a
literal question and never simply restating the survey question (e.g. do NOT write "What is
their favourite football club?" — instead describe or hint at the actual answer, like the
examples above do). Weave in specific, vivid, playful detail pulled from the survey responses
and demographics (nicknames, quirky facts, wordplay, humour) rather than generic phrasing.
The "answer" field is the response, phrased in Jeopardy style ("Who is ...?" or "What is ...?").

Points should track how obscured the clue is, not just vocabulary difficulty: the 200-point clue
should describe the answer almost directly, and each step up to 1000 should reveal less and
require piecing together more indirect hints, while all 5 remain answerable from the survey
context. Clues should still be understandable to a 5 year old where possible.
The clues should not repeat the same information and must not refer to any individual family
member by name. The 5 answers must all be distinct — never reuse the same answer across
difficulty levels within a topic. If the survey responses don't give you 5 distinct answers on
their own, draw on other well-known things from the same era/category to fill the gaps (e.g. for
a childhood toys topic, alongside LEGO or Barbie you could also use Hot Wheels, Care Bears, or
He-Man), while keeping every clue plausibly tied to the family context.
{feedback_section}
Return strict JSON:
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


def generate_questions(demographics, responses, topic, feedback_history=None, previous_questions=None):
    context = _build_context(demographics, responses)
    feedback_section = ""
    if feedback_history:
        numbered_feedback = "\n".join(f"{i}. {f}" for i, f in enumerate(feedback_history, start=1))
        feedback_section = FEEDBACK_SECTION_TEMPLATE.format(
            previous_questions=previous_questions, feedback_history=numbered_feedback
        )
    prompt = QUESTIONS_PROMPT_TEMPLATE.format(context=context, topic=topic, feedback_section=feedback_section)
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
