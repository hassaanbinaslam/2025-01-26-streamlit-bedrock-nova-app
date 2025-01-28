#### 2025-01-26-streamlit-bedrock-nova-app
# Streamlit Image Processing App with Amazon Nova Canvas

This repository contains the code for a Streamlit web application that provides various image processing tools powered by Amazon's Nova Canvas foundation model. This app allows you to experiment with AI-powered image generation and editing, from text-to-image to more advanced features like inpainting and outpainting.

#### Referenced Blog Post: [Unleash Your Creativity: A Rapid Prototyping App with Amazon Nova Canvas](https://hassaanbinaslam.github.io/myblog/posts/2025-01-26-streamlit-bedrock-nova-app.html)

## Features

This application includes the following image processing tools:

*   **Text to Image:** Generate high-quality images from text prompts. You can configure the number of images, size, and other generation parameters.
*   **Text to Image with Condition:** Generate images guided by a reference image using Canny Edge Detection or Segmentation Maps.
*   **Background Removal:** Automatically remove backgrounds from images with precision.
*   **Image Inpainting:** Enhance, restore, or modify images by masking specific areas and providing detailed prompts.
*   **Image Outpainting:** Expand images beyond their original boundaries to create seamless extensions.

## Prerequisites

Before running the application, make sure you have the following:

*   **Access to Amazon Nova Canvas:** You need access to the Amazon Nova Canvas model. You can request access through the Amazon Bedrock console.
*   **AWS CLI Configured:** The AWS CLI must be configured with a user that has the necessary permissions to invoke Bedrock models.
*   **Python Installed:** Make sure you have 3.12+ installed on your local machine. This app is tested with `3.12.8` only.
*   **Streamlit Installed:** Install Streamlit by running `pip install streamlit`
*   **Docker Installed (for Deployment):** If you are going to deploy using docker container.

## Getting Started

1.  **Clone the repository:**

    ```bash
    git clone https://github.com/hassaanbinaslam/2025-01-26-streamlit-bedrock-nova-app.git
    cd 2025-01-26-streamlit-bedrock-nova-app
    ```
2.  **Install requirements:**

    ```bash
    pip install -r requirements.txt
    ```
3.  **Configure the application:**
    *   Modify the `config.py` file to set the Bedrock model ID, region, and user authentication settings.
        ```python
        class Config:
            # The name of the Bedrock model to use
            BEDROCK_MODEL = {
                "id": "amazon.nova-canvas-v1:0",
                "name": "Amazon Bedrock - Nova Canvas",
            }

            # If Bedrock is not activated in us-east-1 in your account, set this value accordingly
            BEDROCK_REGION = "us-east-1"

            # User Auth?
            LOGIN_REQUIRED = False
        ```
4.  **Run the app:**

    ```bash
    streamlit run app.py
    ```
5.  **Access the app:** Open your web browser and go to the URL provided in the terminal (typically `http://localhost:8501`).

## Deployment

For deployment, this application is designed to be easily deployed with Docker on AWS Lightsail. Steps are detailed in the [blog post](https://hassaanbinaslam.github.io/myblog/posts/2025-01-26-streamlit-bedrock-nova-app.html).

You can create a docker image using the provided `Dockerfile`, and upload it to Amazon ECR. From there, you can quickly deploy your application on AWS Lightsail by creating a container service, and granting access to the image from ECR. If you have enabled Cognito Login, then you will be required to create a cognito pool and user to authorize the user. You can also simply turn off the login and directly access the application.

## Code Structure

```{filename="Code Hierarchy"}
├── home
│   └── welcome.py
├── llm
│   ├── __init__.py
│   └── utils.py
├── tools
│   ├── inpainting.py
│   ├── outpainting.py
│   ├── remove_background.py
│   ├── text_to_image_condition.py
│   ├── text_to_image.py
│   └── __init__.py
├── .gitignore
├── app.py
├── config.py
├── Dockerfile
├── README.md
└── requirements.txt
```

*   `app.py`: The main entry point for the Streamlit application.
*   `config.py`: Configuration file for the application (model name, region, auth).
*   `requirements.txt`: Lists the required Python packages.
*   `home/`: Contains the streamlit app home page code.
*   `llm/`: Contains the utilities for interacting with the Amazon Bedrock models.
*   `tools/`: Contains the code for the different image processing tools.
  *   `text_to_image.py`: Code for text to image tool.
  *   `text_to_image_condition.py`: Code for text to image condition tool.
  *   `remove_background.py`: Code for image background removal tool.
  *   `inpainting.py`: Code for image inpainting tool.
  *   `outpainting.py`: Code for image outpainting tool.
*  `Dockerfile`: This file contains information that are used to build the Docker image.

## Contributing

Feel free to contribute to this project by creating pull requests or raising issues. I'm open to suggestions, improvements, and new features.