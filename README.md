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
