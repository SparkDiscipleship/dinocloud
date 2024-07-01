from app import bedrock_langchain

mental_capacity_input="Hi my name is Angel"
print("Testing topic transition for mental capacity...")
print("User input: "+mental_capacity_input)

mental_capacity_topic_transition_result = bedrock_langchain.topic_transition(
    input_transcript="Hi my name is Angel",
    next_topic="mental capacity and if Have he/she gone through a tragedy within the last 3 months?, such as a breakup, Loss of loved one, Traumatic injury/accident"
)

print("Result: "+ mental_capacity_topic_transition_result)
print("------------------------------------------------------------")


emotional_capacity_input = "No I have not experienced any tragedy recently, everything has been smooth"
print("Testing topic transition for emotional capacity...")
print("User input: "+emotional_capacity_input)

emotional_capacity_topic_transition_result = bedrock_langchain.topic_transition(
    input_transcript=emotional_capacity_input,
    next_topic="emotional capcity and ask if He/She is helping to carry burdens or shoulder for people in His/Her life right now? If so, how do they make He/Shee feel?"
)

print("Result: "+ emotional_capacity_topic_transition_result)
print("------------------------------------------------------------")

mental_capacity_sentiment_input = "Recently I broke my left arm and is been difficult my day by day"
print("Testing topic transition for emotional capacity...")
print("User input: "+mental_capacity_sentiment_input)

mental_capacity_sentiment_analysis = bedrock_langchain.sentiment_analysis(
    input_transcript=mental_capacity_sentiment_input,
    topic="mental capacity and if Have he/she gone through a tragedy within the last 3 months?, such as a breakup, Loss of loved one, Traumatic injury/accident",
    redflags=[
        "He/She is shocked about a breakup, Loss of loved one, Traumatic injury/accident",
        "He/She is trying to cope with a breakup, Loss of loved one, Traumatic injury/accident.",
    ]
)

print("Result: "+ mental_capacity_sentiment_analysis)
print("------------------------------------------------------------")

# emotional_capacity_sentiment_analysis = bedrock_langchain.sentiment_analysis(
#     input_transcript="I have always helped many to be able to deal with their worst situations and yes, sometimes I have felt very very tired, I have felt some kind of fatigue. I have always been a good support for others but sometimes my emotional feelints are quite affected by it.",
#     topic="emotional capacity",
#     redflags=[
#         "He/She is or seems to be burned out",
#         "He/She is or seems to be exhausted",
#         "He/She is or seems to be tired",
#         "He/She can't take this anymore"
#     ]     
# )
