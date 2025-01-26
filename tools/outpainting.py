"""
Image Outpainting module using Amazon Bedrock.
Provides a Streamlit interface for extending images beyond their original boundaries.
"""

import streamlit as st
import base64
import json
import boto3
import io
from PIL import Image
import logging

from llm.utils import invoke_model, display_images
from config import Config

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Model configs
MODEL_ID = Config.BEDROCK_MODEL["id"]
MODEL_NAME = Config.BEDROCK_MODEL["name"]
# Available image sizes
IMAGE_SIZES = ["512x512", "1024x1024"]

# Page Configuration
PAGE_CONFIG = {"title": "Image Outpainting Tool", "icon": "🖌️", "layout": "centered"}

# Content
HEADER_TEXT = """
Welcome to the **Image Outpainting Tool**!

This tool allows you to expand your images beyond their original boundaries, creating seamless 
extensions that match the original content. Whether you want to extend landscapes, complete 
partial scenes, or create panoramic views, this tool helps you achieve natural-looking results.

**How It Works:**
1. **Upload Image**: Start by uploading your image.
2. **Select Mask Type**:
    -   *Prompt*: Use text to define the mask area to preserve.
    -   *Image*: Automatically mask the image area to keep unchanged.
3. **Set Expanded Size**: Choose the new image size: `512x512` or `1024x1024`.
4. **Adjust Position**: Use Horizontal and Vertical Position controls to place your image within the expanded canvas.
5. **Add a Prompt**: Describe how the extended areas should look.
6. **Generate Results**: Create and refine your expanded image.
"""

USAGE_TIPS = """
⚠️ **Tips for Best Results:**
- Use high-quality input images
- Ensure your mask accurately covers the areas to be extended
- Provide clear, descriptive prompts for the desired extension
"""


def display_header():
    """Display the application header and description."""
    st.title(PAGE_CONFIG["title"])
    st.caption("Transform Your Images: Expand Beyond Boundaries")
    st.markdown(HEADER_TEXT)
    st.markdown(USAGE_TIPS)
    st.info(f"Bedrock model used: {MODEL_ID}")


def get_user_inputs():
    """Collect user inputs for image processing."""
    try:
        col1, col2 = st.columns(2)
        with col1:
            input_image = st.file_uploader("**Upload Image**", type=["png", "jpg"])
        with col2:
            prompt = st.text_area(
                "**Prompt**", "forest setting in the background with animals and plants"
            )

        col3, col4 = st.columns(2)
        with col3:
            mask_type = st.selectbox("**Mask Type**", ["Prompt", "Image"])
        with col4:
            seed = st.slider(
                "**Seed**", min_value=1, max_value=858993459, step=1, value=12
            )
        return {
            "prompt": prompt,
            "input_image": input_image,
            "mask_type": mask_type,
            "seed": seed,
        }
    except Exception as e:
        logger.error(f"Error getting user inputs: {e}")
        st.error("Error processing user inputs")
        return None


def get_expanded_image_and_mask(input_image, image_size, horizontal_pos, vertical_pos):
    """Create expanded image and mask based on user positioning."""
    try:
        target_width, target_height = map(int, image_size.split("x"))
        original_width, original_height = input_image.size

        # Calculate new position
        position = (
            int((target_width - original_width) * horizontal_pos),
            int((target_height - original_height) * vertical_pos),
        )

        # Create expanded image
        input_image_expanded = Image.new(
            "RGB", (target_width, target_height), (235, 235, 235)
        )
        input_image_expanded.paste(input_image, position)

        # Create expanded image mask
        black_image = Image.new("RGB", input_image.size, (0, 0, 0))
        input_image_expanded_mask = Image.new(
            "RGB", (target_width, target_height), (255, 255, 255)
        )
        input_image_expanded_mask.paste(black_image, position)

        return input_image_expanded, input_image_expanded_mask
    except Exception as e:
        logger.error(f"Error creating expanded image: {e}")
        return None, None


def prepare_request_body(input_image, mask_image, prompt, mask_prompt, mask_type, seed):
    """Prepare the JSON request body for the Bedrock API."""
    try:
        base64_input_image = base64.b64encode(input_image.getvalue()).decode("utf8")
        base64_mask_image = base64.b64encode(mask_image.getvalue()).decode("utf8")

        request_body = {
            "taskType": "OUTPAINTING",
            "outPaintingParams": {
                "text": prompt,
                "image": base64_input_image,
                "outPaintingMode": "PRECISE",
            },
            "imageGenerationConfig": {
                "numberOfImages": 1,
                "seed": seed,
            },
        }

        if mask_type == "Image":
            request_body["outPaintingParams"]["maskImage"] = base64_mask_image
        elif mask_type == "Prompt":
            request_body["outPaintingParams"]["maskPrompt"] = mask_prompt

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
        if not inputs["prompt"] or not inputs["input_image"]:
            return

        # Show original image
        st.subheader("Uploaded Image")
        st.image(inputs["input_image"])
        input_image = Image.open(inputs["input_image"])

        # Get expanded image size and position
        col1, col2, col3 = st.columns(3)
        with col1:
            image_size = st.selectbox("**Exmpanded Image Size**", IMAGE_SIZES)
        with col2:
            horizontal_pos = st.slider(
                "Image Horizontal Position",
                min_value=0.0,
                max_value=1.0,
                value=0.5,
                step=0.01,
            )
        with col3:
            vertical_pos = st.slider(
                "Image Vertical Position",
                min_value=0.0,
                max_value=1.0,
                value=0.5,
                step=0.01,
            )

        # Get expanded image and mask
        expanded_image, expanded_image_mask = get_expanded_image_and_mask(
            input_image, image_size, horizontal_pos, vertical_pos
        )

        if not expanded_image or not expanded_image_mask:
            return

        # Display expanded image and mask/prompt input
        col1, col2 = st.columns(2)
        with col1:
            st.subheader("Expanded Image")
            st.image(expanded_image)
        with col2:
            if inputs["mask_type"] == "Image":
                st.subheader("Expanded Image Mask")
                st.image(expanded_image_mask)
            elif inputs["mask_type"] == "Prompt":
                st.subheader("Enter Mask Prompt")
                mask_prompt = st.text_area("**Mask Prompt**")

        if not st.button("Edit Image", type="primary", use_container_width=True):
            return

        # Validate mask prompt if needed
        if inputs["mask_type"] == "Prompt" and not mask_prompt:
            st.warning("Mask prompt is required")
            return

        # Convert images to bytes
        expanded_img_buffered = io.BytesIO()
        expanded_image.save(expanded_img_buffered, format="PNG")

        expanded_img_mask_buffered = io.BytesIO()
        expanded_image_mask.save(expanded_img_mask_buffered, format="PNG")

        # Process and display results
        body = prepare_request_body(
            expanded_img_buffered,
            expanded_img_mask_buffered,
            inputs["prompt"],
            mask_prompt if inputs["mask_type"] == "Prompt" else None,
            inputs["mask_type"],
            inputs["seed"],
        )

        if body:
            response_body = invoke_model(body)
            if response_body:
                display_images(response_body)

        logger.info("outpainting Page loaded successfully")
    except Exception as e:
        logger.error(f"Application error: {e}")
        st.error("An unexpected error occurred. Please try again later.")


# if __name__ == "__main__":
main()
