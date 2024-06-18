import json
from bedrock import analyze_god_relationship, formulate_question

def handler(event, context):

    print(event)

    transcript = event['inputTranscript']
    slots = event['sessionState']['intent']['slots']
    intent = event['sessionState']['intent']['name']
    attempt = event['proposedNextState']['prompt']['attempt']

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

        if not slots['GodRelationship']:

            # If the GodRelationship Slot is not fullfiled then ask for it
            message = formulate_question("My relationship with God")            
            response = {
                'sessionState': {
                    'dialogAction': {
                        'slotToElicit': 'GodRelationship',
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

            # If the proposed next stage attempt is not the Initial then analyze the user input
            if attempt != 'Initial':
                # Check if user input shows a solid or need to improve about GodRelationship
                god_relationship = analyze_god_relationship(transcript)
                slots['GodRelationship'] = {
                    'value': {
                        "originalValue": transcript,
                        "interpretedValue": god_relationship,
                        "resolvedValues": [god_relationship]
                    }
                }

                response = {
                    'sessionState': {
                        'dialogAction': {
                            'slotToElicit': 'DiscipleshipAttitude', # Move to the next Slot
                            'type': 'ElicitSlot'
                        },
                        'intent': {
                            'name': intent,
                            'slots': slots
                        }
                    }
                }

    print(f"response: {response}")
    return response
