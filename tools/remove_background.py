"""
Background Removal module using Amazon Bedrock.
Provides a Streamlit interface for removing backgrounds from images.
"""

import streamlit as st
import json
import base64
import logging

from llm.utils import invoke_model, display_images
from config import Config

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Constants
MODEL_ID = Config.BEDROCK_MODEL["id"]
MODEL_NAME = Config.BEDROCK_MODEL["name"]

# Page Configuration
PAGE_CONFIG = {"title": "Remove Image Background", "icon": "🖼️", "layout": "centered"}

# Content
HEADER_TEXT = f"""
Welcome to the **Image Background Removal Tool**!

This app empowers your creative workflow by allowing you to effortlessly remove backgrounds from images in just one step. 
Whether you want to composite your subject onto a solid color background or seamlessly layer it over another scene, 
this tool provides a clean and accurate solution. Leveraging the power of **{MODEL_NAME}**, 
the app intelligently detects and segments multiple foreground objects, ensuring even complex scenes with overlapping 
elements are isolated with precision.

Unleash your creativity and transform your images with ease!
"""

INSTRUCTIONS = """
### Instructions:
- Upload an image (PNG or JPG) using the uploader below.
- The app uses Amazon Bedrock to remove the background.
- The processed images will be displayed below.
"""

WARNING_TEXT = """
Please be reasonable with the uploaded image file size. 
Large files may take longer to process and could potentially timeout.
"""


def display_header():
    """Display the application header and description."""
    st.title(PAGE_CONFIG["title"])
    st.caption(
        "Clean Cuts, Creative Freedom: Remove Backgrounds Instantly and Accurately"
    )
    st.markdown(HEADER_TEXT)
    st.markdown(INSTRUCTIONS)
    st.warning(WARNING_TEXT, icon="⚠️")
    st.info(
        f"""
        Bedrock model used: {MODEL_ID}

        Input Image: Each side must be between 320-4096 pixels, inclusive.
        """
    )


def get_user_inputs():
    """Gather inputs from the user."""
    try:
        # Input image
        input_image = st.file_uploader("**Upload Image**", type=["png", "jpg"])

        return {"input_image": input_image}
    except Exception as e:
        logger.error(f"Error getting user inputs: {e}")
        st.error("Error processing user inputs")
        return None


def prepare_request_body(inputs):
    """Prepare the JSON request body for the Bedrock API."""
    try:

        # Encode image to base64
        base64_input_image = base64.b64encode(inputs["input_image"].getvalue()).decode(
            "utf8"
        )

        request_body = {
            "taskType": "BACKGROUND_REMOVAL",
            "backgroundRemovalParams": {"image": base64_input_image},
        }

        return json.dumps(request_body)
    except Exception as e:
        logger.error(f"Error preparing request body: {e}")
        return None


def main():
    """Main application function."""
    try:
        display_header()

        inputs = get_user_inputs()

        # validate required inputs
        if not inputs["input_image"]:
            return

        # Display uploaded image
        st.subheader("Uploaded Image")
        st.image(inputs["input_image"])

        if st.button("Remove Background", type="primary", use_container_width=True):
            body = prepare_request_body(inputs)
            if body:
                response_body = invoke_model(body)
                if response_body:
                    display_images(response_body)

        logger.info("remove_background loaded successfully")
    except Exception as e:
        logger.error(f"Application error: {e}")
        st.error("An unexpected error occurred. Please try again later.")


# if __name__ == "__main__":
main()
