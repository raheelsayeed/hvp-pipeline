### TODOs:

1. List of all participant characteristics to collect. 
2. List of all question-item characteristics. 
3. Question(s) assignment algorithm: Filter and assign questions based on question metadata and participant characteristics:
    - Precise precise characteristics
    - Version checks
    - Validation checks


### Sequence flow 

note over User[WebApp]: 1. Enroll via Website: OAuth2/iCloud/Google/X\nComplete form: TODO-1**: [characteristics]

User[WebApp]->Server-Layer: OAuth Credentials

Server-Layer->db-Participant: Create/Persist: Participant-DB

Server-Layer<--db-Participant: id: Participant_1

Server-Layer->db-Questions: Filter Questions for Participant-1

note over Server-Layer,db-Questions: **TODO-2**: Question-Participant match function

db-Questions-->Server-Layer: n Question Items

note over Server-Layer: Assign Participant & Create Survey

Server-Layer->Bucket: Persist survey Survey-Participant-1.json

Server-Layer-->User[WebApp]: "Ready to begin"\nEmail survey-web-app link

note over User[WebApp]: 2. Begin Survey-Session (stateless) [webApp]

User[WebApp]->Bucket: Persist SurveyResponse-Participant-1.json


## Server components

1. Database for participant data 
2. ?? Database for questions ?? Necessary only if we anticipate a huge number 
3. Server-layer (Python)
4. Authentication server ()



### Todo 

- [ ] From-email address for email notifications
- [x] Website domain address 
- [x] Main/Index page needed or not (After login, jump straight to the first question)
- [x] Previous browsing
- [x] Previous question editing
- [x] BUG: user_name on Apple sign-in 
- [x] Profile Form selections should be populated from ENUMs
- [ ] App-Participant attributes in HVP and then App 
- [x] Replace Question -> Scenario
- [x] Replace AnswerSet -> Decision

