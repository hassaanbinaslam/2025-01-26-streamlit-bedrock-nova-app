"""
Text to Image Generation module using Amazon Bedrock.
Provides a Streamlit interface for generating images from text descriptions.
"""

import streamlit as st
import json
import logging

from llm.utils import invoke_model, display_images
from config import Config

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Model Id
MODEL_ID = Config.BEDROCK_MODEL["id"]
MODEL_NAME = Config.BEDROCK_MODEL["name"]

# Page Configuration
PAGE_CONFIG = {"title": "Text-to-Image Generation", "icon": "🎨", "layout": "centered"}

# Available image sizes
IMAGE_SIZES = [
    "384x576",
    "384x640",
    "448x576",
    "512x512",
    "576x384",
    "768x768",
    "768x1152",
    "1024x1024",
]

# Content
HEADER_TEXT = f"""
Welcome to the **Text-to-Image Generation Tool**! 

This app allows you to turn your imagination into stunning visuals with just a few words. 
By harnessing the advanced capabilities of **{MODEL_NAME}**, 
you can generate high-quality images tailored to your prompts. 
"""

INSTRUCTIONS = """
### Instructions:
- Use the controls below to configure the text-to-image generation process.
- Select the number of images, size, and other parameters.
- Enter a positive prompt and optionally a negative prompt.
"""

CFG_SCALE_INFO = """
cfgScale: Specifies how strongly the generated image should adhere to the prompt. 
Use a lower value to introduce more randomness in the generation.
"""


def display_header():
    """Display the application header and description."""
    st.title(PAGE_CONFIG["title"])
    st.caption(
        "Transform Words into Art: Create Stunning Visuals with Text-to-Image AI"
    )
    st.markdown(HEADER_TEXT)
    st.markdown(INSTRUCTIONS)
    st.warning(
        "⚠️ Please be mindful of the parameters you set. Larger image sizes and more images may increase processing time."
    )
    st.info(
        f"""
        Bedrock model used: {MODEL_ID}
        {CFG_SCALE_INFO}
        """
    )


def get_user_inputs():
    """Gather inputs from the user."""
    try:

        # First row
        col1, col2 = st.columns(2)
        ## Number of images
        with col1:
            num_images = st.slider(
                "**Number of images to generate**",
                min_value=1,
                max_value=5,
                step=1,
                value=1,
            )
        ## Image size
        with col2:
            image_size = st.selectbox("**Image size**", IMAGE_SIZES)

        # Second row
        col3, col4 = st.columns(2)
        ## cfgScale
        with col3:
            cfg_scale = st.slider(
                "**cfgScale**", min_value=1.0, max_value=10.0, step=0.1, value=7.5
            )
        ## Seed
        with col4:
            seed = st.slider(
                "**Seed**", min_value=1, max_value=858993459, step=1, value=12
            )

        # Third row
        col5, col6 = st.columns(2)
        ## Prompt
        with col5:
            prompt = st.text_area("**Prompt**", value="A dog in a forest")
        ## Negative prompt
        with col6:
            negative_prompt = st.text_area("**Negative Prompt (Optional)**", value="")

        return {
            "num_images": num_images,
            "image_size": image_size,
            "cfg_scale": cfg_scale,
            "prompt": prompt,
            "negative_prompt": negative_prompt,
            "seed": seed,
        }
    except Exception as e:
        logger.error(f"Error getting user inputs: {e}")
        st.error("Error processing user inputs")
        return None


def prepare_request_body(inputs):
    """Prepare the JSON request body for the Bedrock API."""
    try:
        width, height = map(int, inputs["image_size"].split("x"))

        request_body = {
            "taskType": "TEXT_IMAGE",
            "textToImageParams": {
                "text": inputs["prompt"],
            },
            "imageGenerationConfig": {
                "numberOfImages": inputs["num_images"],
                "quality": "standard",
                "height": height,
                "width": width,
                "cfgScale": inputs["cfg_scale"],
                "seed": inputs["seed"],
            },
        }

        if inputs["negative_prompt"].strip():
            request_body["textToImageParams"]["negativeText"] = inputs[
                "negative_prompt"
            ].strip()

        return json.dumps(request_body)
    except Exception as e:
        logger.error(f"Error preparing request body: {e}")
        return None


def main():
    """Main application function."""
    try:
        display_header()

        inputs = get_user_inputs()

        # validate required input
        if not inputs["prompt"]:
            return

        if st.button("Generate Image", type="primary", use_container_width=True):
            body = prepare_request_body(inputs)
            if body:
                response_body = invoke_model(body)
                if response_body:
                    display_images(response_body)

        logger.info("text_to_image Page loaded successfully")
    except Exception as e:
        logger.error(f"Application error: {e}")
        st.error("An unexpected error occurred. Please try again later.")


# if __name__ == "__main__":
main()
