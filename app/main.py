from bedrock import topic_transition, sentiment_analysis

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

    # Default response, let Lex take next action
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

            message = topic_transition(
                input_transcript="My name is " + transcript,
                next_topic="mental capacity and ask if He/She have gone through a tragedy or hardtime within the last 3 months?"
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
                elif 'good' in answer.lower():
                    mental_capacity = 'good'
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

        elif not slots['EmotionalCapacity'] and attempt != 'Initial':

            answer = sentiment_analysis(
                    input_transcript=transcript,
                    topic="emotional capacity",
                    redflags=[
                        "He/She is or seems to be burned out",
                        "He/She is or seems to be exhausted",
                        "He/She is or seems to be tired",
                        "He/She can't take this anymore"
                    ]             
                )

            print("Answer provided by sentiment analysis: "+answer)

            if 'neutral' in answer.lower():
                mental_capacity = 'neutral'
            elif 'good' in answer.lower():
                mental_capacity = 'good'
            else:
                mental_capacity = 'bad'

            slots['EmotionalCapacity'] = {
                'value': {
                    "originalValue": transcript,
                    "interpretedValue": mental_capacity,
                    "resolvedValues": [mental_capacity]
                }
            }

            message = topic_transition(
                input_transcript=transcript,
                next_topic="self-awareness and ask if He/She recognize His/Her flaws/tendencies/triggers and how that could impact someone's ability to trust me"
            )

            response =  {
                'sessionState': {
                    'dialogAction': {
                        'slotToElicit': 'SelfAwareness',
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

