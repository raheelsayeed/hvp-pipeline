#!/usr/bin/env python

from rich.console import Console 

p = Console().print

# Load question data from a JSON file outside the package
def load_question_from_file(file_path):
    with open(file_path, 'r') as file:
        return json.load(file)



from hvp.core.participant import ParticipantType
from hvp.core.question import *



from hvp.core.answeroption import AnswerTypes 
boolean_type = AnswerTypes.BOOLEAN
print(boolean_type.identifier)



p("=====================================")

question_data = load_question_from_file('input_data/questions.json')
questions = [Question.from_json(q) for q in question_data]
p(f'Number of questions loaded: {len(questions)}')
p(f'{questions[0].display_item()}')


p("=====================================")
QSet = QuestionSet(
    title="Triage and Diagnositic Questions",
    questions=questions,
    version="2.1"
)
p(QSet.model_dump())
p("=====================================")

from hvp.core.participant import Participant 
participant_human = Participant(
    first_name="John",
    last_name="Doe",
    type=ParticipantType.HUMAN,
    age=30,
    email="john.doe@example.com"
)
p(participant_human)    
custom_filter = lambda q, p: "important" in q.tags and p.first_name.startswith("J")

p("=====================================")

from hvp.core.survey import * 
from hvp.generator.generator import SurveyGenerator

# Generate a survey with specific criteria
survey = SurveyGenerator().create_and_assign(
    num_questions=5,
    question_set=QSet,
    participant=participant_human,
    filter_func=lambda q, p: q.type in 
        [QuestionTypes.TRIAGE, QuestionTypes.DIAGNOSIS]
)




survey_md = survey.to_markdown("generated_data/sample_survey.md")


p("=====================================")


from hvp.llm.openai import GPT
from hvp.llm.llmparticipant import LLMParticipant

gpt = GPT.v4o()
p(type(gpt))
gpt_participant = LLMParticipant(
    first_name="ChatGPT",
    last_name=gpt.model_version,
    instruction="You are a helpful AI assistant for clinical decision making.",
    model=gpt
)
p(gpt_participant)
survey = SurveyGenerator().create_and_assign(
    num_questions=5,
    question_set=QSet,
    participant=gpt_participant,
    filter_func=lambda q, p: q.type in 
        [QuestionTypes.TRIAGE, QuestionTypes.DIAGNOSIS]
)

from hvp.llm.evaluator import LLMSurveyProcessor 

evaluator = LLMSurveyProcessor(survey=survey)
evaluated_survey = evaluator.run()

try: 
    evaluated_survey.to_markdown("generated_data/evaluated_sample2.md")
    evaluated_survey_json = evaluated_survey.model_dump_json(indent=4)
    p(evaluated_survey_json)
    open("generated_data/evaluated_survey_response2.json", "w").write(evaluated_survey_json)


except Exception as e:
    p(f"Error: {e}")