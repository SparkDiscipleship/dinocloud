from langchain_core.messages import HumanMessage, SystemMessage
from langchain_aws import ChatBedrock
from typing import List

model_id = 'anthropic.claude-3-haiku-20240307-v1:0'

def topic_transition(input_transcript: str, next_topic: str, is_first: bool = False, name: str = ""):
    """A topic transition function that understands what the user said and returns
    a friendly statement with a question about the next topic.

    input_transcript: this is the input transcript from the Amazon Lex event.
    next_topic: this is the topic information about the next question to formulate.
    is_first: boolean indicating if this is the first question after getting the user's name.
    name: the user's name for personalization.
    """
    if is_first:
        initial_message = f"""Thanks {name}, nice to meet you. Let's begin by learning more about where you are on the discipleship journey. \
        I'm going to ask a series of questions to better understand your readiness to invest in the spiritual growth of others. Ready?"""
        prompt = f"""You are helpful chatbot. Start with a message with this style: '{initial_message}' \
                then formulate a gentle reply to what the user says and reformulate an enriched question about "{next_topic}" \
                that can be asked to the user. Do NOT start with a greeting."""
    else:
        prompt = f"""You are helpful chatbot, formulate a gentle reply to \
                what the user says and reformulate an enriched question about "{next_topic}" \
                that can be asked to the user. Do NOT start with a greeting"""
    
    return send_message(input_transcript, prompt)


def sentiment_analysis(input_transcript: str, topic:str, redflags: List[str]):
    """A custom sentiment analysis to detect potential redflags in a user response
    from a question about a topic.

    input_transcript: this is the input transcript from the Amazon Lex event.
    topic: this is the topic information about what was asked for the input.
    redflags: list of redflags to use for the analysis
    """
    redflags_parsed = "\n".join(redflags)

    prompt =f"""You are a sentiment analysis AI that detects pre-defined \
            sentiments considered redflags of what the user says. \
            The Redflags are: {redflags_parsed}. \
            Return "bad" if you found the redflags. \
            Return "neutral" if the user said nothing related to the topic "{topic}". \
            Return "good" if the user is positive or optimistic about the topic "{topic}". \
            You can only reply bad, neutral or good"""

    return send_message(input_transcript, prompt)

def topic_requestion(input_transcript: str, topic: str):
    """A function that ends the conversation, responding to the user's last message
    and providing a final closing statement.

    input_transcript: this is the input transcript from the Amazon Lex event.
    name: this is the name of the user to personalize the closing message.
    """
    prompt = f"""You are a helpful chatbot. Reformulate the user's question \
            related to the topic "{topic}". Do NOT start with a greeting. \
            Ensure the reformulated question is clear, friendly, and enriched with \
            relevant context."""

    return send_message(input_transcript, prompt)



def end_conversation(input_transcript: str, name: str):
    """A function that ends the conversation, responding to the user's last message
    and providing a final closing statement.

    input_transcript: this is the input transcript from the Amazon Lex event.
    name: this is the name of the user to personalize the closing message.
    """
    prompt = f"""You are a helpful chatbot. Respond to the user's last message \
            and provide a closing statement. Ensure the response is clear, friendly, \
            and enriched with relevant context. The closing message should be with the next style: \
            '{name}, thanks so much for taking the time to share more about yourself with me! \
            We'll pass along this information to your church leader and they should be in touch \
            with you about next steps. We're encouraged you are obedient to The Great Commission!'"""

    return send_message(input_transcript, prompt)


def start_conversation(transcript):
    """A function that starts the conversation with an initial greeting and introductory message."""

    initial_message = """Hi! My name is Spark. I am your discipleship co-pilot, helping you get the most out of discipleship relationships within your church. My purpose is to enhance your relationships, not replace them, so think of me as your assistant, making some of the burdensome tasks of discipleship easier. To get started, what is your name?"""

    prompt = f"""You are a helpful chatbot. Provide an initial greeting and introductory message. The message should be: '{initial_message}'"""

    return send_message(transcript, prompt)

def send_message(input_transcript: str, prompt: str):
    """A function that ends the conversation, responding to the user's last message
    and providing a final closing statement.

    input_transcript: this is the input transcript from the Amazon Lex event.
    name: this is the name of the user to personalize the closing message.
    """

    chat = ChatBedrock(
        model_id=model_id,
        model_kwargs={ 
            "max_tokens": 256,
            "temperature": 0.5,
            "top_k": 250,
            "stop_sequences": ["\n\nHuman"],
        })

    messages = [
        SystemMessage(
            content= prompt
        ),
        HumanMessage(
            content=input_transcript
        ),
    ]

    return chat.invoke(messages).content