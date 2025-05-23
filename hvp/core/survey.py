from typing import List, Optional, Dict, Any

from .participant import Participant
from .question import Question
from .primitive import *




class Survey(IdentifiableUUID):
    title: str = "Human Values Project"
    participant: Participant
    questions: List[Question]
    footer: Optional[str] = None
    purpose: Optional[str] = None
    instructions: Optional[str] = None

    @property
    def s3_filename(self) -> str:
        return f"survey_{self.participant.identifier}.json"
    

    def to_markdown_header(self) -> str:
        header = f"# {self.title}\n\n"
        header += f"#### Participant: {self.participant.display_name} | {self.participant.type}\n\n"
        if self.instructions:
            header += f"#### Instructions: {self.instructions}\n\n"
        return header

    def to_markdown(self, file_path: Optional[str] = None) -> str:
        # Start with the survey title
        markdown = self.to_markdown_header()
        
        # Iterate over each question and append its markdown
        for index, question in enumerate(self.questions, start=1):
            
            markdown += f"## Question {index}\n\n"
            markdown += f"_System prompt: {self.participant.instruction}_\n\n"
            markdown += f"{question.to_markdown()}\n\n"

        # Optionally save to a file
        if file_path:
            with open(file_path, 'w') as file:
                file.write(markdown)
        
        return markdown
    
