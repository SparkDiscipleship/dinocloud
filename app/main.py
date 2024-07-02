from bedrock_langchain import topic_transition, sentiment_analysis

elicitslot_response =  {
    'sessionState': {
        'dialogAction': {
            'slotToElicit': None,
            'type': 'ElicitSlot'
        },
        'intent': {
            'name': None,
            'slots': None
        }
    },
    'messages': [
        {
            'contentType': 'PlainText',
            'content': None
        }
    ]
}

def prepare_topic_tranistion(transcript: str, next_topic: str, intent, slots):

    message = topic_transition(
        input_transcript=transcript,
        next_topic=next_topic
    )

    response =  {
            'sessionState': {
                'dialogAction': {
                    'slotToElicit': 'MentalCapacity',
                    'type': 'ElicitSlot'
                },
                'intent': {
                    'name': intent,
                    'slots': slots
                }
            },
            'messages': [
                {
                    'contentType': 'PlainText',
                    'content': message.replace('"', '')
                }
            ]
        }

    return response

def handler(event, context):

    print(event)

    transcript = event['inputTranscript']
    slots = event['sessionState']['intent']['slots']
    intent = event['sessionState']['intent']['name']
    try:
        attempt = event['proposedNextState']['prompt']['attempt']
    except KeyError:
        attempt = 'Initial'
        pass

    print(f"The user message is: {transcript}")
    print(f"Current attempt: {attempt}")
    print(f"Current slots: {slots}")

    response = {
        'sessionstate': {
            'dialogAction': {
                'type': 'Delegate'
            },
            'intent': {
                'name': intent,
                'slots': slots
            }
        }
    }

    if event['invocationSource'] == 'DialogCodeHook':

        if not slots['MentalCapacity']:

            response = prepare_topic_tranistion(
                transcript="My name is " + transcript,
                next_topic="mental capacity and if Have he/she gone through a tragedy within the last 3 months?, such as a breakup, Loss of loved one, Traumatic injury/accident",
                slots=slots,
                intent=intent                
            )

            if attempt != 'Initial':
                answer = sentiment_analysis(
                    input_transcript=transcript,
                    topic="mental capacity",
                    redflags=[
                        "He/She is shocked about what He/She experienced",
                        "He/She is trying to cope with the event.",
                    ]                    
                )

                print("Answer provided by sentiment analysis: "+answer)

                if 'neutral' in answer.lower():
                    mental_capacity = 'neutral'
                else:
                    mental_capacity = 'bad'

                slots['MentalCapacity'] = {
                    'value': {
                        "originalValue": transcript,
                        "interpretedValue": mental_capacity,
                        "resolvedValues": [mental_capacity]
                    }
                }

                message = topic_transition(
                            input_transcript=transcript,
                            next_topic="emotional capcity and ask if He/She is helping to carry burdens or shoulder for people in His/Her life right now? If so, how do they make He/Shee feel?"
                        )

                response =  {
                    'sessionState': {
                        'dialogAction': {
                            'slotToElicit': 'EmotionalCapacity',
                            'type': 'ElicitSlot'
                        },
                        'intent': {
                            'name': intent,
                            'slots': slots
                        }
                    },
                    'messages': [
                        {
                            'contentType': 'PlainText',
                            'content': message.replace('"', '')
                        }
                    ]
                }
        
        else:
            response = {
                "sessionState": {
                    "dialogAction": {
                        "type": "Close"
                    },
                    "intent": {
                        "name": "MentorClassification",
                        "state": "Fulfilled"
                    }
                }
            }

    print(f"response: {response}")
    return response

