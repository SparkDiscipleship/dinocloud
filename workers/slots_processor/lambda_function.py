from .bedrock_langchain import topic_transition, sentiment_analysis, topic_requestion, end_conversation, start_conversation
import json
import boto3
import os
import time

dynamodb = boto3.resource('dynamodb')
vettings_questions_history_table = dynamodb.Table('VettingQuestionsHistory')
vettings_questions_status_table = dynamodb.Table('VettingQuestionsStatus')

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

initial_topics = {
    "MentalCapacity": None,
    "EmotionalCapacity": None,
    "SelfAwareness": None,
    "SpiritualMaturity": None,
    "HealthyRelationships": None,
    "GodWordKnowledge": None
}

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
        input_transcript= transcript,
        next_topic=f"{category} and if {next_topic}",
        is_first=True,
        name=transcript
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

def save_message_to_dynamodb(userId, senderType, message):
    item = {
        'userId': userId,
        'timestamp': int(time.time()),
        'senderType': senderType,
        'content': message
    }

    try:
        vettings_questions_history_table.put_item(Item=item)
    except Exception as err:
        print(f"There was an error")    
        print(json.dumps(err))


def save_status_to_dynamodb(userId, status, session):
    item = {
        'userId': userId,
        'status': status,
        'session': session,
    }

    try:
        vettings_questions_status_table.put_item(Item=item)
    except Exception as err:
        print(f"There was an error")    
        print(json.dumps(err))

def is_good_profile(topics_data):
    for topic in topics:
        if topics_data[topic["slotName"]] != 'good':
            return False
    return True

def send_initial_message(transcript, slots, intent):
    message = start_conversation(transcript)

    response = { 
        'sessionState': {
            'dialogAction': {
                'slotToElicit': "FirstName",
                'type': 'ElicitSlot'
            },
            'intent': {
                'name':intent,
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

def get_user_session(user_id):
    try:
        response = vettings_questions_status_table.get_item(Key={'userId': user_id})
        return response.get('Item')
    except Exception as e:
        print(f"Error fetching user session: {e}")
        return None
    
def handler(event, context):
    transcript = event['inputTranscript']
    
    userId = event['userId'] if 'userId' in event else os.environ.get('USER_ID', '1')
    status = 'inProgress'
    slots = event['sessionState']['intent']['slots']
    intent = event['sessionState']['intent']['name']
    currentCategory = event['sessionState']['sessionAttributes']['currentCategory'] if 'currentCategory' in event['sessionState']['sessionAttributes'] else None
    session_attributes = event['sessionState'].get('sessionAttributes', {})

    response = {
        'sessionState': {
            'dialogAction': {
                'type': 'Delegate'
            },
            'intent': {
                'name': intent,
                'slots': slots
            }
        }
    }


    firstMessage = False

    save_message_to_dynamodb(userId, 'user', event['inputTranscript'])

    try:
        attempt = event['proposedNextState']['prompt']['attempt']
    except KeyError:
        attempt = 'Initial'
        pass

    if 'invocationLabel' in event and event['invocationLabel'] == 'initialMessage': 
        user_session = get_user_session(userId)
        print(f"user_session: {json.dumps(user_session)}")
        print(f"user id: {userId}")
        
        if not user_session:
            print(f'No exists user session')
            response = send_initial_message(transcript, slots, intent)
            firstMessage = True
        else:
            event = user_session['session']
            print(f"Current event by load session: {json.dumps(event)}")

    if not firstMessage:
        slots = event['sessionState']['intent']['slots']
        intent = event['sessionState']['intent']['name']
        currentCategory = event['sessionState']['sessionAttributes']['currentCategory'] if 'sessionAttributes' in event['sessionState'] and 'currentCategory' in event['sessionState']['sessionAttributes'] else None
        session_attributes = event['sessionState'].get('sessionAttributes', {})

        print(f"The user message is: {transcript}")
        print(f"Current attempt: {attempt}")
        print(f"Current slots: {slots}")
        print(f"Current event: {json.dumps(event)}")


        response = {
            'sessionState': {
                'dialogAction': {
                    'type': 'Delegate'
                },
                'intent': {
                    'name': intent,
                    'slots': slots
                }
            }
        }

        print('has to ask for some topic')
        current_topic = get_current_topic(currentCategory)
        print(f"current_topic: {json.dumps(current_topic)}")
        
        if not current_topic:
            print('first topic')

            first_topic = topics[0]
            response = prepare_topic_tranistion(
                transcript=transcript,
                category=first_topic["category"],
                next_topic=first_topic["description"],
                slots=slots,
                intent=intent                
            )
            response['sessionState']['sessionAttributes'] =  {**initial_topics, 'currentCategory': first_topic['category'], 'currentRetries': str(0)} 



        else:
            print('other topic than first')
            next_topic_element = get_next_topic(currentCategory)
            print(f"next topic element: {json.dumps(next_topic_element)}")
            print(f"topic: {json.dumps(current_topic)} ")
            print(f"transcript: {transcript} ")

            answer = sentiment_analysis(
                    input_transcript=transcript,
                    topic=current_topic["category"],
                    redflags=current_topic["redflags"]                  
                )

            print(f"answer: {answer}")
            current_retries =  int(session_attributes['currentRetries'] if 'currentRetries' in session_attributes else '0')

            if 'neutral' in answer.lower() and current_retries < 2:
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
                                **session_attributes, 
                                'currentCategory': current_topic['category'],
                                'currentRetries': str(current_retries + 1)
                                },                        
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
                elif 'neutral' in answer.lower():
                    response_status = 'neutral'
                else:
                    response_status = 'bad'

                slots[current_topic['slotName']] = {
                    'value': {
                        "originalValue": transcript,
                        "interpretedValue": response_status,
                        "resolvedValues": [response_status]
                    }
                }

                session_attributes[current_topic['slotName']] = response_status
                
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
                            'sessionAttributes': {**session_attributes, 'currentCategory': next_topic_element['category'], 'currentRetries': str(0)},
                        },
                        'messages': [
                            {
                                'contentType': 'PlainText',
                                'content': message.replace('"', '')
                            }
                        ]
                    }
                else:
                    name = slots.get('FirstName', {}).get('value', {}).get('interpretedValue', 'User')
                    message = end_conversation(transcript, name)
                    response = {
                        "sessionState": {
                            "dialogAction": {
                                "type": "Close"
                            },
                            "intent": {
                                "name": "VettingQuestions",
                                "state": "Fulfilled",
                                'slots': slots,
                            },
                            'sessionAttributes': session_attributes,
                        },
                        'messages': [
                            {
                                'contentType': 'PlainText',
                                'content': message
                            }
                        ]
                    }
                    status = 'goodProfile' if is_good_profile(session_attributes) else 'rottenApple'
        save_message_to_dynamodb(userId, 'lex', response['messages'][0]['content'])

    print(f'finish with response: {json.dumps(response)}')

    save_status_to_dynamodb(userId, status, response)
    return response

