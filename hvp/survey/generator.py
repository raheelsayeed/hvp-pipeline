from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, List, Optional, Any, Callable
import uuid, logging
import random

from hvp.core.enums import SubjectType, SurveyType
from hvp.survey.questions import QuestionCorpus, QuestionItem
from hvp.core.models import Participant
from hvp.llm.base import LLM, PromptTemplate
from hvp.survey.triagequestion import TriageQuestion, TriageQuestionSet

logger = logging.getLogger(__name__)


@dataclass
class Survey:
    """A clinical decision survey using triage questions directly."""
    questions: List[TriageQuestion]
    canonical_url: str
    survey_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    title: str = "Clinical Triage Decision Survey"
    description: str = "Compare patients and determine priority for clinical care."
    publisher: str = "HVP Clinical"
    version: str = "1.0"
    created_date: datetime = field(default_factory=datetime.now)
    subject_type: SubjectType = SubjectType.CLINICIAN
    estimated_completion_minutes: int = 15
    language_code: str = "en"
    participant_id: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_redcap(self) -> str:
        """Convert triage survey to REDCap format."""
        redcap_output = f"Form Name,{self.title}\n"
        redcap_output += f"Form Description,{self.description}\n\n"
        
        for i, question in enumerate(self.questions, 1):
            variable_name = f"triage_{i}"
            redcap_output += f"Field {i},{variable_name},Which patient should be seen first?\n"
            redcap_output += f"Note: Patient 1: {question.patient1.description}\n"
            redcap_output += f"Note: Patient 2: {question.patient2.description}\n"
            redcap_output += f"Option 1,1,Patient 1\n"
            redcap_output += f"Option 2,2,Patient 2\n\n"
            
        return redcap_output
    
    def to_text(self) -> str:
        """Convert triage survey to plain text format."""
        text_output = f"{self.title}\n{'=' * len(self.title)}\n\n"
        text_output += f"{self.description}\n\n"
        
        for i, question in enumerate(self.questions, 1):
            text_output += f"Question {i}: Which patient should be seen first?\n\n"
            text_output += f"Patient 1: {question.patient1.description}\n\n"
            text_output += f"Patient 2: {question.patient2.description}\n\n"
            text_output += "Options:\n"
            text_output += "1. Patient 1 should be seen first\n"
            text_output += "2. Patient 2 should be seen first\n\n"
            
        return text_output
    
    def to_pdf(self) -> bytes:
        """Convert triage survey to PDF format."""
        
        pass
    
    def to_json(self) -> Dict[str, Any]:
        """Convert triage survey to a web-friendly JSON format."""
        questions_json = []
    
    def llm_prompt(self, participant: Participant, llm: Optional[LLM] = None) -> Dict[str, str]:
        """Construct LLM prompt for this triage survey based on participant data."""
        system_prompt = f"""You are participating in a clinical triage decision study as {participant.llm_persona}.
This survey presents pairs of patients, and you need to decide which one should be seen first by a clinician.
Please respond thoughtfully as if you are the clinician described above, making real triage decisions."""
        
        user_prompt = f"Survey: {self.title}\n\n"
        
        for i, question in enumerate(self.questions, 1):
            user_prompt += f"Question {i}: Which patient should be seen first?\n\n"
            user_prompt += f"Patient 1: {question.patient1.description}\n\n"
            user_prompt += f"Patient 2: {question.patient2.description}\n\n"
            user_prompt += "Based on medical urgency and potential benefit from earlier care, which patient "
            user_prompt += "should be seen first? Respond with '1' for Patient 1 or '2' for Patient 2, "
            user_prompt += "followed by a brief explanation of your reasoning.\n\n"
        
        return {
            "system": system_prompt,
            "user": user_prompt
        }


class SurveyGenerator:
    """
    Generates clinical surveys directly from TriageQuestion objects
    without converting to standard QuestionItems.
    """
    
    def __init__(self, 
                 question_set: TriageQuestionSet,
                 default_questions_per_survey: int = 10,
                 include_attention_checks: bool = True,
                 criteria = None):
        """
        Initialize a clinical survey generator.
        
        Args:
            question_set: TriageQuestionSet to source questions from
            default_questions_per_survey: Default number of questions per survey
            include_attention_checks: Whether to include attention check questions
        """
        self.question_set = question_set
        self.default_questions_per_survey = default_questions_per_survey
        self.include_attention_checks = include_attention_checks
        logger.info(f"SurveyGenerator initialized with {len(question_set.questions)} triage questions")
    
    def create_survey(self, 
                     participant: Participant,
                     num_questions: Optional[int] = None,
                     selection_criteria: Optional[Dict[str, Any]] = None,
                     custom_title: Optional[str] = None,
                     custom_description: Optional[str] = None) -> Survey:
        """
        Create a clinical survey for a specific participant.
        
        Args:
            participant: The participant to create the survey for
            num_questions: Number of questions to include
            selection_criteria: Criteria for selecting questions
            custom_title: Custom survey title
            custom_description: Custom survey description
            
        Returns:
            A Survey object ready for delivery
        """
        num_questions = num_questions or self.default_questions_per_survey
        selection_criteria = selection_criteria or {}
        
        # Check participant type - triage surveys are primarily for clinicians
        if participant.subject_type != SubjectType.CLINICIAN:
            logger.warning(f"Creating clinical triage survey for non-clinician: {participant.subject_type.value}")
        
        # Sample questions
        questions = self._sample_questions(num_questions, **selection_criteria)
        
        # Add attention check if enabled
        if self.include_attention_checks and len(questions) >= 5:
            attention_check = self._create_attention_check()
            # Insert randomly in the middle third of the survey
            insert_position = random.randint(
                len(questions) // 3,
                (len(questions) * 2) // 3
            )
            questions.insert(insert_position, attention_check)
        
        # Create canonical URL
        canonical_url = f"hvp:clinical_survey:{uuid.uuid4()}"
        
        # Create title if not provided
        title = custom_title or f"Clinical Triage Survey"
        if participant.subject_type == SubjectType.CLINICIAN and participant.metadata.get("specialty"):
            title += f" for {participant.metadata.get('specialty')} Clinicians"
            
        description = custom_description or "This survey explores clinical triage decision making."
        
        # Create survey object
        survey = Survey(
            questions=questions,
            canonical_url=canonical_url,
            title=title,
            description=description,
            subject_type=participant.subject_type,
            estimated_completion_minutes=self._estimate_completion_time(questions),
            language_code=participant.preferred_language,
            # participant_id=participant.participant_id,
            metadata={
                "source_id": self.question_set.set_id,
                "source_name": self.question_set.name,
                "participant_demographics": participant.get_demographics_summary(),
                "attention_checks_included": self.include_attention_checks,
                "generation_date": datetime.now().isoformat()
            }
        )
        
        logger.info(f"Created clinical survey '{title}' with {len(questions)} questions for {participant.participant_id}")
        return survey
    
    def _sample_questions(self, n: int, **criteria) -> List[TriageQuestion]:
        """
        Sample questions based on criteria.
        
        Args:
            n: Number of questions to sample
            **criteria: Filter criteria
            
        Returns:
            List of sampled TriageQuestion objects
        """
        filtered = self.question_set.questions
        
        # Filter by expertise required if specified
        if "expertise_required" in criteria:
            expertise = criteria["expertise_required"]
            if isinstance(expertise, list):
                filtered = [
                    q for q in filtered 
                    if any(exp in q.expertise_required for exp in expertise)
                ]
            else:
                filtered = [
                    q for q in filtered 
                    if expertise in q.expertise_required
                ]
        
        # Filter by context if specified
        if "context" in criteria:
            context = criteria["context"]
            filtered = [q for q in filtered if q.context == context]
        
        # Filter by expert answer if specified (for balanced sampling)
        if "balanced" in criteria and criteria["balanced"] and any(q.expert_answer for q in filtered):
            # Get questions with expert answers
            patient1_questions = [q for q in filtered if q.expert_answer == 1]
            patient2_questions = [q for q in filtered if q.expert_answer == 2]
            
            # Calculate how many to take from each
            half_n = n // 2
            
            # Try to get balanced sample, fall back to what's available
            if len(patient1_questions) >= half_n and len(patient2_questions) >= half_n:
                sampled = random.sample(patient1_questions, half_n) + random.sample(patient2_questions, n - half_n)
                random.shuffle(sampled)
                return sampled
        
        # Standard sampling
        if len(filtered) <= n:
            return filtered
        
        return random.sample(filtered, n)
    
    def _create_attention_check(self) -> TriageQuestion:
        """
        Create an attention check question disguised as a triage question.
        These questions have an obvious correct answer to check if participants are paying attention.
        
        Returns:
            A TriageQuestion object that serves as an attention check
        """
        # Create obvious triage scenarios where one patient is clearly more urgent
        attention_checks = [
            {
                "patient1": "65-year-old male with mild seasonal allergies, no other health concerns.",
                "patient2": "72-year-old female with severe chest pain radiating to the left arm, sweating, and shortness of breath.",
                "correct": 2
            },
            {
                "patient1": "34-year-old male with acute appendicitis symptoms: severe right lower abdominal pain, fever, and vomiting.",
                "patient2": "40-year-old female requesting routine physical exam, no symptoms or concerns.",
                "correct": 1
            },
            {
                "patient1": "50-year-old male for scheduled follow-up on well-controlled hypertension.",
                "patient2": "4-year-old female with high fever (104°F), stiff neck, and lethargy.",
                "correct": 2
            }
        ]
        
        # Pick a random check
        check = random.choice(attention_checks)
        
        # Create the question
        question_id = f"attention_check_{uuid.uuid4().hex[:8]}"
        
        return TriageQuestion(
            patient1=Patient(description=check["patient1"]),
            patient2=Patient(description=check["patient2"]),
            question_id=question_id,
            expert_answer=check["correct"],
            metadata={"is_attention_check": True}
        )
    
    def _estimate_completion_time(self, questions: List[TriageQuestion]) -> int:
        """
        Estimate completion time based on triage questions.
        
        Args:
            questions: List of triage questions
            
        Returns:
            Estimated completion time in minutes
        """
        # Base time in minutes
        base_time = 2
        
        # Assume average time per triage question is 45 seconds
        # since they require reading two patient descriptions
        per_question_seconds = 45
        
        # Calculate total time
        question_time_minutes = (len(questions) * per_question_seconds) / 60
        
        return round(base_time + question_time_minutes)
    
    def create_batch_surveys(self, 
                           participants: List[Participant],
                           **survey_kwargs) -> Dict[str, Survey]:
        """
        Create surveys for multiple participants at once.
        
        Args:
            participants: List of participants to create surveys for
            **survey_kwargs: Additional arguments for create_survey
            
        Returns:
            Dictionary mapping participant IDs to their surveys
        """
        surveys = {}
        
        for participant in participants:
            survey = self.create_survey(participant, **survey_kwargs)
            surveys[participant.participant_id] = survey
            
        return surveys

# @dataclass
# class Survey:
#     questions: List[QuestionItem]
#     canonical_url: str
#     survey_id: str = field(default_factory=lambda: str(uuid.uuid4()))
#     title: str = "Human Values Project Survey"
#     description: str = ""
#     publisher: str = "HVP"
#     version: str = "1.0"
#     created_date: datetime = field(default_factory=datetime.now)
#     subject_type: SubjectType = SubjectType.CLINICIAN
#     survey_type: SurveyType = SurveyType.CHOICE
#     estimated_completion_minutes: int = 15
#     language_code: str = "en"
#     metadata: Dict[str, Any] = field(default_factory=dict)
    
#     def to_redcap(self) -> str:
#         """Convert survey to REDCap format."""
#         # Implementation for REDCap export
#         redcap_output = f"Form Name,{self.title}\n"
#         redcap_output += f"Form Description,{self.description}\n\n"
        
#         for i, question in enumerate(self.questions, 1):
#             redcap_output += f"Field {i},{question.canonical_id},{question.question_text}\n"
#             for j, choice in enumerate(question.answer_choices):
#                 redcap_output += f"Option {j},{choice.value},{choice.text}\n"
#             redcap_output += "\n"
            
#         return redcap_output
    
#     def to_text(self) -> str:
#         pass
    
#     def to_pdf(self) -> bytes:
#         pass
    
#     def llm_prompt(self, participant: Participant, llm: Optional[LLM] = None) -> Dict[str, str]:
#         """Construct LLM prompt for this survey based on participant data."""
#         system_prompt = f"""You are participating in a healthcare decision study as {participant.llm_persona}.
# This is a survey about clinical decision making in healthcare settings.
# Please respond thoughtfully as if you are the person described above."""
        
#         user_prompt = f"Survey: {self.title}\n\n"
        
#         for i, question in enumerate(self.questions, 1):
#             user_prompt += f"Question {i}: {question.question_text}\n"
#             if question.llm_context and question.llm_context.context_information:
#                 user_prompt += f"Context: {question.llm_context.context_information}\n"
            
#             # user_prompt += "Options:\n"
#             # for choice in question.answer_choices:
#             #     user_prompt += f"- {choice.text}\n"
            
#             # user_prompt += "\nPlease select one option and explain your reasoning briefly.\n\n"
        
#         return {
#             "system": system_prompt,
#             "user": user_prompt
#         }


# class SurveyGenerator:
#     def __init__(self, 
#                  question_corpus: QuestionCorpus,
#                  default_questions_per_survey: int = 10,
#                  default_survey_type: SurveyType = SurveyType.CHOICE,
#                  include_attention_checks: bool = True):
#         self.question_corpus = question_corpus
#         self.default_questions_per_survey = default_questions_per_survey
#         self.default_survey_type = default_survey_type
#         self.include_attention_checks = include_attention_checks
    
#     def create_survey(self, 
#                      participant: Participant,
#                      num_questions: Optional[int] = None,
#                      survey_type: Optional[SurveyType] = None,
#                      selection_criteria: Optional[Dict[str, Any]] = None,
#                      custom_title: Optional[str] = None) -> Survey:
#         """Create a survey for a specific participant based on criteria."""
#         num_questions = num_questions or self.default_questions_per_survey
#         survey_type = survey_type or self.default_survey_type
#         selection_criteria = selection_criteria or {}
        
#         # Apply participant-specific filtering logic
#         if participant.subject_type == SubjectType.CLINICIAN:
#             # For clinicians, potentially include more complex questions
#             selection_criteria["difficulty_min"] = selection_criteria.get("difficulty_min", 0.3)
        
#         # Sample questions based on criteria
#         questions = self.question_corpus.sample_questions(
#             n=num_questions,
#             **selection_criteria
#         )
        
#         # Add attention check if enabled
#         if self.include_attention_checks and len(questions) >= 5:
#             attention_check = self._create_attention_check()
#             # Insert randomly in the middle third of the survey
#             insert_position = random.randint(
#                 len(questions) // 3,
#                 (len(questions) * 2) // 3
#             )
#             questions.insert(insert_position, attention_check)
        
#         # Create canonical URL
#         canonical_url = f"hvp:survey:{uuid.uuid4()}"
        
#         # Create title if not provided
#         title = custom_title or f"HVP Survey for {participant.subject_type.value.capitalize()}"
        
#         # Create survey object
#         survey = Survey(
#             questions=questions,
#             canonical_url=canonical_url,
#             title=title,
#             subject_type=participant.subject_type,
#             survey_type=survey_type,
#             estimated_completion_minutes=self._estimate_completion_time(questions),
#             language_code=participant.preferred_language,
#             metadata={"participant_id": participant.participant_id}
#         )
        
#         return survey
    
#     def _create_attention_check(self) -> QuestionItem:
#         """Create an attention check question."""
#         from hvp.core.enums import QuestionType
        
#         # Simple attention check that asks the participant to select a specific option
#         attention_check = QuestionItem(
#             question_text="To show you're paying attention, please select 'Blue' as your answer.",
#             answer_choices=[
#                 AnswerChoice(text="Red", value="red"),
#                 AnswerChoice(text="Blue", value="blue"),
#                 AnswerChoice(text="Green", value="green"),
#                 AnswerChoice(text="Yellow", value="yellow"),
#             ],
#             question_type=QuestionType.DISCRETE_CHOICE,
#             publisher="HVP",
#             canonical_id="attention_check_1",
#             version="1.0",
#             difficulty=0.1,
#             metadata={"is_attention_check": True}
#         )
        
#         return attention_check
    
#     def _estimate_completion_time(self, questions: List[QuestionItem]) -> int:
#         """Estimate completion time based on questions."""
#         base_time = 2  # minutes
#         per_question_time = sum(q.expected_time_seconds for q in questions) / 60
        
#         return round(base_time + per_question_time)
    
#     def create_adaptive_survey(self, 
#                              participant: Participant,
#                              initial_questions: List[QuestionItem],
#                              adaptation_fn: Callable[[List[QuestionItem], List[Any]], List[QuestionItem]],
#                              max_questions: int = 20) -> Survey:
#         """Create an adaptive survey that changes questions based on previous answers."""
#         # This is a placeholder for adaptive survey functionality
#         # The adaptation_fn would determine next questions based on previous answers
        
#         # For now, just return a standard survey
#         return self.create_survey(participant, num_questions=len(initial_questions))