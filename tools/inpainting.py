"""
Image Inpainting module using Amazon Bedrock.
Provides a Streamlit interface for filling in masked areas of images with AI-generated content.
"""

import streamlit as st
import base64
import json
import io
from PIL import Image
from streamlit_drawable_canvas import st_canvas
import logging

from llm.utils import invoke_model, display_images
from config import Config

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Model configs
MODEL_ID = Config.BEDROCK_MODEL["id"]
MODEL_NAME = Config.BEDROCK_MODEL["name"]
MAX_IMAGE_SIZE = 1024

# Page Configuration
PAGE_CONFIG = {"title": "Image Inpainting Tool", "icon": "🖌️", "layout": "centered"}

# Content
HEADER_TEXT = """
Welcome to the **Image Inpainting Tool**!

This app allows you to enhance, restore, or creatively modify images by masking specific areas 
and providing detailed prompts to guide the process. Whether you're fixing imperfections or adding 
new elements, this tool empowers you with advanced inpainting features.

**How It Works:**
1. **Upload an Image**: Begin by uploading the image you wish to modify.
2. **Mask the Area**: Use the integrated canvas tool to draw masks over the regions you want to change.
3. **Provide a Prompt**: Describe the changes you'd like to see (e.g., "replace the masked area with a sunset sky").
4. **Generate Results**: Review and refine the generated outputs to achieve the desired effect.
"""

FEATURES_TEXT = """
**Features:**
- **Interactive Canvas Tool**: Intuitively mask areas directly on the image.
- **Prompt-Guided Edits**: Provide specific instructions to shape the outcome.
- **High-Quality Inpainting**: Achieve seamless integration of modifications.
"""


def display_header():
    """Display the application header and description."""
    st.title(PAGE_CONFIG["title"])
    st.caption("Transform Your Images: Precision Restoration and Creative Edits")
    st.markdown(HEADER_TEXT)
    st.markdown(FEATURES_TEXT)

    st.warning(
        "⚠️ For best results, use high-quality images and ensure your mask accurately covers the areas to be edited."
    )
    st.info(f"Bedrock model used: {MODEL_ID}")


def get_user_inputs():
    """Collect user inputs for canvas configuration."""
    try:
        col1, col2 = st.columns(2)
        with col1:
            input_image = st.file_uploader("**Upload Image**", type=["png", "jpg"])
        with col2:
            prompt = st.text_area(
                "**Prompt**", value="Replace the masked area with a honey bee"
            )
        col3, col4 = st.columns(2)
        with col3:
            stroke_width = st.slider("**Canvas Stroke Width**", 1, 25, 20)
        with col4:
            seed = st.slider(
                "**Seed**", min_value=1, max_value=858993459, step=1, value=12
            )

        return {
            "stroke_width": stroke_width,
            "prompt": prompt,
            "input_image": input_image,
            "seed": seed,
        }
    except Exception as e:
        logger.error(f"Error getting user inputs: {e}")
        st.error("Error processing user inputs")
        return None, None, None


def resize_image(image):
    """
    Resize the input image if it exceeds maximum dimensions.

    Args:
        image: PIL Image object
    Returns:
        PIL Image object: Resized or original image
    """
    try:
        width, height = image.size
        st.write(f"Uploaded image of size {width}x{height}")

        if width > MAX_IMAGE_SIZE or height > MAX_IMAGE_SIZE:
            if width > height:
                new_width = MAX_IMAGE_SIZE
                new_height = int((height / width) * MAX_IMAGE_SIZE)
            else:
                new_height = MAX_IMAGE_SIZE
                new_width = int((width / height) * MAX_IMAGE_SIZE)

            resized_image = image.resize(
                (new_width, new_height), Image.Resampling.LANCZOS
            )
            st.write(f"Resized image from {width}x{height} to {new_width}x{new_height}")
            return resized_image
        return image
    except Exception as e:
        logger.error(f"Error resizing image: {e}")
        st.error("Error processing image")
        return image


def display_canvas(stroke_width, image):
    """Display the canvas for drawing masks."""
    try:
        width, height = image.size
        return st_canvas(
            stroke_width=stroke_width,
            stroke_color="rgba(0, 0, 0, 1.0)",
            background_image=image,
            update_streamlit=True,
            height=height,
            width=width,
            drawing_mode="freedraw",
            key="main",
            display_toolbar=False,
        )
    except Exception as e:
        logger.error(f"Error displaying canvas: {e}")
        st.error("Error setting up drawing canvas")
        return None


def prepare_request_body(input_image, mask_image, prompt, seed):
    """Prepare the JSON request body for the Bedrock API."""
    try:
        base64_input_image = base64.b64encode(input_image.getvalue()).decode("utf8")
        base64_mask_image = base64.b64encode(mask_image.getvalue()).decode("utf8")

        return json.dumps(
            {
                "taskType": "INPAINTING",
                "inPaintingParams": {
                    "text": prompt,
                    "image": base64_input_image,
                    "maskImage": base64_mask_image,
                    # "returnMask": False,
                },
                "imageGenerationConfig": {
                    "numberOfImages": 1,
                    "seed": seed,
                },
            }
        )
    except Exception as e:
        logger.error(f"Error preparing request body: {e}")
        return None


def process_mask_image(canvas_result):
    """Process the mask image from canvas result."""
    try:
        mask_image = canvas_result.image_data
        pil_mask_image = Image.fromarray(mask_image.astype("uint8"), mode="RGBA")

        # Create white background
        rgb_mask = Image.new("RGB", pil_mask_image.size, (255, 255, 255))
        # Use alpha channel as mask
        rgb_mask.paste(pil_mask_image, mask=pil_mask_image.split()[3])

        # Binarize the image
        threshold = 128
        rgb_mask = rgb_mask.point(lambda p: 0 if p < threshold else 255)

        # Convert to bytes
        mask_buffered = io.BytesIO()
        rgb_mask.save(mask_buffered, format="PNG")
        return rgb_mask, mask_buffered
    except Exception as e:
        logger.error(f"Error processing mask image: {e}")
        return None, None


def main():
    """Main application function."""
    try:
        display_header()

        inputs = get_user_inputs()

        # validate required inputs
        if not inputs["input_image"] or not inputs["prompt"]:
            return

        # Process input image
        pil_image = Image.open(inputs["input_image"])
        resized_img = resize_image(pil_image)

        # Display canvas and get result
        st.write("Use the canvas below to draw the Image Mask")
        canvas_result = display_canvas(inputs["stroke_width"], resized_img)
        if not canvas_result:
            return

        if st.button("Edit Image", type="primary", use_container_width=True):
            # Display original and masked images
            col1, col2 = st.columns(2)
            with col1:
                st.subheader("Original Image")
                st.image(resized_img, output_format="PNG")
            with col2:
                st.subheader("Masked Image")
                st.image(canvas_result.image_data, output_format="PNG")

            # Process mask image
            rgb_mask, mask_buffered = process_mask_image(canvas_result)
            if not rgb_mask or not mask_buffered:
                return

            # Convert input image to bytes
            img_buffered = io.BytesIO()
            resized_img.save(img_buffered, format="PNG")

            # Prepare and send request
            body = prepare_request_body(
                img_buffered, mask_buffered, inputs["prompt"], inputs["seed"]
            )
            print("request prepared")

            if body:
                response_body = invoke_model(body)
                print("model invoked")
                if response_body:
                    display_images(response_body)

        logger.info("inpainting Page loaded successfully")
    except Exception as e:
        logger.error(f"Application error: {e}")
        st.error("An unexpected error occurred. Please try again later.")


# if __name__ == "__main__":
main()
