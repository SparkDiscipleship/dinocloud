from app import bedrock_langchain

test_result = bedrock_langchain.sentiment_analysis(
    input_transcript="I have always helped many to be able to deal with their worst situations and yes, sometimes I have felt very very tired, I have felt some kind of fatigue. I have always been a good support for others but sometimes my emotional feelints are quite affected by it.",
    topic="emotional capacity",
    redflags=[
            "He/She is or seems to be burned out",
            "He/She is or seems to be exhausted",
            "He/She can't take this anymore"
        ]
)

print(test_result)
