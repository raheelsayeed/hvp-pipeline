from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Tuple, Union
from datetime import datetime
import uuid
import re
import logging

from hvp.core.models import Patient
from hvp.llm.base import LLM
from hvp.survey.questions import LLMContext


logger = logging.getLogger(__name__)

@dataclass
class TriageQuestion:
    """A question comparing two patients for triage priority."""
    patient1: Patient
    patient2: Patient
    question_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    created_date: datetime = field(default_factory=datetime.now)
    expertise_required: List[str] = field(default_factory=list)
    context: str = "primary care triage"


    metadata: Dict[str, Any] = field(default_factory=dict)
    expert_answer: Optional[int] = None  # 1 or 2, indicating which patient should be seen first
    question_text: str = None 
    llm_context: Optional[LLMContext] = None
    
    def get_prompt(self, include_expert_answer: bool = False) -> str:
        """Generate a prompt for this triage question."""
        prompt = (
            f"You are an experienced clinician making triage decisions for {self.context}.\n\n"
            f"Compare the following two patients and decide who should be seen first:\n\n"
            f"Patient 1: {self.patient1.description}\n\n"
            f"Patient 2: {self.patient2.description}\n\n"
            f"Based on medical urgency and potential benefit from earlier care, which patient "
            f"should be seen first? Respond with '1' for Patient 1 or '2' for Patient 2, "
            f"followed by a brief explanation of your reasoning."
        )
        
        if include_expert_answer and self.expert_answer:
            prompt += f"\n\nExpert answer: Patient {self.expert_answer} should be seen first."
            
        return prompt
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "question_id": self.question_id,
            "patient1": self.patient1.description,
            "patient2": self.patient2.description,
            "context": self.context,
            "expertise_required": self.expertise_required,
            "expert_answer": self.expert_answer,
            "created_date": self.created_date.isoformat()
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'TriageQuestion':
        """Create a TriageQuestion instance from a dictionary."""
        question = cls(
            patient1=Patient(description=data["patient1"]),
            patient2=Patient(description=data["patient2"]),
            question_id=data.get("question_id", str(uuid.uuid4())),
            context=data.get("context", "primary care triage"),
            expertise_required=data.get("expertise_required", []),
            metadata=data.get("metadata", {})
        )
        
        if "expert_answer" in data:
            question.expert_answer = data["expert_answer"]
            
        if "created_date" in data:
            question.created_date = datetime.fromisoformat(data["created_date"])
            
        return question


@dataclass
class TriageQuestionSet:
    """A collection of triage questions for evaluation."""
    questions: List[TriageQuestion] = field(default_factory=list)
    set_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    name: str = "Default Triage Question Set"
    description: str = ""
    created_date: datetime = field(default_factory=datetime.now)
    author: str = ""
    
    def add_question(self, question: TriageQuestion) -> None:
        """Add a question to the set."""
        self.questions.append(question)
    
    def load_from_csv(self, file_path: str) -> None:
        """Load questions from a CSV file similar to those in the paper."""
        import csv
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                reader = csv.reader(f)
                header = next(reader)  # Skip header
                
                for row in reader:
                    if len(row) >= 2:  # Ensure we have at least two columns
                        patient1_desc = row[0]
                        patient2_desc = row[1]
                        
                        # Create patient objects
                        patient1 = Patient(description=patient1_desc)
                        patient2 = Patient(description=patient2_desc)
                        
                        # Create question
                        question = TriageQuestion(
                            patient1=patient1,
                            patient2=patient2,
                            context="primary care triage"
                        )
                        
                        # Add expert answer if available (3rd column)
                        if len(row) >= 3 and row[2] in ['1', '2']:
                            question.expert_answer = int(row[2])
                        
                        self.questions.append(question)
                        
            logger.info(f"Loaded {len(self.questions)} triage questions from {file_path}")
        except Exception as e:
            logger.error(f"Error loading triage questions from {file_path}: {str(e)}")
            raise
    
    def evaluate_model(self, llm: Union[LLM, Any], verbose: bool = False) -> Dict[str, Any]:
        """
        Evaluate an LLM on this question set.
        
        Args:
            llm: An instance of the LLM class or any object with a chat method
            verbose: Whether to print progress information
            
        Returns:
            Dictionary with evaluation results
        """
        results = {
            "total_questions": len(self.questions),
            "correct": 0,
            "incorrect": 0,
            "agreement_rate": 0.0,
            "responses": []
        }
        
        if not self.questions:
            logger.warning("No questions in the set to evaluate")
            return results
        
        for i, question in enumerate(self.questions):
            if verbose:
                logger.info(f"Processing question {i+1}/{len(self.questions)}...")
                
            # Skip questions without expert answers
            if question.expert_answer is None:
                logger.debug(f"Skipping question {question.question_id} - no expert answer")
                continue
                
            # Get LLM response
            prompt = question.get_prompt()
            try:
                response = llm.chat(
                    system_prompt="You are an experienced clinician making triage decisions.",
                    user_prompt=prompt
                )
                
                # Extract the decision (1 or 2)
                llm_decision = None
                if hasattr(response, 'content'):
                    content = response.content
                else:
                    # Handle case where response might be a string or other format
                    content = str(response)
                    
                # Look for "1" or "2" at the beginning or after "Patient"
                match = re.search(r'^\s*([1-2])\b', content) or re.search(r'Patient\s+([1-2])', content)
                if match:
                    llm_decision = int(match.group(1))
                
                # Record results
                is_correct = llm_decision == question.expert_answer
                
                if is_correct:
                    results["correct"] += 1
                else:
                    results["incorrect"] += 1
                    
                results["responses"].append({
                    "question_id": question.question_id,
                    "expert_answer": question.expert_answer,
                    "llm_decision": llm_decision,
                    "is_correct": is_correct,
                    "full_response": content if hasattr(response, 'content') else str(response)
                })
                
            except Exception as e:
                logger.error(f"Error evaluating question {question.question_id}: {str(e)}")
                results["responses"].append({
                    "question_id": question.question_id,
                    "error": str(e),
                    "expert_answer": question.expert_answer
                })
        
        # Calculate agreement rate
        answered_questions = results["correct"] + results["incorrect"]
        if answered_questions > 0:
            results["agreement_rate"] = results["correct"] / answered_questions
            
        return results
    
    def to_csv(self, file_path: str) -> None:
        """Export the question set to CSV."""
        import csv
        
        try:
            with open(file_path, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow(["Patient1", "Patient2", "ExpertAnswer"])
                
                for question in self.questions:
                    row = [
                        question.patient1.description,
                        question.patient2.description,
                        question.expert_answer if question.expert_answer else ""
                    ]
                    writer.writerow(row)
                    
            logger.info(f"Exported {len(self.questions)} triage questions to {file_path}")
        except Exception as e:
            logger.error(f"Error exporting to {file_path}: {str(e)}")
            raise

    

@dataclass
class QuestionSet:
    """A collection of triage questions for evaluation."""
    questions: List[TriageQuestion] = field(default_factory=list)
    set_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    name: str = "Default Triage Question Set"
    description: str = ""
    created_date: datetime = field(default_factory=datetime.now)
    author: str = ""
    
    def add_question(self, question: TriageQuestion) -> None:
        """Add a question to the set."""
        self.questions.append(question)
    
    def load_from_csv(self, file_path: str) -> None:
        """Load questions from a CSV file similar to those in the paper."""
        import csv
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                reader = csv.reader(f)
                header = next(reader)  # Skip header
                
                for row in reader:
                    if len(row) >= 2:  # Ensure we have at least two columns
                        patient1_desc = row[0]
                        patient2_desc = row[1]
                        
                        # Create patient objects
                        patient1 = Patient(description=patient1_desc)
                        patient2 = Patient(description=patient2_desc)
                        
                        # Create question
                        question = TriageQuestion(
                            patient1=patient1,
                            patient2=patient2,
                            context="primary care triage"
                        )
                        
                        # Add expert answer if available (3rd column)
                        if len(row) >= 3 and row[2] in ['1', '2']:
                            question.expert_answer = int(row[2])
                        
                        self.questions.append(question)
                        
            logger.info(f"Loaded {len(self.questions)} triage questions from {file_path}")
        except Exception as e:
            logger.error(f"Error loading triage questions from {file_path}: {str(e)}")
            raise
    
    def evaluate_model(self, llm: Union[LLM, Any], verbose: bool = False) -> Dict[str, Any]:
        """
        Evaluate an LLM on this question set.
        
        Args:
            llm: An instance of the LLM class or any object with a chat method
            verbose: Whether to print progress information
            
        Returns:
            Dictionary with evaluation results
        """
        results = {
            "total_questions": len(self.questions),
            "correct": 0,
            "incorrect": 0,
            "agreement_rate": 0.0,
            "responses": []
        }
        
        if not self.questions:
            logger.warning("No questions in the set to evaluate")
            return results
        
        for i, question in enumerate(self.questions):
            if verbose:
                logger.info(f"Processing question {i+1}/{len(self.questions)}...")
                
            # Skip questions without expert answers
            if question.expert_answer is None:
                logger.debug(f"Skipping question {question.question_id} - no expert answer")
                continue
                
            # Get LLM response
            prompt = question.get_prompt()
            try:
                response = llm.chat(
                    system_prompt="You are an experienced clinician making triage decisions.",
                    user_prompt=prompt
                )
                
                # Extract the decision (1 or 2)
                llm_decision = None
                if hasattr(response, 'content'):
                    content = response.content
                else:
                    # Handle case where response might be a string or other format
                    content = str(response)
                    
                # Look for "1" or "2" at the beginning or after "Patient"
                match = re.search(r'^\s*([1-2])\b', content) or re.search(r'Patient\s+([1-2])', content)
                if match:
                    llm_decision = int(match.group(1))
                
                # Record results
                is_correct = llm_decision == question.expert_answer
                
                if is_correct:
                    results["correct"] += 1
                else:
                    results["incorrect"] += 1
                    
                results["responses"].append({
                    "question_id": question.question_id,
                    "expert_answer": question.expert_answer,
                    "llm_decision": llm_decision,
                    "is_correct": is_correct,
                    "full_response": content if hasattr(response, 'content') else str(response)
                })
                
            except Exception as e:
                logger.error(f"Error evaluating question {question.question_id}: {str(e)}")
                results["responses"].append({
                    "question_id": question.question_id,
                    "error": str(e),
                    "expert_answer": question.expert_answer
                })
        
        # Calculate agreement rate
        answered_questions = results["correct"] + results["incorrect"]
        if answered_questions > 0:
            results["agreement_rate"] = results["correct"] / answered_questions
            
        return results
    
    def to_csv(self, file_path: str) -> None:
        """Export the question set to CSV."""
        import csv
        
        try:
            with open(file_path, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow(["Patient1", "Patient2", "ExpertAnswer"])
                
                for question in self.questions:
                    row = [
                        question.patient1.description,
                        question.patient2.description,
                        question.expert_answer if question.expert_answer else ""
                    ]
                    writer.writerow(row)
                    
            logger.info(f"Exported {len(self.questions)} triage questions to {file_path}")
        except Exception as e:
            logger.error(f"Error exporting to {file_path}: {str(e)}")
            raise