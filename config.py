class Config:
    # The name of the Bedrock model to use
    BEDROCK_MODEL = {
        "id": "amazon.nova-canvas-v1:0",
        "name": "Amazon Bedrock - Nova Canvas",
    }

    # If Bedrock is not activated in us-east-1 in your account, set this value
    # accordingly
    BEDROCK_REGION = "us-east-1"

    DEPLOYMENT_REGION = "us-east-1"

    STACK_NAME = "StreamlitApp"
