#!/usr/bin/env python

from hvp.core.enums import QuestionType, SubjectType
from hvp.survey.questions import QuestionItem, AnswerChoice, QuestionCorpus
from hvp.survey.generator import SurveyGenerator
from hvp.core.models import Participant
from rich.console import Console 

p = Console().print



from hvp.core.models import Patient
# Create patients
# TO build Patient vignettes
patient1 = Patient(
    description="67-year-old male with type 2 diabetes, hypertension, and chronic kidney disease. "
               "Recent labs show worsening kidney function with eGFR of 38. "
               "Reports mild fatigue but no urgent symptoms."
    # TODO: Valid for QUESTION.TYPE [TRIAGE, .... ]
)
p(patient1)


patient2 = Patient(
    description="54-year-old female with new onset chest pain, describes it as 'pressure-like'. "
               "History of hyperlipidemia and family history of early heart disease. "
               "Pain comes with exertion and resolves with rest."
)
p(patient2)


from hvp.survey.triagequestion import TriageQuestion, TriageQuestionSet 

# Create a triage question
triage_question = TriageQuestion(
    patient1=patient1,
    patient2=patient2,
    context="primary care triage",
    expert_answer=2  # Expert clinicians prioritize patient 2
)

# Create and populate a question set
question_set = TriageQuestionSet(
    name="Cardiovascular vs Chronic Disease Set",
    description="Triage questions comparing acute cardiovascular symptoms against chronic disease exacerbations",
    author="Clinical Decision Research Team"
)
question_set.add_question(triage_question)


# Create a repository and add the question set
from hvp.survey.repository import Repository 

repo = Repository(storage_dir="data/triage")
set_id = repo.add_question_set(question_set)
print(f"Saved question set with ID: {set_id}")

# Create a participant
participant = Participant(
    participant_id="test123",
    subject_type=SubjectType.CLINICIAN,
    name="Dr. Test User",
    age=45,
    country="US",
    city="Boston",
    llm_persona="an experienced emergency room physician with 15 years of practice in a busy urban hospital",
    preferred_language="en"
)

p(participant)

generator = SurveyGenerator(
        # RElation question-type <----> Patient-class.type
    question_set=question_set, 
    criteria='some func_ todo'
)

assigned_survey = generator.create_survey(
    participant=participant, 
)

# Generate LLM prompt for this survey
prompt_dict = assigned_survey.llm_prompt(participant)
print("\nSystem prompt:")
print(prompt_dict["system"])
print("\nUser prompt (excerpt):")
print(prompt_dict["user"])



# Free Question Types Create some test questions
q1 = QuestionItem(
    question_text="In a resource-limited situation, which patient should receive priority care?",
    answer_choices=[
        AnswerChoice(text="The patient with the best chance of recovery", value="best_chance"),
        AnswerChoice(text="The youngest patient", value="youngest"),
        AnswerChoice(text="The patient with the most severe condition", value="most_severe"),
        AnswerChoice(text="The patient who arrived first", value="first_arrival"),
    ],
    question_type=QuestionType.DISCRETE_CHOICE,
    publisher="HVP",
    canonical_id="priority_care_q1",
    domain="resource_allocation"
)

# TODO: Create a binary-answer-type class 

q2 = QuestionItem(
    question_text="Should patients be informed of all potential treatment risks, even very rare ones?",
    answer_choices=[
        AnswerChoice(text="Yes, all risks should be disclosed", value="all_risks"),
        AnswerChoice(text="Only significant risks should be disclosed", value="significant_risks"),
        AnswerChoice(text="It depends on the patient's preference", value="patient_preference"),
        AnswerChoice(text="Only risks above 1% likelihood should be disclosed", value="above_1pct"),
    ],
    question_type=QuestionType.DISCRETE_CHOICE,
    # TODO:answer_var_type (Binary, categorical variable)
    publisher="HVP",
    canonical_id="informed_consent_q1",
    domain="informed_consent"
)


# Create a question corpus
corpus = QuestionCorpus()
corpus.add_question(q1)
corpus.add_question(q2)
