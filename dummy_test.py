from bedrock import analyze_god_relationship, formulate_question

prompt1 = "Im really conviced that my faith to God is very solid, and I feel really confident that He is always helping me"
answer1 = analyze_god_relationship(prompt1)
print(answer1.strip())

prompt2 = "My relationship with God"
answer2 = formulate_question(prompt2)
print(answer2.strip())
