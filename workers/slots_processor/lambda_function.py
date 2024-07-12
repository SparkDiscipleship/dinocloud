from .bedrock_langchain import topic_transition, sentiment_analysis, topic_requestion
import json

topics = [
    {
        "category": "Mental Capacity",
        "description": "Have you gone through a tragedy within the last 3 months? Such as Breakup, Loss of loved one or Traumatic injury or accident",
        "redflags": ["Yes"],
        "slotName": "MentalCapacity",
    },
    {
        "category": "Emotional Capacity",
        "description": "Are there any burdens you are helping to carry or shoulder for people in your life right now? If so, how do they make you feel?",
        "redflags": ["burnt out", "exhausted", "I can't take this anymore", "It's putting me at my capacity"],
        "slotName": "EmotionalCapacity"
    },
    {
        "category": "Self Awareness",
        "description": "Based on your personality, what are some challenges you might bring into relationships and how would you navigate them?",
        "redflags": ["I don't know any challenges", "Although there are challenges I can bring to the relationship, I don't see the need to work on addressing them", "How I communicate to everyone is exactly the same"],
        "slotName": "SelfAwareness"
    },
    {
        "category": "Spiritual Maturity",
        "description": "Why do you want to disciple others?",
        "redflags": ["To prove something", "It's all about me", "I need this to feel better about myself or be fulfilled", "I'm here to take (versus give)"],
        "slotName": "SpiritualMaturity"
    },
    {
        "category": "In Healthy Relationships",
        "description": "Tell me about an incident within the last 3 months where you had conflict with someone. How did you handle that? How did you grow?",
        "redflags": ["I built up resentment", "I did more talking than listening", "I was critical of the other person instead of extending grace", "There was nothing I realized that I could have done to be more loving"],
        "slotName": "HealthyRelationships"
    },
    {
        "category": "Knowledge of God's Word",
        "description": "What are you studying in God's Word currently and how is it impacting your life?",
        "redflags": ["I'm not actively reading God's word", "There is nothing that I attempt to change in my life or mindset after reading God's word", "No mention of a bible passage", "No mention of an insight or revelation about themselves of God from reading God's word"],
        "slotName": "GodWordKnowledge"
    }
]

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
def get_next_topic(category):
    for i, topic in enumerate(topics):
        if topic["category"] == category:
            if i + 1 < len(topics):
                return topics[i + 1]
            else:
                return None
    return None

def get_current_topic(category):
    if category: 
        for topic in topics:
            if topic['category'] == category:
                return topic 
    return None

def prepare_topic_tranistion(transcript: str, category: str, next_topic: str, intent, slots):

    message = topic_transition(
        input_transcript=transcript,
        next_topic=f"{category} and if {next_topic}"
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
                },
                'sessionAttributes': {
                    'currentCategory': category
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

    transcript = event['inputTranscript']
    slots = event['sessionState']['intent']['slots']
    intent = event['sessionState']['intent']['name']
    currentCategory = event['sessionState']['sessionAttributes']['currentCategory'] if 'currentCategory' in event['sessionState']['sessionAttributes'] else None
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
        current_topic = get_current_topic(currentCategory)
        print(f"current_topic: {json.dumps(current_topic)}")
        
        if not current_topic:
            first_topic = topics[0]
            response = prepare_topic_tranistion(
                transcript="My name is " + transcript,
                category=first_topic["category"],
                next_topic=first_topic["description"],
                slots=slots,
                intent=intent                
            )
        else:
            next_topic_element = get_next_topic(currentCategory)

            answer = sentiment_analysis(
                    input_transcript=transcript,
                    topic=current_topic["category"],
                    redflags=current_topic["redflags"]                  
                )

            print("Answer provided by sentiment analysis: "+ answer)

            response_status = ''

            if 'neutral' in answer.lower():
                response_status = 'neutral'
                message = topic_requestion(transcript, topic=f"{current_topic['category']} and if {current_topic['description']}")

                response =  { 
                        'sessionState': {
                            'dialogAction': {
                                'slotToElicit': current_topic['slotName'],
                                'type': 'ElicitSlot'
                            },
                            'intent': {
                                'name': intent,
                                'slots': slots
                            },
                            'sessionAttributes': {
                                'currentCategory': current_topic['category'],
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
                if 'good' in answer.lower():
                    response_status = 'good'
                else:
                    response_status = 'bad'
                print(json.dumps(slots))
                slots[current_topic['slotName']] = {
                    'value': {
                        "originalValue": transcript,
                        "interpretedValue": response_status,
                        "resolvedValues": [response_status]
                    }
                }
                print(json.dumps(slots))    
                
                if next_topic_element:                
                    
                    message = topic_transition(
                                input_transcript=transcript,
                                next_topic=f"{next_topic_element['category']} and if {next_topic_element['description']}"
                            )

                    response =  { 
                        'sessionState': {
                            'dialogAction': {
                                'slotToElicit': next_topic_element['slotName'],
                                'type': 'ElicitSlot'
                            },
                            'intent': {
                                'name': intent,
                                'slots': slots
                            },
                            'sessionAttributes': {
                                'currentCategory': next_topic_element['category'],
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
                                "name": "VettingQuestions",
                                "state": "Fulfilled",
                                'slots': slots,
                            }
                        },
                        'messages': [
                            {
                                'contentType': 'PlainText',
                                'content': "¡Thanks you for your response!"
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
                    "name": "VettingQuestions",
                    "state": "Fulfilled"
                }
            }
        }

    print(f"response: {response}")
    return response

