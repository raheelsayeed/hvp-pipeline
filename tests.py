#!/usr/bin/env python
from rich.console import Console
from hvp.core import question, response
import json
from rich import print

# Load question data from a JSON file outside the package
def load_question_from_file(file_path):
    with open(file_path, 'r') as file:
        return json.load(file)

triage_questions = '/Users/raheel/dbmi/humanValuesProject/hvp-app/static/demo/triage_pilot_v2_ids.json'  
question_data = load_question_from_file(triage_questions)
triage_questions_v2 = [question.Question(**q) for q in question_data]
print(f'Number of questions loaded: {len(triage_questions_v2)}')

# response_files_path = 'human_responses/TRIAGE/'
# response_records = response.ResponseRecord.load_all_responses(response_files_path)
# p(f'Number of Responses: {len(response_records)}')
# p(response_records[0])

print('==== OpenAI-ChatGPT ====')

from hvp.llm.openai import GPT

gpt = GPT.v4o()
print(type(gpt))
print(gpt_participant)

from hvp.llm.evaluator import LLMEval 

gpt_triage = LLMEval(
    questions=triage_questions_v2,
    llm=gpt_participant
)



responses, errors = gpt_triage.run() 

p(responses, errors)

exit()



p("Create LLMSurveyProcessor")
p("Evaluate GPT-Survey")

from hvp.llm.evaluator import LLMSurveyProcessor 
try: 
    evaluator = LLMSurveyProcessor(survey=survey)
    evaluated_survey = evaluator.run()
    evaluated_survey.to_markdown("generated_data/evaluated_sample2.md")
    evaluated_survey_json = evaluated_survey.model_dump_json(indent=4)
    p(evaluated_survey_json)
    open("generated_data/evaluated_survey_response2.json", "w").write(evaluated_survey_json)
except Exception as e:
    p(f"Error: {e}")


p("=====================================")
p("=====================================")
p("Claud:")


from hvp.llm.claude import Claude
claud = Claude.v37()
claud_participant = LLMParticipant(
    first_name="Claude",
    last_name=claud.model_version,
    instruction="You are a helpful AI assistant for clinical decision making.",
    model=claud
)
p(claud_participant)
p("Assigning survey to Claude")
survey_claud = SurveyGenerator().create_and_assign(
    num_questions=5,
    question_set=QSet,
    participant=claud_participant,
    filter_func=lambda q, p: q.type in 
        ['TRIAGE']
)

evaluator = LLMSurveyProcessor(survey=survey_claud)
try: 
    evaluated_survey = evaluator.run()
    evaluated_survey.to_markdown("generated_data/claud_evaluated_sample.md")
    evaluated_survey_json = evaluated_survey.model_dump_json(indent=4)
    p(evaluated_survey_json)
    open("generated_data/claud_evaluated_survey_response.json", "w").write(evaluated_survey_json)
except Exception as e:
    p(f"Error: {e}")


