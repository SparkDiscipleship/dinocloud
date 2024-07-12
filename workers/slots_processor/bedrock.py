import boto3
import json
from typing import List

client = boto3.client('bedrock-runtime')
model_id = 'anthropic.claude-v2:1'

def topic_transition(input_transcript: str, next_topic: str):

    prompt = f"""Based on a user conversation. \
        Reply gently to what the user said and reformulate a question about "{next_topic}" that I can use to continue with the \
        conversation. Do NOT include more than 30 words. \
              
        User said: {input_transcript}"""


    body = json.dumps({
            "prompt": f"\n\nHuman: {prompt}\n\nAssistant:",
            "max_tokens_to_sample": 300,
            "temperature": 0.1,
            "top_p": 0.9,
        })

    output = client.invoke_model(
        body = body,
        modelId = model_id
    )

    response_body = json.loads(output.get('body').read())
    answer = response_body.get('completion')

    return answer.strip()


def sentiment_analysis(input_transcript: str, topic: str, redflags: List[str]):

    formated_redflags = ', '.join(redflags)

    # prompt = f"""Consider the sentiment is bad if you identify redflags such as {formated_redflags}.

    # Analyze the following text and reply me if the sentiment is good, bad or neutral about {topic}, just reply me the result:
    
    # {input_transcript}

    # Result:"""

    prompt = f"""You are a bot that detects a set of pre-defined sentiments
    of a human text, your response as bot can be "true" if the pre-defined 
    sentiments are found in the human text, "neutral" if the human text does 
    not talks about a topic

    Analyze the following text and reply me if the sentiment is good, bad or neutral about {topic}, just reply me the result:
    
    {input_transcript}

    Result:"""


    body = json.dumps({
            "inputText": prompt,
            "textGenerationConfig": {
                "maxTokenCount": 512,
                "temperature": 0.2,
                "topP": 0.2,
            }
        })

    output = client.invoke_model(
        body = body,
        modelId = model_id
    )

    response_body = json.loads(output.get('body').read())
    answer = response_body['results'][0]['outputText']

    return answer