.PHONY: build

build:
	@echo "Compressing Lambda Function Python Code."
	mkdir -p build/layer/python && python -m pip install --platform manylinux2014_aarch64 -r requirements.txt -t build/layer/python && zip -r build/lambda-layer.zip build/layer

deploy:
	@echo "Deploying the cost-savings-automation lambda function"
	sam deploy --template-file ./template.yaml --stack-name SparkMentorBot --resolve-s3 --capabilities CAPABILITY_NAMED_IAM --region us-east-1

test:
	@echo "Running test for applycation"
	PYTHONPATH=. python tests/test_bedrock_langchain.py