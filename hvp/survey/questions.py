from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, List, Optional, Any, Union
from uuid import UUID, uuid4

from hvp.core.enums import QuestionType
from hvp.llm.base import PromptTemplate

@dataclass
class AnswerChoice:
    text: str
    value: str
    display_order: int = 0
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class LLMContext:
    """Context information for LLM processing of a question."""
    prompt_template: Optional[PromptTemplate] = None
    context_information: str = ""
    expected_format: str = ""
    scoring_criteria: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class QuestionItem:
    question_text: str
    answer_choices: List[AnswerChoice]
    question_type: QuestionType
    publisher: str
    canonical_id: str
    version: str = "1.0"
    created_date: datetime = field(default_factory=datetime.now)
    last_updated: datetime = field(default_factory=datetime.now)
    llm_context: Optional[LLMContext] = None
    domain: Optional[str] = None
    difficulty: float = 0.5  # 0-1 scale, higher is more difficult
    expected_time_seconds: int = 30
    translations: Dict[str, Dict[str, str]] = field(default_factory=dict)
    dependencies: List[str] = field(default_factory=list)  # List of canonical_ids this question depends on
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def __str__(self) -> str:
        return f"{self.canonical_id} ({self.question_type.value}): {self.question_text[:30]}..."
    
    def translate(self, language_code: str) -> Optional[Dict[str, str]]:
        """Get the translation for this question in the specified language."""
        return self.translations.get(language_code)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to a dictionary representation."""
        return {
            "question_text": self.question_text,
            "answer_choices": [
                {"text": choice.text, "value": choice.value} 
                for choice in self.answer_choices
            ],
            "question_type": self.question_type.value,
            "canonical_id": self.canonical_id,
            "publisher": self.publisher,
            "version": self.version,
            "domain": self.domain,
            "difficulty": self.difficulty
        }

@dataclass
class QuestionCorpus:
    questions: List[QuestionItem] = field(default_factory=list)
    name: str = "Default Corpus"
    description: str = ""
    version: str = "1.0"
    
    def add_question(self, question: QuestionItem) -> None:
        """Add a question to the corpus."""
        self.questions.append(question)
    
    def get_question(self, canonical_id: str) -> Optional[QuestionItem]:
        """Get a question by its canonical ID."""
        for question in self.questions:
            if question.canonical_id == canonical_id:
                return question
        return None
    
    def filter_questions(self, 
                        question_type: Optional[QuestionType] = None,
                        domain: Optional[str] = None,
                        difficulty_min: float = 0.0,
                        difficulty_max: float = 1.0) -> List[QuestionItem]:
        """Filter questions based on criteria."""
        filtered = self.questions
        
        if question_type:
            filtered = [q for q in filtered if q.question_type == question_type]
        
        if domain:
            filtered = [q for q in filtered if q.domain == domain]
        
        filtered = [
            q for q in filtered 
            if difficulty_min <= q.difficulty <= difficulty_max
        ]
        
        return filtered
    
    def sample_questions(self, 
                        n: int,
                        **filter_kwargs) -> List[QuestionItem]:
        """Sample n questions from the corpus, with optional filtering."""
        import random
        
        filtered = self.filter_questions(**filter_kwargs)
        
        if len(filtered) <= n:
            return filtered
        
        return random.sample(filtered, n)
    
    def __len__(self) -> int:
        return len(self.questions)