"""
Welcome page module for the Streamlit image processing application.

This module serves as the landing page for the application, providing an overview
of available features and basic usage instructions.
"""

import streamlit as st
import logging

from config import Config

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Page Configuration Constants
PAGE_CONFIG = {"title": "Image Processing Tools", "icon": "🖼️", "layout": "wide"}

# Model Id
MODEL_ID = Config.BEDROCK_MODEL["id"]
MODEL_NAME = Config.BEDROCK_MODEL["name"]

# Content Constants
AVAILABLE_TOOLS = """
- **Text to Image**: Convert text descriptions into images
- **Text to Image with Condition**: Generate images with specific conditions
- **Remove Image Background**: Automatically remove image backgrounds
- **Image Inpainting**: Fill in missing or masked parts of images
- **Image Outpainting**: Extend images beyond their original boundaries
"""

HOW_TO_USE = """
1. Select a tool from the navigation menu on the left
2. Follow the instructions specific to each tool
3. Upload images when required
4. Adjust parameters as needed
5. Download your processed results
"""

SUPPORTED_FORMATS = """
- Input formats: PNG, JPEG, JPG
- Output formats: PNG, JPEG
- Maximum file size: 20MB
"""

USAGE_TIPS = """
- For best results, use high-quality input images
- Ensure proper lighting in your images
- Be specific in your text descriptions
- Check image dimensions before processing
"""

FOOTER = """
<div style='text-align: center'>
    <p>Made with ❤️ using Streamlit</p>
</div>
"""


def display_header():
    """Display the main title and introduction."""
    st.title("🎨 Welcome to Image Processing Tools")
    st.markdown(
        f"""
        Welcome to a comprehensive image processing toolkit! This application provides
        various tools to manipulate and generate images using state-of-the-art **{MODEL_NAME}** model.
        """
    )


def display_main_content():
    """Display the main content sections in two columns."""
    try:
        # Create two columns for features overview
        col1, col2 = st.columns(2)

        # Left column - Available Tools
        with col1:
            st.header("📋 Available Tools")
            st.markdown(AVAILABLE_TOOLS)

        # Right column - How to Use
        with col2:
            st.header("🚀 How to Use")
            st.markdown(HOW_TO_USE)

    except Exception as e:
        logger.error(f"Error displaying main content: {e}")
        st.error("Error loading page content")


def display_additional_info():
    """Display additional information sections."""
    try:
        # Supported Formats Section
        st.header("📁 Supported Formats")
        st.markdown(SUPPORTED_FORMATS)

        # Tips Section
        st.header("💡 Tips")
        st.markdown(USAGE_TIPS)

    except Exception as e:
        logger.error(f"Error displaying additional info: {e}")
        st.error("Error loading additional information")


def display_footer():
    """Display the page footer."""
    try:
        st.markdown("---")
        footer_col1, footer_col2, footer_col3 = st.columns(3)
        with footer_col2:
            st.markdown(FOOTER, unsafe_allow_html=True)
    except Exception as e:
        logger.error(f"Error displaying footer: {e}")


def main():
    """Main function to run the welcome page."""
    try:
        display_header()
        display_main_content()
        display_additional_info()
        display_footer()
        logger.info("Welcome page loaded successfully")
    except Exception as e:
        logger.error(f"Error in welcome page: {e}")
        st.error("An error occurred while loading the page")


main()
