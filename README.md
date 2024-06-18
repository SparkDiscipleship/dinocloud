# spark-chatbot
chatbot system for spark

## Requirements

- [Install AWS SAM CLI](https://docs.aws.amazon.com/serverless-application-model/latest/developerguide/install-sam-cli.html)
- [Install AWS CLI](https://docs.aws.amazon.com/cli/latest/userguide/getting-started-install.html)
- [Python3.12](https://www.python.org/downloads/)
- [Python Virtual Environment](https://pypi.org/project/virtualenv/)

## Before Start

First you need to create a _.venv_ file.

```bash
pip install virtualenv # Make sure you have installed venv
cd ~/<project_folder> # Make sure you change to the root folder of the project
python3.12 -m venv .venv # Create a venv with python 3.12
source .venv/bin/activate # Change python interpreter
pip install -r requirements.txt # Install python libraries
```

> [!NOTE]
> Depending on your editor you may need to change your langauge interpreter to avoid any alerts about missing dependencies or libraries.

## Run the project

You need to create an AWS Role session, the current available account for this project is the _sandbox_ account:

```bash
aws configure sso --profile dinocloud-sandbox

# When prompted with the required values
# URL: https://d-90677ff854.awsapps.com/start/
# Region: us-east-1

export AWS_PROFILE=dinocloud-sandbox
```

Now you are ready to run the make file commands:

```bash
make build # This will generate the function.zip file with the python code

make deploy # This will create the cloudformation stack with the code
```