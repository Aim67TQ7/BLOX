/**
 * Primary Purpose of This Code:
 * - Preparing Photos for API Transmission:
 *   Ensures images are ready to be sent via an API by converting, validating, and compressing them.
 * - Setting a Maximum File Size:
 *   Defines a limit (20MB) for the size of files to ensure efficient processing without overloading resources.
 * - Converting Files to Base64:
 *   Converts image files into a Base64 string format for embedding in web pages or sending in JSON responses.
 * - Validating Image Size:
 *   Ensures the file size does not exceed the defined maximum, preventing oversized files from being processed.
 * - Compressing Images:
 *   Reduces the dimensions and quality of large images to save space and improve performance while maintaining acceptable quality.
 */

// This sets the maximum file size to 20MB (in bytes).
export const MAX_FILE_SIZE = 20 * 1024 * 1024; // 20MB in bytes

// This function turns a file into a Base64 string, which is like turning the file into a text format.
export const convertToBase64 = (file: File): Promise<string> => {
  return new Promise((resolve, reject) => {
    const reader = new FileReader(); // A helper that reads files
    reader.readAsDataURL(file); // Start reading the file
    reader.onload = () => resolve(reader.result as string); // When done, return the Base64 string
    reader.onerror = (error) => reject(error); // If something goes wrong, let us know
  });
};

// This function checks if the file size is small enough (not bigger than MAX_FILE_SIZE).
export const validateImageSize = (file: File): boolean => {
  return file.size <= MAX_FILE_SIZE; // Returns true if the file is small enough
};

// This function makes a big image smaller without losing too much quality.
export const compressImage = async (base64String: string): Promise<string> => {
  return new Promise((resolve, reject) => {
    const img = new Image(); // A helper to work with images
    img.src = base64String; // Load the image from the Base64 string
    img.onload = () => {
      const canvas = document.createElement('canvas'); // A virtual drawing board
      const ctx = canvas.getContext('2d'); // A tool to draw on the board
      if (!ctx) {
        reject(new Error('Could not get canvas context')); // If the tool is missing, stop here
        return;
      }

      // Figure out the new size of the image while keeping its shape
      let { width, height } = img;
      const maxDimension = 1920; // The largest width or height allowed

      if (width > maxDimension || height > maxDimension) {
        if (width > height) {
          height = (height / width) * maxDimension; // Adjust height to match the new width
          width = maxDimension;
        } else {
          width = (width / height) * maxDimension; // Adjust width to match the new height
          height = maxDimension;
        }
      }

      canvas.width = width; // Set the canvas to the new width
      canvas.height = height; // Set the canvas to the new height
      ctx.drawImage(img, 0, 0, width, height); // Draw the smaller image on the board
      
      // Turn the new image into a smaller JPEG file with good quality
      const compressedBase64 = canvas.toDataURL('image/jpeg', 0.8);
      resolve(compressedBase64); // Return the new Base64 string
    };
    img.onerror = () => reject(new Error('Failed to load image')); // If loading the image fails, stop here
  });
};
