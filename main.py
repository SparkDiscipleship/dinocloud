from bedrock import analyze_god_relationship, formulate_question

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

        if not slots['GodRelationship']:

            # If the GodRelationship Slot is not fullfiled then ask for it
            message = formulate_question("How is your relationship with God and how did you find yourself there?")            
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

                message = formulate_question("Do you feel ready to be a disciple-maker?")

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
                    },
                    'messages': [
                        {
                            'contentType': 'PlainText',
                            'content': message.replace('"', '')
                        }
                    ]
                }

        elif not slots['DiscipleshipAttitude']:

            # If the proposed next stage attempt is not the Initial then analyze the user input
            if attempt != 'Initial':
                # Check if user input shows a solid or need to improve about GodRelationship
                god_relationship = analyze_god_relationship(transcript)
                slots['DiscipleshipAttitude'] = {
                    'value': {
                        "originalValue": transcript,
                        "interpretedValue": god_relationship,
                        "resolvedValues": [god_relationship]
                    }
                }

                message = formulate_question("Tell me a time in your life where you experienced something really hard.")

                response = {
                    'sessionState': {
                        'dialogAction': {
                            'slotToElicit': 'GodInHardTime', # Move to the next Slot
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

        elif not slots['GodInHardTime']:

            # If the proposed next stage attempt is not the Initial then analyze the user input
            if attempt != 'Initial':
                # Check if user input shows a solid or need to improve about GodRelationship
                god_relationship = analyze_god_relationship(transcript)
                slots['GodInHardTime'] = {
                    'value': {
                        "originalValue": transcript,
                        "interpretedValue": god_relationship,
                        "resolvedValues": [god_relationship]
                    }
                }
                message = formulate_question("As you look back on this experience, do you see God's hand in it now?")    
                response = {
                    'sessionState': {
                        'dialogAction': {
                            'slotToElicit': 'GodPresence', # Move to the next Slot
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

        elif not slots['GodPresence']:
            # If the proposed next stage attempt is not the Initial then analyze the user input
            if attempt != 'Initial':
                # Check if user input shows a solid or need to improve about GodRelationship
                god_relationship = analyze_god_relationship(transcript)
                slots['GodPresence'] = {
                    'value': {
                        "originalValue": transcript,
                        "interpretedValue": god_relationship,
                        "resolvedValues": [god_relationship]
                    }
                }

                response = {
                    'sessionState': {
                        'dialogAction': {
                            'type': 'ConfirmIntent'
                        },
                        'intent': {
                            'name': intent,
                            'slots': slots
                        }
                    },
                    'messages': [
                        {
                            'contentType': 'PlainText',
                            'content': "Thanks for all your answers, is there any final argument do you want to mention?"
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
