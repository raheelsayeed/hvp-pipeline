from typing import Iterable, Dict, Tuple, List, Set, Any
from datetime import datetime
from pydantic import BaseModel, Field

# NOTE:
# We purposefully avoid importing ResponseRecord here to prevent a circular import
# (hvp.core.response -> hvp.funcs.concordance -> hvp.core.response).
# The functions operate on any objects that expose: question_id, answer_value, timestamp.

class ConcordanceResult(BaseModel):
    """
    Concordance summary between two sets of ResponseRecord-like objects.

    - rate: matches / overlap (0.0 if overlap == 0)
    - matches: count where both answered and values are equal
    - overlap: count of questions answered by both (by question_id)
    - matched_question_ids / mismatched_question_ids: for audit/debug
    """
    rate: float
    matches: int
    overlap: int
    matched_question_ids: List[str] = Field(default_factory=list)
    mismatched_question_ids: List[str] = Field(default_factory=list)


def _latest_answers_map(responses: Iterable[Any]) -> Dict[str, Tuple[datetime, str]]:
    """
    Collapse multiple answers per question to the latest by timestamp.

    Returns: question_id -> (timestamp, answer_value_as_str)
    Expects each item to have attributes: question_id, answer_value, timestamp.
    """
    latest: Dict[str, Tuple[datetime, str]] = {}
    for r in responses:
        qid = getattr(r, "question_id")
        val = str(getattr(r, "answer_value")).strip()
        ts = getattr(r, "timestamp")
        prev = latest.get(qid)
        if prev is None or ts > prev[0]:
            latest[qid] = (ts, val)
    return latest


def concordance_rate(
    responses_a: Iterable[Any],
    responses_b: Iterable[Any],
) -> ConcordanceResult:
    """
    Compute concordance between two user response lists.

    Definition:
      - Overlap: questions answered by **both** A and B (by question_id),
        after collapsing to latest answer per question.
      - Match: for an overlapping question_id, `answer_value` strings are exactly equal.

    Complexity: O(N + M) time, O(N + M) space (hash-map join), where N and M are list sizes.
    """
    latest_a = _latest_answers_map(responses_a)
    latest_b = _latest_answers_map(responses_b)

    ids_a: Set[str] = set(latest_a.keys())
    ids_b: Set[str] = set(latest_b.keys())
    overlap_ids = ids_a & ids_b

    if not overlap_ids:
        return ConcordanceResult(rate=0.0, matches=0, overlap=0)

    matches = 0
    matched_ids: List[str] = []
    mismatched_ids: List[str] = []

    for qid in overlap_ids:
        if latest_a[qid][1] == latest_b[qid][1]:
            matches += 1
            matched_ids.append(qid)
        else:
            mismatched_ids.append(qid)

    rate = matches / len(overlap_ids)
    return ConcordanceResult(
        rate=rate,
        matches=matches,
        overlap=len(overlap_ids),
        matched_question_ids=matched_ids,
        mismatched_question_ids=mismatched_ids,
    )
