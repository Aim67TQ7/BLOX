# This script integrates evaluation data, image processing, and API communication.
# It sends data to an API, retrieves results, and supports adding a prompt for additional context.

import requests
import base64
import os
from io import BytesIO
from PIL import Image

# Maximum file size for validation (20MB)
MAX_FILE_SIZE = 20 * 1024 * 1024

# Converts an image file to a Base64 string
def convert_to_base64(file_path: str) -> str:
    try:
        with open(file_path, "rb") as file:
            return base64.b64encode(file.read()).decode("utf-8")
    except Exception as e:
        raise ValueError(f"Error converting file to Base64: {e}")

# Validates if an image file is within the allowed size limit
def validate_image_size(file_path: str) -> bool:
    try:
        return os.path.getsize(file_path) <= MAX_FILE_SIZE
    except Exception as e:
        raise ValueError(f"Error validating file size: {e}")

# Compresses an image and returns it as a Base64 string
def compress_image(base64_string: str) -> str:
    try:
        image_data = base64.b64decode(base64_string)
        image = Image.open(BytesIO(image_data))

        # Resize dimensions
        max_dimension = 1920
        width, height = image.size

        if width > max_dimension or height > max_dimension:
            if width > height:
                height = int((height / width) * max_dimension)
                width = max_dimension
            else:
                width = int((width / height) * max_dimension)
                height = max_dimension

        image = image.resize((width, height), Image.ANTIALIAS)

        # Compress and encode the image
        buffer = BytesIO()
        image.save(buffer, format="JPEG", quality=80)
        return base64.b64encode(buffer.getvalue()).decode("utf-8")
    except Exception as e:
        raise ValueError(f"Error compressing image: {e}")

# Sends evaluation data to an API with an optional prompt
def send_evaluation_to_api(scores: dict, area: str, prompt: str = "") -> dict:
    try:
        payload = {
            "area": area,
            "scores": scores,
            "prompt": prompt  # Optional prompt for context
        }

        response = requests.post("https://example.com/api/evaluations", json=payload)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        raise RuntimeError(f"Error sending evaluation to API: {e}")

# Sends image data to an API for analysis
def send_image_to_api(base64_image: str, prompt: str = "") -> dict:
    try:
        payload = {
            "image": base64_image,
            "prompt": prompt  # Optional prompt for context
        }

        response = requests.post("https://example.com/api/images", json=payload)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        raise RuntimeError(f"Error sending image to API: {e}")

# Sends both evaluation and image data to an API
def send_evaluation_and_image_to_api(scores: dict, area: str, base64_image: str, prompt: str = "") -> dict:
    try:
        payload = {
            "area": area,
            "scores": scores,
            "image": base64_image,
            "prompt": prompt  # Optional prompt for context
        }

        response = requests.post("https://example.com/api/evaluation-image", json=payload)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        raise RuntimeError(f"Error sending evaluation and image to API: {e}")

# Example usage
if __name__ == "__main__":
    # Sample data
    sample_scores = {
        "sort": 8,
        "setInOrder": 7,
        "shine": 9,
        "standardize": 6,
        "sustain": 5,
    }

    area_name = "Warehouse A"
    prompt_text = "Evaluate compliance and provide recommendations."

    # File path to the image
    image_path = "path/to/image.jpg"

    if validate_image_size(image_path):
        base64_image = convert_to_base64(image_path)
        compressed_image = compress_image(base64_image)

        # Send evaluation and image data to the API
        result = send_evaluation_and_image_to_api(sample_scores, area_name, compressed_image, prompt_text)

        print("API Response:", result)
    else:
        print("The image is too large to process.")
