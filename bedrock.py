import boto3
import json

client = boto3.client('bedrock-runtime')
model_id = 'amazon.titan-text-express-v1'

def analyze_god_relationship(input: str):
    """
    Uses amazon bedrock to analyze the statement about My relationship with God
    returns:
    - solid
    - improve required
    """


    prompt = f"""
    {input}

    Analyze the above statement and reply me only "solid", for 
    the analysis consider the following:

    - solid: If the statement refers to catholic religios practices like 
    pray continually, always go to church, put God above all things, look 
    for the good for your neighbor, among other religious practices.
    Otherwise reply neutral
    """

    body = json.dumps({
            "inputText": prompt,
            "textGenerationConfig": {
                "maxTokenCount": 512,
                "temperature": 0.7,
            }
        })

    output = client.invoke_model(
        body = body,
        modelId = model_id
    )

    response_body = json.loads(output.get('body').read())
    print(response_body)

    answer = response_body['results'][0]['outputText']

    if 'solid' in answer:
        return 'solid'
    else:
        return 'improve required'


def formulate_question(topic: str):
    """
    Formulate a question about the {topic}
    return:
    - a formulated question ready to be used in the Lex prompt 
    """
    
    prompt = f"""
    write a question to ask a person about "{topic}", avoid greetings in your
    reply, for example:

    What is your relationship with God and how did you find yourself here?
    """

    body = json.dumps({
            "inputText": prompt,
            "textGenerationConfig": {
                "maxTokenCount": 512,
                "temperature": 0.9,

            }
        })

    output = client.invoke_model(
        body = body,
        modelId = model_id
    )

    response_body = json.loads(output.get('body').read())
    print(response_body)

    answer = response_body['results'][0]['outputText']

    return answer