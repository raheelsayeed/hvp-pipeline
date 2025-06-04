from typing import Any, Dict, Optional
from pydantic import BaseModel, Field, SerializeAsAny
from .participant import ParticipantType
from .primitive import IdentifiableUUID
from .survey import Survey
from .question import Question

class QuestionResponse(BaseModel):
    question_identifier: str
    answer_set_identifier: str
    prompt: Optional[str] = None 
    response: dict | None = Field(title="No Response")


class SurveyResponse(IdentifiableUUID): 
    survey: Survey
    responses: list[QuestionResponse]

    @property
    def participant_is_LLM(self) -> bool:
        return self.survey.participant.type == ParticipantType.LLM
    
    def get_response_for_question(self, question_id: str, answer_id: str) -> str:

        for response in self.responses:
            if response.question_identifier == question_id and response.answer_set_identifier == answer_id:
                return self.survey.participant.format_response(response=response.response)

        return "No response available"
    
    def to_markdown2(self) -> str:
        # Convert survey_response to Markdown for rendering in template
        md = f"##### Survey: {self.survey.identifier}\n\n"

        # Map questions by identifier for quick lookup
        question_map = {q.identifier: q for q in self.survey.questions}

        for r in self.responses:
            question = question_map.get(r.question_identifier)
            if not question:
                continue  # skip if question not found in survey

            # Find the corresponding answer set in the question
            answer_set = next(
                (a for a in question.answers if a.identifier == r.answer_set_identifier),
                None
            )

            md += f"## Question: {question.identifier}\n\n"
            md += f"**Instruction:** {question.instruct_human}\n\n"
            md += f"**Prompt:**\n\n{question.text}\n\n"

            if answer_set:
                md += f"**Answer Set ({answer_set.identifier}) Options:**\n"
                for opt in answer_set.options:
                    md += f"- {opt['text']} (`{opt['value']}`)\n"
            else:
                md += "*Answer set not found.*\n"

            md += f"\n**Response:** `{r.response}`\n\n---\n\n"

        return md
    

    def to_markdown(self, file_path: Optional[str] = None) -> str:
        markdown = self.survey.to_markdown_header()
        markdown += f"#### Completed: {self.date_created}\n\n"

        markdown += "## Questions\n\n"

        for i, response in enumerate(self.responses):
            print(f'Response<{i}>: {response}')
            markdown += f"### Question {i + 1}\n\n"
            markdown += f"_System prompt: {self.survey.participant.instruction}_\n\n"
            markdown += response.prompt + "\n\n"
            

            markdown += f"> **LLM Response:**\n"
            block_quote = '\n'.join(f"> {line}" for line in self.survey.participant.format_response(response=response.response).splitlines())
            markdown += f"{block_quote}\n\n"

        if file_path:
            with open(file_path, 'w') as file:
                file.write(markdown)

        return markdown




