#!/usr/bin/env python


import random
import numpy as np
import pandas as pd

random.seed(42)
np.random.seed(42)

NUM_PATIENTS = 1800
HEALTHY_PERCENT = 0.20  # 20% healthy

# Generate normally distributed ages with a maximum age of 92
mean_age = 50
std_dev_age = 20
ages = np.clip(np.random.normal(loc=mean_age, scale=std_dev_age, size=NUM_PATIENTS), 0, 92).astype(int)

sexes = np.random.choice(['Male', 'Female'], size=NUM_PATIENTS)

# Dictionary of age-sex-appropriate diseases
diseases_by_age = {
    'child': ['asthma', 'type 1 diabetes', 'ADHD'],
    'young_adult': ['iron-deficiency anemia', 'asthma', 'type 1 diabetes'],
    'adult': ['type 2 diabetes', 'hypertension', 'hypothyroidism', 'obstructive sleep apnea'],
    'middle_aged': ['coronary artery disease', 'chronic kidney disease', 'rheumatoid arthritis'],
    'older': ['osteoporosis', 'Alzheimer\'s dementia', 'atrial fibrillation', 'benign prostatic hyperplasia', 'macular degeneration'],
}

# Conditions, co-morbidities, and related medications
disease_details = {
    'iron-deficiency anemia': {
        'co_conditions': ['menorrhagia'],
        'meds': ['ferrous sulfate']
    },
    'asthma': {
        'co_conditions': ['seasonal allergies'],
        'meds': ['albuterol']
    },
    'type 1 diabetes': {
        'co_conditions': ['hypoglycemia'],
        'meds': ['insulin']
    },
    'type 2 diabetes': {
        'co_conditions': ['diabetic retinopathy', 'hyperlipidemia'],
        'meds': ['metformin', 'insulin glargine']
    },
    'hypertension': {
        'co_conditions': ['left ventricular hypertrophy'],
        'meds': ['lisinopril']
    },
    'hypothyroidism': {
        'co_conditions': ['mild anemia'],
        'meds': ['levothyroxine']
    },
    'obstructive sleep apnea': {
        'co_conditions': ['BMI of 34'],
        'meds': ['CPAP therapy']
    },
    'coronary artery disease': {
        'co_conditions': ['hyperlipidemia', 'smoking history'],
        'meds': ['atorvastatin', 'aspirin']
    },
    'chronic kidney disease': {
        'co_conditions': ['hyperkalemia'],
        'meds': ['furosemide']
    },
    'rheumatoid arthritis': {
        'co_conditions': ['joint deformities'],
        'meds': ['methotrexate']
    },
    'osteoporosis': {
        'co_conditions': ['history of hip fracture'],
        'meds': ['alendronate']
    },
    'Alzheimer\'s dementia': {
        'co_conditions': ['urinary incontinence'],
        'meds': ['donepezil', 'memantine']
    },
    'atrial fibrillation': {
        'co_conditions': ['palpitations'],
        'meds': ['apixaban']
    },
    'benign prostatic hyperplasia': {
        'co_conditions': ['elevated post-void residual volume'],
        'meds': ['tamsulosin']
    },
    'macular degeneration': {
        'co_conditions': ['vision loss'],
        'meds': ['ranibizumab']
    },
    'ADHD': {
    'co_conditions': ['learning difficulties'],
    'meds': ['methylphenidate']
    }
}

def get_age_group(age):
    if age < 18:
        return 'child'
    elif age < 35:
        return 'young_adult'
    elif age < 55:
        return 'adult'
    elif age < 70:
        return 'middle_aged'
    else:
        return 'older'

def create_patient(index):
    age = ages[index]
    sex = sexes[index]
    is_healthy = (random.random() < HEALTHY_PERCENT)
    
    if is_healthy:
        return f"{sex}, {age} years old — Healthy."
    
    age_group = get_age_group(age)
    possible_dz = diseases_by_age[age_group]
    if sex == 'Male' and age_group == 'older':
        possible_dz += ['benign prostatic hyperplasia']
    elif sex == 'Female' and age_group == 'older':
        possible_dz += ['osteoporosis']
    
    disease = random.choice(possible_dz)
    co_conditions = disease_details[disease].get('co_conditions', [])
    meds = disease_details[disease].get('meds', [])
    
    comorbidities = random.sample(co_conditions, min(2, len(co_conditions)))
    medications = random.sample(meds, min(2, len(meds)))
    
    description = f"{sex}, {age} years old — Diagnosed with {disease}."
    if comorbidities:
        description += f" Also has " + " and ".join(comorbidities) + "."
    if medications:
        description += " Takes " + " and ".join(medications) + "."
    return description

# Generate all patients
descriptions = [create_patient(i) for i in range(NUM_PATIENTS)]

# Save to tab-delimited file
df = pd.DataFrame({'PatientDescription': descriptions})
df.to_csv("patient_descriptions.tsv", sep='\t', index=False)

# Optionally, display the first few records
print(df.head(10))