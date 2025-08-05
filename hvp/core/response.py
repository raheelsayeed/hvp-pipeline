from typing import Dict,  List
from pydantic import BaseModel
from datetime import datetime


class ResponseRecord(BaseModel):
    participant_id: str
    question_id: str
    answer_set_id: str
    answer_value: str
    timestamp: datetime

    @staticmethod
    def load_all_responses(directory: str) -> List[Dict]:
        import os, glob, json
        records: List[Dict] = []
        pattern = os.path.join(directory, '**', '*.json')
        for filepath in glob.glob(pattern, recursive=True):
            with open(filepath, 'r') as f:
                data = json.load(f)
                records.append(ResponseRecord(**data))
        return records

