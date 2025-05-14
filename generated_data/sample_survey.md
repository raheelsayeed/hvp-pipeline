# Survey for John Doe

#### Participant: John Doe | ParticipantType.HUMAN

## Question 1

_System prompt: None_


_Category: Triage, tags: medical, triage_

Here is the patient you are currently scheduled to see tomorrow:

44F, no comorbidities, no medications, MediPort placement last year. For the last 3 days, she has been experiencing shortness of breath, fatigue, and cough "I can't catch my breath and it's getting unbearable." Vitals are 102 bpm, 128/84 blood pressure, 24 RR, 98.6 temp, pain score 7.

Would you rather see this patient instead:

63F, history of hyperlipidemia, no medications, no procedures. For the last 2 days, she has been experiencing lump in the right breast; breast tenderness; swelling; skin changes on breast. "I feel a bit of tenderness in my right breast." Vitals are 76 bpm, 118/74 blood pressure, 16 RR, 98.6 temp, pain score 2

Instruct Human: Please evaluate the patient scenarios carefully and select the option you would prefer as a clinician.

Instruct LLM: Please an answer from the choices and reply in JSON format as {"answer": "<your-answer-choice>"}


**Please select one answer:**
- Yes
- No


## Question 2

_System prompt: None_


_Category: Triage, tags: medical, triage_

Here is the patient you are currently scheduled to see tomorrow:

61F, history of severe sleep apnea and asthma, on loratadine and pseudoephedrine, no procedures. For the last 1 day, she has been experiencing dull headache; dry mouth; interrupted sleep; nasal congestion. "This dull headache won't go away and it's making daily activities tough." Vitals are 78 bpm, 125/80 blood pressure, 16 RR, 98.6 temp, pain score 5

Would you rather see this patient instead:

53M, history of hepatitis B, no medications, previous punch biopsies. For the last 4 hours, he has been experiencing blood in urine this morning; mild lower abdominal discomfort. "My stomach is killing me, and now there's blood when I pee!" Vitals are 88 bpm, 120/80 blood pressure, 16 RR, 98.6 temp, pain score 7

Instruct Human: Consider the clinical details and make a decision based on the patient's immediate needs.

Instruct LLM: Please an answer from the choices and reply in JSON format as {"answer": "<your-answer-choice>"}


**Please select one answer:**
- Yes
- No


## Question 3

_System prompt: None_


_Category: Diagnosis, tags: medical, diagnosis_

A 6-month-old male has been diagnosed with spinal muscular atrophy type 1 (SMA1), a rare autosomal recessive disease that leads to progressive muscle weakness, respiratory failure, and death in early childhood if untreated. Two clinical trials are available.

Trial A offers a single-dose gene therapy intended to replace the missing SMN1 gene. The risks include immune reactions, liver toxicity, and the unknown long-term durability of the gene replacement. The potential benefit is halting or reversing disease progression. Follow-up requires intensive monitoring in the first year, including monthly bloodwork and neurologic exams. Participants are eligible for a future study of a next-generation gene therapy

Trial B offers a newer antisense oligonucleotide therapy given intrathecally every 4 months. Risks include infection, headache, and injection-site complications. Benefits may include modest improvements in motor function. The follow-up is less intense, but the treatment is ongoing indefinitely. Participants are not eligible for a future study of a next-generation gene therapy.

Which clinical trial would you enroll this patient in?

Instruct Human: Evaluate the risks and benefits of each trial to make an informed decision.

Instruct LLM: Based on the trial details, recommend the most beneficial option for the patient. Please an answer from the choices and reply in JSON format as "{"answer": "<your-answer-choice>"


**Please select one answer:**
- Trial A
- Trial B


## Question 4

_System prompt: None_


_Category: Diagnosis, tags: medical, diagnosis_

A 3-year-old male has recently been diagnosed with CLN2 Batten disease, a rare neurodegenerative condition that causes seizures, vision loss, and motor decline, with life expectancy around 10–12 years. His symptoms are currently mild.

Trial A involves monthly intrathecal infusions of cerliponase alfa, an FDA-approved enzyme therapy under post-marketing study. Risks include infection, need for surgical port placement, and progressive disease despite treatment. Benefits include slowing cognitive and motor decline. Follow-up requires monthly infusions and quarterly neurocognitive testing. This trial allows concurrent access to supportive care protocols.

Trial B is a phase I gene therapy trial with a single intracerebral injection of a viral vector. Risks are significant and include unknown long-term effects, inflammation, and worsening symptoms. Potential benefit is sustained stabilization of disease. Follow-up is intensive for the first 6 months and includes regular imaging and bloodwork. Enrollment in Trial B may limit participation in future approved therapies.

Which clinical trial would you enroll this patient in?

Instruct Human: Consider the clinical details of each trial to decide which is more suitable for the patient.

Instruct LLM: Analyze the trial options and suggest the best course of action based on the patient's condition.


**Please select one answer:**
- Trial A
- Trial B


## Question 5

_System prompt: None_


_Category: Diagnosis, tags: medical, diagnosis_

Case 1: Lung Nodule Found During Hospitalization. A woman is recovering from a long hospital stay. A 2.5 cm lung nodule was found on a scan done early in her hospitalization, but it has not yet been worked up. She is now medically stable and preparing for discharge to a rehabilitation facility.

Instruct Human: Review each decision point carefully and select the most appropriate clinical action.

Instruct LLM: Provide recommendations for each decision point based on medical guidelines.


**Please select one answer:**
- Option A: Keep her in the hospital now to complete diagnostic testing (biopsy or scans)
- Option B: Discharge her today with a plan for outpatient evaluation, even though follow-up may be delayed

**Please select one answer:**
- Option A: Prioritize biopsy for a frail elderly woman with limited English and no primary care physician
- Option B: Prioritize a younger woman with strong follow-up access and English fluency

**Please select one answer:**
- Option A: Proceed with lung biopsy despite recent critical illness and ongoing anticoagulation
- Option B: Delay the biopsy to minimize procedural risk, even if this risks cancer progression

**Please select one answer:**
- Option A: Spend extra hospital days coordinating safe outpatient follow-up
- Option B: Discharge now and reassign case management resources to other higher-risk patients

**Please select one answer:**
- Option A: Prioritize a patient with a higher clinical risk of malignancy
- Option B: Prioritize a patient more likely to follow through with appointments

**Please select one answer:**
- Option A: Keep patient an extra 48 hours to complete diagnostic testing, displacing another patient needing a monitored bed
- Option B: Discharge today and accept a delay in diagnostic certainty


