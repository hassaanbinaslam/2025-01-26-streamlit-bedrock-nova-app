"""
Text to Image Generation with Conditioning module using Amazon Bedrock.
Provides a Streamlit interface for generating images with control over structure and composition.
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

# Model Id
MODEL_ID = Config.BEDROCK_MODEL["id"]
MODEL_NAME = Config.BEDROCK_MODEL["name"]

# Page Configuration
PAGE_CONFIG = {"title": "Image Conditioning Tool", "icon": "🖌️", "layout": "centered"}

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

# Control modes
CONTROL_MODES = ["CANNY_EDGE", "SEGMENTATION"]

# Content
HEADER_TEXT = """
Welcome to the **Image Conditioning Tool**!

Shape your creations with precision and intention by leveraging advanced image conditioning features. 
This app allows you to guide the generation process using a reference image, helping you achieve 
the exact look and feel you desire.

**Features:**
- **Canny Edge Detection**: Extract and use edge maps to provide foundational structure.
- **Segmentation Maps**: Define and control specific areas or objects for precise rendering.

Unleash your creativity and take full control of the image generation process!
"""

CFG_SCALE_INFO = """
cfgScale: Specifies how strongly the generated image should adhere to the prompt. 
Use a lower value to introduce more randomness in the generation.
"""

CONTROL_STRENGTH_INFO = """
Control Strength: Determines how closely the generated image adheres to the reference image.
Use a lower value to introduce more randomness in the generation.
"""

INPUT_IMAGE = """
Input Image: Each side must be between 320-4096 pixels, inclusive.
"""


def display_header():
    """Display the application header and description."""
    st.title(PAGE_CONFIG["title"])
    st.caption(
        "Guide Your Vision: Precision Image Creation with Canny Edge and Segmentation Maps"
    )
    st.markdown(HEADER_TEXT)
    st.warning(
        "⚠️ For optimal results, ensure that the reference image is clear and appropriately sized."
    )
    st.info(
        f"""
        Bedrock model used: {MODEL_ID}
        {INPUT_IMAGE}
        {CFG_SCALE_INFO}
        {CONTROL_STRENGTH_INFO}
        """
    )


def get_user_inputs():
    """Gather inputs from the user."""
    try:
        # Input image
        input_image = st.file_uploader("**Upload Image**", type=["png", "jpg"])

        # First Row
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
        ## Control mode
        with col4:
            control_mode = st.selectbox("**Control Mode**", CONTROL_MODES)

        # Third row
        col5, col6 = st.columns(2)
        ## Control strength
        with col5:
            control_strength = st.slider(
                "**Control Strength**",
                min_value=0.0,
                max_value=1.0,
                step=0.1,
                value=0.7,
            )
        ## Seed
        with col6:
            seed = st.slider(
                "**Seed**", min_value=1, max_value=858993459, step=1, value=12
            )

        # Fourth row
        col7, col8 = st.columns(2)
        ## Prompt
        with col7:
            prompt = st.text_area("**Prompt**", value="")
        ## Negative prompt
        with col8:
            negative_prompt = st.text_area("**Negative Prompt (Optional)**", value="")

        return {
            "input_image": input_image,
            "num_images": num_images,
            "image_size": image_size,
            "prompt": prompt,
            "negative_prompt": negative_prompt,
            "cfg_scale": cfg_scale,
            "control_mode": control_mode,
            "control_strength": control_strength,
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
        base64_input_image = base64.b64encode(inputs["input_image"].getvalue()).decode(
            "utf8"
        )

        request_body = {
            "taskType": "TEXT_IMAGE",
            "textToImageParams": {
                "text": inputs["prompt"],
                "conditionImage": base64_input_image,
                "controlMode": inputs["control_mode"],
                "controlStrength": inputs["control_strength"],
            },
            "imageGenerationConfig": {
                "numberOfImages": inputs["num_images"],
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

        # validate required inputs
        if not inputs["input_image"] or not inputs["prompt"]:
            return

        # Display uploaded image
        st.subheader("Uploaded Image")
        st.image(inputs["input_image"])

        if st.button("Generate Image", type="primary", use_container_width=True):
            body = prepare_request_body(inputs)
            if body:
                response_body = invoke_model(body)
                if response_body:
                    display_images(response_body)

        logger.info("text_to_image_condition Page loaded successfully")
    except Exception as e:
        logger.error(f"Application error: {e}")
        st.error("An unexpected error occurred. Please try again later.")


# if __name__ == "__main__":
main()
