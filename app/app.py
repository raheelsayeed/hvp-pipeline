from flask import Flask, render_template, redirect, session, request, url_for, g
from config import Config
import requests, os, json
import urllib.parse
from rich.console import Console
from utils.s3 import * 
from functions import *
import markdown
from flask import g, session
from utils.appparticipant import AppParticipant
import logging 
from rich.logging import RichHandler
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s [%(levelname)s] %(message)s',
     handlers=[RichHandler()]
)

log = logging.getLogger(__name__)

p = Console().print

app = Flask(__name__)
app.config.from_object(Config)
app.secret_key = Config.SECRET_KEY

DUE_SURVEY_ID = 'due_survey_id'
DUE_SURVEY_METADATA = 'due_survey_metadata'

# functions
@app.template_filter('markdown')
def render_markdown(text):
    return markdown.markdown(text)




@app.before_request
def load_survey():
    survey_id = session.get(DUE_SURVEY_ID)
    if survey_id:
        participant_id = session.get('user', {}).get('email', None)
        s3_file = f"surveys/{participant_id}/{survey_id}.json"
        if s3_file:
          survey_s3_str = download_survey(key=s3_file)
          survey = Survey(**json.loads(survey_s3_str))
          g.survey = survey
    else:
        g.survey = None




@app.route('/')
def index():
    
    if not 'user' in session:
      return render_template('login.html')
    
    def pkg(text, title, survey_list, due_item, show_resume):
      return {
          "user": session.get('user', None),
          "status": {"title": title, "text": text},
          "survey_list": survey_list,
          "due_survey_item": due_item,
          "show_resume": show_resume
      }
  

    participant = AppParticipant.load(session.get('user', {}).get('email'))

     # Check if profile is complete
    if not participant.has_demographics:
        session['participant_id'] = participant.identifier
        return redirect(url_for('complete_profile')) 
    
    # get surveys for participant
    survey_items = participant.get_due_surveys()
    due_survey_item = next(filter(lambda x: x.metadata['status'] == "pending", survey_items), None)
    survey_list = [s.metadata for s in survey_items]
    status_text = ""
    status_title = "" 
    
    if due_survey_item: 
        session[DUE_SURVEY_ID] = due_survey_item.survey.identifier
        status_title = "📝 Survey is due"
        status_text = "You have a survey due and takes only XXX mins to complete"
    else:
        session.pop(DUE_SURVEY_ID, None)
        status_title = "No survey currently assigned"
        status_text = "Currently, there are no surveys assigned for you. You will receive an email once it is ready."
    return render_template('main_page.html', **pkg(status_text, status_title, survey_list, due_survey_item, False))

          

@app.route('/complete-profile', methods=['GET', 'POST'])
def complete_profile():
    if request.method == 'POST':
        participant_id = session.get('participant_id')
        if not participant_id:
            return "Participant not found in session", 400

        participant = AppParticipant.load(participant_id)
        if not participant:
            return f"Participant {participant_id} not found in DB", 404

        # Collect data from form
        participant.age = request.form.get('age')
        participant.gender = request.form.get('gender')
        participant.race_ethnicity = request.form.get('race_ethnicity')
        # is_provider = request.form.get('is_provider') == 'yes'
        # participant.is_provider = is_provider
        # participant.provider_type = request.form.get('provider_type') if is_provider else None

        # Save updates
        participant.persist()

        return redirect(url_for('index'))

    return render_template("profile.html")


@app.route('/login')
def login():
    cognito_login_url = (
        f"https://{Config.COGNITO_DOMAIN}/login"
        f"?client_id={Config.CLIENT_ID}"
        f"&response_type=code"
        f"&scope=openid+email+profile"
        f"&redirect_uri={urllib.parse.quote(Config.REDIRECT_URI)}"
    )
    return redirect(cognito_login_url)


@app.route('/callback')
def callback():
    code = request.args.get("code")
    token_url = f"https://{app.config['COGNITO_DOMAIN']}/oauth2/token"
    data = {
        "grant_type": "authorization_code",
        "client_id": app.config["CLIENT_ID"],
        "code": code,
        "redirect_uri": app.config["REDIRECT_URI"]
    }

    auth = (app.config["CLIENT_ID"], app.config["CLIENT_SECRET"])
    token_response = requests.post(token_url, data=data, auth=auth)
    tokens = token_response.json()

    try: 
        claims = verify_token_response(tokens)
        session["user"] = {
            "email": claims["id_claims"].get("email"),
            "sub": claims["id_claims"].get("sub"),
            "name": claims["id_claims"].get("name"),
        }

            # create or fetch participant    
        user_data = session.get('user')
        log.debug(user_data)
        full_name = user_data.get("name", None)
        if full_name:
            parts = full_name.strip().split()
            first_name = parts[0]
            last_name = " ".join(parts[1:]) if len(parts) > 1 else ""
        else:
            first_name = user_data.get("given_name", "") or "Participant"
            last_name = user_data.get("family_name", "") or ""

        participant = AppParticipant(
            first_name=first_name,
            last_name=last_name,
            type=ParticipantType.HUMAN,
            email=user_data.get("email")
        )

        participant.persist()

        return redirect(url_for("index"))

    except Exception as e:
        return f"Login failed: {e}", 403


@app.route('/logout')
def logout():
    session.clear()
    logout_url = (
        f"https://{Config.COGNITO_DOMAIN}/logout"
        f"?client_id={Config.CLIENT_ID}"
        f"&logout_uri={Config.MAIN_URI}"
    )
    return redirect(logout_url)


    
def update_survey_status(status: str):
     if not 'user' in session and not DUE_SURVEY_ID in session:
         return 
         
     participant_id = session["user"]["email"]
     
     survey_id = session.get(DUE_SURVEY_ID)
     
     if status == "complete": 
        
        metadata = mark_survey_complete(participant_id, survey_id)
        
        session[DUE_SURVEY_METADATA] = metadata
        # check if more surveys, if not clear due_survey_id 
        session.pop(DUE_SURVEY_ID)

        return metadata

    
# ----- SURVEY --------- # 
# ----- ------ --------- # 
@app.route("/survey/start")
def survey_start():
    if 'user' not in session or DUE_SURVEY_ID not in session:
        return redirect(url_for('index'))
    
    return redirect("/survey/question/0")

@app.route("/survey/question/<int:question_number>", methods=["GET", "POST"])
def answer_question(question_number):
    if 'user' not in session or DUE_SURVEY_ID not in session:
        return redirect(url_for('index'))

    load_survey()
    if not g.survey:
       return redirect(url_for('index'))

    questions = g.survey.questions
    total_questions = len(questions)

    if request.method == "POST":
        
        selected = request.form.get("answer")
        p(f"Q{question_number}: {selected}")


        if question_number + 1 >= total_questions:

            # SURVEY ENDED
            update_survey_status("complete")
            content = {"user": session['user'], "status": {"title": "All set!", "text": "Thank you for participating in Human Values Project.\n\nWe will notify you if there are additional tasks."}}
            
            return render_template("main_page.html", **content)

        return redirect(url_for('answer_question', question_number=question_number + 1))

    current_question = questions[question_number]
    return render_template("question.html",
                           user=session['user'],
                           question=current_question,
                           question_number=question_number,
                           total_questions=total_questions)

@app.route("/survey/complete")
def survey_complete():
    return redirect(url_for('index')) 


if __name__ == '__main__':
    app.run(port=3000, debug=True)
