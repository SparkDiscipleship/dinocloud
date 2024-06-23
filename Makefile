.PHONY: build

build:
	@echo "Compressing Lambda Function Python Code."
	sam build --template-file ./template.yaml

deploy:
	@echo "Deploying the cost-savings-automation lambda function"
	sam deploy --template-file ./template.yaml --stack-name SparkMentorBot --resolve-s3 --capabilities CAPABILITY_NAMED_IAM --region us-east-1

test:
	@echo "Running test for applycation"
	PYTHONPATH=. python tests/test_bedrock_langchain.py