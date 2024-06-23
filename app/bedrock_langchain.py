from langchain_core.messages import HumanMessage, SystemMessage
from langchain_aws import ChatBedrock
from typing import List

chat = ChatBedrock(
    model_id='amazon.titan-text-express-v1',
    model_kwargs={'temperature': 0.1, 'topP': 0.1}
)


def topic_transition(input_transcript: str, next_topic: str):
    """A topic transition function that understand what the user said and returns
    a friendly statement with a question about the next topic.

    input_transcript: this is the input transcript from the Amazon Lex event.
    topic: this is the topic information about the next question to formulate.
    """

    messages = [
        SystemMessage(
            content="""You are a helpful assistant that helps with a survey, you respond 
            gently to what a user says and then you add a formulated friendly question 
            to ask them about the next topic"""
        ),
        HumanMessage(
            content=f"The user said '{input_transcript}' and the next topic is '{next_topic}'"
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

    messages = [
        HumanMessage(
            content=f"""
            The following is a text from a user when asked about 
            the topic "{topic}":

            "{input_transcript}"

            Respond if the sentiment of the text is one of the 
            following:

            {redflags_parsed}

            Otherwise, return only one of the following depending 
            on the description:

            good: if the text talks a lot of the topic {topic}.

            neutral: if the text is not enough good or talks about 
            the {topic}
            """
        )
    ]

    return chat.invoke(messages).content
