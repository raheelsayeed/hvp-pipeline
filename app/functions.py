import json
from hvp.core.participant import Participant, ParticipantType
from hvp.core.survey import Survey 
from config import Config


def get_participant(user) -> Participant:
    p = Participant(
         first_name="John", 
         last_name="Doe", 
         type=ParticipantType.HUMAN, 
         age=30,
         email="mockemail@mock.com")
    
    return p


### This is a placeholder for the actual implementation of the survey assignment logic.
### Participant is matched to a set of questions 
### A new survey is created and sent to the participant 

from utils.s3 import download_survey, upload_survey
def get_assigned_survey_for(participant: Participant):
    
    filename = participant.survey_filename
    downloaded = download_survey(filename)

    if downloaded:
        return downloaded 
    else:
        # TODO: CREATE SURVEY 
        from demo import Demo
        survey = Demo.AssignedSurvey()

        save_resp = upload_survey(data=survey.model_dump_json(), key=filename)
        print(f"Survey saved to S3: {save_resp}")
        return survey


        



import requests
from jose import jwt
from jose.exceptions import JWTError, JWTClaimsError


def verify_token_response(token_response: dict) -> dict:
    """
    Verifies the ID and Access tokens from a Cognito OAuth2 token response.

    Args:
        token_response (dict): Must include 'id_token' and 'access_token' keys.

    Returns:
        dict: Contains validated 'id_claims' and 'access_claims'.
    Raises:
        Exception if verification fails.
    """
    id_token = token_response.get("id_token")
    access_token = token_response.get("access_token")
    JWKS_URL = f"{Config.PUBLIC_KEY_URL}/.well-known/jwks.json"

    if not id_token or not access_token:
        raise ValueError("Both id_token and access_token are required in the response")

    # Step 1: Get public keys
    jwks = requests.get(JWKS_URL).json()["keys"]

    def get_key(token):
        headers = jwt.get_unverified_header(token)
        kid = headers["kid"]
        return next((k for k in jwks if k["kid"] == kid), None)

    def verify_token(token, key, token_type):
        options = {
            "verify_aud": True,
            "verify_iss": True,
            "verify_exp": True,
            "verify_at_hash": token_type == "id_token"
        }

        return jwt.decode(
            token,
            key,
            algorithms=["RS256"],
            audience=Config.CLIENT_ID,
            issuer=Config.PUBLIC_KEY_URL,
            access_token=access_token if token_type == "id_token" else None,
            options=options
        )

    try:
        id_key = get_key(id_token)
        if not id_key:
            raise Exception("No matching key for ID token")

        access_key = get_key(access_token)
        if not access_key:
            raise Exception("No matching key for Access token")

        id_claims = verify_token(id_token, id_key, token_type="id_token")
        access_claims = verify_token(access_token, access_key, token_type="access_token")

        return {
            "id_claims": id_claims,
            "access_claims": access_claims
        }

    except JWTClaimsError as ce:
        raise Exception(f"Token claim validation error: {ce}")
    except JWTError as e:
        raise Exception(f"Token verification failed: {e}")
    except Exception as ex:
        raise Exception(f"Unexpected error during token verification: {ex}")
    


import boto3, os

def send_welcome_email(recipient_email, link):
    session = boto3.Session(profile_name=os.environ.get("AWS_LOGIN_PROFILE_NAME"))
    ses = session.client("ses", region_name="us-east-2")
    
    response = ses.send_email(
        Source="raheel_sayeed@hms.harvard.edu",
        Destination={"ToAddresses": [recipient_email]},
        Message={
            "Subject": {"Data": "Welcome to the Human Values Project"},
            "Body": {
                "Text": {
                    "Data": (
                        "Thank you for signing up for the <a href=\"https://hvp.global\">Human Values Project</a>.\n\n"
                        f"You may now begin your assigned survey here: {link}\n\n"
                        "We appreciate your contribution."
                    )
                }
            }
        }
    )
    return response