HumanValuesProject
===================

Please note: Need AWS-Bedrock for Claude model run 

## secrets 

```
export AZURE_OPENAI_API_KEY=<api_key>
export AZURE_OPENAI_ENDPOINT=<end_point>
export AWS_LOGIN_PROFILE_NAME=<profile-name>

aws sso login --profile <profile-name>
```

### Setup 

```
$ python3 -m venv .venv
$ source .venv/bin/activate
$ pip install -r requirements.txt
$ chmod +x tests.py 
$ ./tests.py 
``` 

