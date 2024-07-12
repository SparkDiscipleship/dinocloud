from langchain_core.messages import HumanMessage, SystemMessage
from langchain_aws import ChatBedrock
from typing import List


model_id = 'anthropic.claude-3-haiku-20240307-v1:0'

def topic_transition(input_transcript: str, next_topic: str):
    """A topic transition function that understand what the user said and returns
    a friendly statement with a question about the next topic.

    input_transcript: this is the input transcript from the Amazon Lex event.
    topic: this is the topic information about the next question to formulate.
    """

    chat = ChatBedrock(
        model_id=model_id,
        model_kwargs =  { 
            "max_tokens": 256,
            "temperature": 0.5,
            "top_k": 250,
            "stop_sequences": ["\n\nHuman"],
        })

    messages = [
        SystemMessage(
            content=f"""You are helpful chatbot, formulate a gently reply to \
            what the user says and reformulate a enriched question about "{next_topic}" \
            that can asked to the user. Do NOT start with a greeting"""
        ),
        HumanMessage(
            content=input_transcript
        ),
    ]

    return chat.invoke(messages).content

def sentiment_analysis(input_transcript: str, topic:str, redflags: List[str]):
    """A custom sentiment analysis to detect potential redflags in a user response
    from a question about a topic.

    input_transcript: this is the input transcript from the Amazon Lex event.
    topic: this is the topic information about what was asked for the input.
    redflags: list of redflags to use for the analysis
    """

    redflags_parsed = "\n".join(redflags)

    chat = ChatBedrock(
        model_id=model_id,
        model_kwargs =  { 
            "max_tokens": 512,
            "temperature": 0.0,
            "top_k": 250,
            "stop_sequences": ["\n\nHuman"],
        })

    messages = [
        SystemMessage(
            content=f"""You are a sentiment analysis AI that detects pre-defined \
            sentiments considered redflags of what the user says. \
            The Redflags are: {redflags_parsed}. \
            Return "bad" if you found the redflags. \
            Return "neutral" if the user said nothing related to the topic "{topic}". \
            Return "good" if the user is positive or optimistic about the topic "{topic}". \
            You can only reply bad, neutral or good"""
        ),
        HumanMessage(
            content=input_transcript
        )
    ]

    return chat.invoke(messages).content
