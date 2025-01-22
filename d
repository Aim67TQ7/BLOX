# Primary Purpose of This Code:
# - Preparing Photos for API Transmission:
#   Ensures images are ready to be sent via an API by converting, validating, and compressing them.
# - Setting a Maximum File Size:
#   Defines a limit (20MB) for the size of files to ensure efficient processing without overloading resources.
# - Converting Files to Base64:
#   Converts image files into a Base64 string format for embedding in web pages or sending in JSON responses.
# - Validating Image Size:
#   Ensures the file size does not exceed the defined maximum, preventing oversized files from being processed.
# - Compressing Images:
#   Reduces the dimensions and quality of large images to save space and improve performance while maintaining acceptable quality.

import base64
from io import BytesIO
from PIL import Image

# This sets the maximum file size to 20MB (in bytes).
MAX_FILE_SIZE = 20 * 1024 * 1024  # 20MB in bytes

# This function turns a file into a Base64 string.
def convert_to_base64(file_path: str) -> str:
    try:
        with open(file_path, "rb") as file:
            base64_string = base64.b64encode(file.read()).decode("utf-8")
            return base64_string
    except Exception as e:
        raise ValueError(f"Error converting file to Base64: {e}")

# This function checks if the file size is small enough (not bigger than MAX_FILE_SIZE).
def validate_image_size(file_path: str) -> bool:
    try:
        file_size = os.path.getsize(file_path)
        return file_size <= MAX_FILE_SIZE
    except Exception as e:
        raise ValueError(f"Error validating file size: {e}")

# This function makes a big image smaller without losing too much quality.
def compress_image(base64_string: str) -> str:
    try:
        # Decode the Base64 string to an image
        image_data = base64.b64decode(base64_string)
        image = Image.open(BytesIO(image_data))

        # Figure out the new size of the image while keeping its shape
        width, height = image.size
        max_dimension = 1920  # The largest width or height allowed

        if width > max_dimension or height > max_dimension:
            if width > height:
                height = int((height / width) * max_dimension)
                width = max_dimension
            else:
                width = int((width / height) * max_dimension)
                height = max_dimension

        # Resize the image
        image = image.resize((width, height), Image.ANTIALIAS)

        # Save the compressed image to a BytesIO buffer
        buffer = BytesIO()
        image.save(buffer, format="JPEG", quality=80)  # Compress to JPEG with 80% quality
        compressed_base64 = base64.b64encode(buffer.getvalue()).decode("utf-8")

        return compressed_base64
    except Exception as e:
        raise ValueError(f"Error compressing image: {e}")
