import streamlit as st
import json
import boto3
import base64
import io
from PIL import Image
import logging

# Move the logging configuration here if it's shared
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

from config import Config

MODEL_ID = Config.BEDROCK_MODEL["id"]
BEDROCK_REGION = Config.BEDROCK_REGION


def invoke_model(body):
    """Generic function to invoke any Bedrock model."""
    try:
        boto3_bedrock = boto3.client("bedrock-runtime", region_name=BEDROCK_REGION)
        response = boto3_bedrock.invoke_model(
            body=body,
            modelId=MODEL_ID,
            accept="application/json",
            contentType="application/json",
        )
        return json.loads(response.get("body").read())
    except Exception as e:
        logger.error(f"Error invoking model: {e}")
        st.error(f"An error occurred while generating images: {e}")
        return None


def display_images(response_body):
    """Generic function to display base64 encoded images."""
    try:
        images_data = response_body.get("images", [])
        if not images_data:
            st.error("No images returned from the model. Please try again.")
            return

        st.subheader("Generated Images:")
        for img_data in images_data:
            img = Image.open(io.BytesIO(base64.b64decode(img_data)))
            st.image(img, use_container_width=True)
    except Exception as e:
        logger.error(f"Error displaying images: {e}")
        st.error("Error displaying generated images")
