## Evaluation criteria self-assessment

This project was built for the
[LLM Zoomcamp evaluation criteria](https://github.com/DataTalksClub/llm-zoomcamp/blob/main/project.md#evaluation-criteria).
Honest self-assessment against each dimension, to save reviewers time:

| Criterion | Status | Notes |
|---|---|---|
| Problem description | Done | See [Problem](#problem) above. |
| Retrieval flow | Partial | An LLM is used with structured context (demographics + survey CSVs), but the full data is injected into every prompt rather than retrieved from an indexed knowledge base — there's no embedding/vector search step yet. |
| Retrieval evaluation | Not done | No retrieval approaches are compared, since there's no retrieval step yet (see above). |
| LLM evaluation | Not done | Prompts were iterated on manually against sample outputs (see commit history in [kepochi/game.py](kepochi/game.py)), but no systematic prompt/approach comparison exists yet. |
| Interface | Done | Streamlit UI ([kepochi/app.py](kepochi/app.py)). |
| Ingestion pipeline | Partial | Synthetic data generation and CSV loading are manual/semi-automated via the UI; no dedicated ingestion tool (e.g. dlt) is wired up yet. |
| Monitoring | Not done | No feedback collection or dashboard yet. |
| Containerization | Not done | Runs locally via `uv`; no Dockerfile/docker-compose yet. |
| Reproducibility | Done | Setup/run steps above; dependencies pinned in `uv.lock`; sample data included in `data/`. |

### Roadmap to close the gaps above

- Move the family knowledge base into SQLite (as originally scoped) and add a retrieval step
  (even simple keyword/SQL filtering) instead of dumping the full CSV into every prompt.
- Add a small eval set (expected topics/clue style per family profile) and compare at least two
  prompt variants for topic generation and clue generation.
- Add Dockerfile/docker-compose for one-command startup.
- Add lightweight feedback capture (e.g. thumbs up/down per clue) surfaced in a small dashboard.
