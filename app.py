"""
Streamlit application for image manipulation and generation tools.

This module serves as the main entry point for a Streamlit application that provides
various image processing and generation capabilities using AWS services.

Features:
    - Text to Image Generation
    - Conditional Image Generation
    - Background Removal
    - Image Inpainting
    - Image Outpainting
"""

import logging
import os
import streamlit as st

from pathlib import Path
from streamlit_cognito_auth import CognitoAuthenticator
from config import Config


# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Constants
ICONS = {
    "HOME": ":material/home:",
    "TEXT": ":material/text_fields:",
    "REMOVE": ":material/remove:",
    "IMAGE": ":material/image:",
}

# Base directory for page modules
BASE_DIR = Path(".")

# login
if Config.LOGIN_REQUIRED:
    pool_id = os.environ["POOL_ID"]
    app_client_id = os.environ["APP_CLIENT_ID"]
    app_client_secret = os.environ["APP_CLIENT_SECRET"]

    authenticator = CognitoAuthenticator(
        pool_id=pool_id,
        app_client_id=app_client_id,
        app_client_secret=app_client_secret,
        use_cookies=False,
    )

    def logout():
        print("User logged out")
        authenticator.logout()


def initialize_pages():
    """Initialize all pages in the application."""
    try:
        # Initialize the home page
        pages = {
            "welcome": st.Page(
                str(BASE_DIR / "home" / "welcome.py"),
                title="Welcome",
                icon=ICONS["HOME"],
                default=True,
            )
        }

        # Initialize tool pages
        tool_pages = {
            "text_to_image": {
                "path": "tools/text_to_image.py",
                "title": "Text to Image",
                "icon": ICONS["TEXT"],
            },
            "text_to_image_condition": {
                "path": "tools/text_to_image_condition.py",
                "title": "Text to Image with Condition",
                "icon": ICONS["TEXT"],
            },
            "remove_background": {
                "path": "tools/remove_background.py",
                "title": "Remove Image Background",
                "icon": ICONS["REMOVE"],
            },
            "inpainting": {
                "path": "tools/inpainting.py",
                "title": "Image Inpainting",
                "icon": ICONS["IMAGE"],
            },
            "outpainting": {
                "path": "tools/outpainting.py",
                "title": "Image Outpainting",
                "icon": ICONS["IMAGE"],
            },
        }

        # Create pages from configuration
        for page_id, config in tool_pages.items():
            pages[page_id] = st.Page(
                str(BASE_DIR / config["path"]),
                title=config["title"],
                icon=config["icon"],
            )
            # logger.info(f"Initialized page: {config['title']}")

        return pages

    except Exception as e:
        logger.error(f"Error initializing pages: {e}")
        st.error("Failed to initialize pages. Please check the logs.")
        raise


def create_navigation_structure(pages):
    """Create the navigation structure for the application."""
    return {
        "Home": [pages["welcome"]],
        "Tools": [
            pages["text_to_image"],
            pages["text_to_image_condition"],
            pages["remove_background"],
            pages["inpainting"],
            pages["outpainting"],
        ],
    }


def main():
    """Main entry point for the application."""
    try:
        if Config.LOGIN_REQUIRED:
            # login
            is_logged_in = authenticator.login()
            if not is_logged_in:
                st.stop()

            # logout button
            with st.sidebar:
                st.text(f"Welcome,\n{authenticator.get_username()}")
                st.button("Logout", "logout_btn", on_click=logout)

        # Initialize pages
        pages = initialize_pages()

        # Create and run navigation
        nav_structure = create_navigation_structure(pages)
        navigation = st.navigation(nav_structure)
        navigation.run()

        # logger.info("Application started successfully")

    except Exception as e:
        logger.error(f"Application failed to start: {e}")
        st.error("An error occurred while starting the application. Please try again.")


if __name__ == "__main__":
    main()
