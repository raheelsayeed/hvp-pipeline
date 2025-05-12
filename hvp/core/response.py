from typing import Any, Dict, Optional
from pydantic import BaseModel, Field, SerializeAsAny
from .participant import ParticipantType
from .primitive import IdentifiableUUID
from .survey import Survey
from .question import Question

class QuestionResponse(IdentifiableUUID):
    question_identifier: str
    answer_set_identifier: str
    prompt: str
    response: dict | None = Field(title="No Response")




class SurveyResponse(IdentifiableUUID): 
    survey: Survey
    responses: list[QuestionResponse]

    @property
    def participant_is_LLM(self) -> bool:
        return self.survey.participant.type == ParticipantType.LLM
    

   ## TODO: LLM answer function should be derived from the LLM class

    def get_response_for_question(self, question_id: str, answer_id: str) -> str:

        for response in self.responses:
            if response.question_identifier == question_id and response.answer_set_identifier == answer_id:
                return self.survey.participant.format_response(response=response.response)
                # return response.content
        return "No response available"
    

    def to_markdown(self, file_path: Optional[str] = None) -> str:
        markdown = self.survey.to_markdown_header()
        markdown += f"#### Completed: {self.date_created}\n\n"

        markdown += "## Questions\n\n"

        for i, response in enumerate(self.responses):
            print(f'Response<{i}>: {response}')
            markdown += response.prompt + "\n\n"
            

            markdown += f"> **LLM Response:**\n"
            block_quote = '\n'.join(f"> {line}" for line in self.survey.participant.format_response(response=response.response).splitlines())
            markdown += f"{block_quote}\n\n"

        if file_path:
            with open(file_path, 'w') as file:
                file.write(markdown)

        return markdown




