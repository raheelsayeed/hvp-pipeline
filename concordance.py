#!/usr/bin/env python
from rich.console import Console
from hvp.core import question, response
from typing import Optional, List, Iterable, Any, Dict, Tuple
import json, re
p = Console().print

# Load question data from a JSON file outside the package
def load_question_from_file(file_path):
    with open(file_path, 'r') as file:
        return json.load(file)

triage_questions = '/Users/raheel/dbmi/humanValuesProject/hvp-app/static/demo/triage_pilot_v2_ids.json'  
question_data = load_question_from_file(triage_questions)

questions = [question.Question(**q) for q in question_data if q.get('metadata', {}).get('zak_choice', None) is not None]
question_identifiers = [question.identifier for question in questions]
p(f'Number of questions loaded: {len(questions)}')
p(questions[0].version)



response_files_path = 'human_responses/raheel.sayeed@gmail.com/TRIAGE/'
response_records = response.ResponseRecord.load_all_responses(response_files_path)

# filter responses to only the questions_pool 
response_records = [rr for rr in response_records if rr.question_id in question_identifiers]
p(f'Number of Responses: {len(response_records)}')
p(response_records[0])



def extract_zak_choice(q) -> Optional[str]:
    """
    Returns Zak's choice as a string (e.g., "2") if present, else None.
    If multiple zak_choice_* tags exist, last one wins (adjust if needed).
    """
    zak_val = q.metadata.get('zak_choice', None)
    zak_val = str(zak_val) if zak_val else None 
    
    return zak_val


def build_zak_map(questions: Iterable[question.Question]) -> Dict[str, str]:
    """
    Build {question_id -> zak_value_as_string}.
    Expects each question to have .identifier and .tags.
    """
    out = {}
    for q in questions:
        z = extract_zak_choice(q)
        if z is not None:
            qid = q.identifier
            out[qid] = z
    return out




def concordance_user_vs_zak(questions: Iterable[question.Question], user_responses: Iterable[response.ResponseRecord]) -> Tuple[float, int, int]: 

    zak_by_qid = build_zak_map(questions)

    matches = 0
    total = len(user_responses) 

    for i, resp in enumerate(user_responses): 

        zak_val = zak_by_qid[resp.question_id]
        user_val = resp.answer_value 
        matches += 1 if user_val == zak_val else 0 

    
    rate = matches / total 
    discordant = total - matches 
    return rate, matches, discordant 




p(concordance_user_vs_zak(questions, response_records))

from hvp.funcs import ConcordanceResult, compute_concordance_rate
# p(compute_concordance_rate(response_records, response_records))