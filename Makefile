.PHONY: build

build:
	@echo "Compressing Lambda Function Python Code."
	mkdir -p build && zip ./build/function.zip *.py -x '*test*.py'

deploy:
	@echo "Deploying the cost-savings-automation lambda function"
	sam deploy --template-file ./template.yaml --stack-name SparkMentorBot --resolve-s3 --capabilities CAPABILITY_NAMED_IAM

