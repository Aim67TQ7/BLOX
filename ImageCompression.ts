// Hey! This code helps handle pictures in our app.
// It's written in TypeScript, which is like JavaScript but with extra safety rules.

// Think of this like a size limit sign at a swimming pool
// We're saying "no files bigger than 20 megabytes allowed!"
// We calculate it by multiplying: 20MB * 1024 (to get kilobytes) * 1024 (to get bytes)
export const MAX_FILE_SIZE = 20 * 1024 * 1024; // 20MB in bytes

/**
 * This function is like a translator - it takes a file (like a picture)
 * and turns it into a special code (called base64) that computers can easily work with
 * 
 * It's like taking a picture and turning it into a really long text message!
 * 
 * @param file - The picture file we want to translate
 * @returns A promise (like a "I'll get back to you later") with the translated file
 */
export const convertToBase64 = (file: File): Promise<string> => {
  // We make a promise (like saying "I promise I'll finish this task")
  return new Promise((resolve, reject) => {
    // FileReader is like a helper that knows how to read files
    const reader = new FileReader();
    // Tell the helper to start reading our file
    reader.readAsDataURL(file);
    // When the helper finishes reading, give back the result
    reader.onload = () => resolve(reader.result as string);
    // If something goes wrong, let us know about the error
    reader.onerror = (error) => reject(error);
  });
};

/**
 * This function checks if a picture file is too big
 * It's like having a bathroom scale to check if your luggage is too heavy for the airplane!
 * 
 * @param file - The file we want to check
 * @returns true if the file is small enough, false if it's too big
 */
export const validateImageSize = (file: File): boolean => {
  return file.size <= MAX_FILE_SIZE;
};

/**
 * This function makes pictures smaller (compresses them) so they don't take up too much space
 * It's like squeezing a big sponge to make it smaller!
 * 
 * Here's what it does:
 * 1. Makes sure the picture isn't too wide or tall (max 1920 pixels)
 * 2. Saves it as a JPEG (a type of picture file) that's a bit squeezed (80% quality)
 * 
 * It's like when you squeeze a sponge - it gets smaller but still works just fine!
 * 
 * @param base64String - The picture (in special computer code) that we want to make smaller
 * @returns A promise with the smaller version of the picture
 */
export const compressImage = async (base64String: string): Promise<string> => {
  return new Promise((resolve, reject) => {
    // Create a new picture holder
    const img = new Image();
    // Put our picture in the holder
    img.src = base64String;
    
    // When the picture is ready...
    img.onload = () => {
      // Make a canvas (like a digital painting canvas) to work on the picture
      const canvas = document.createElement('canvas');
      const ctx = canvas.getContext('2d');
      
      // Make sure our canvas is working
      if (!ctx) {
        reject(new Error('Oops! Could not get canvas to work'));
        return;
      }

      // Get the size of our picture
      let { width, height } = img;
      // This is the biggest we want our picture to be (1920 pixels)
      const maxDimension = 1920;

      // If the picture is too big, let's make it smaller
      // But we want to keep it looking right - like when you shrink a photo copy,
      // you want to keep everything in the right shape!
      if (width > maxDimension || height > maxDimension) {
        if (width > height) {
          // If it's wider than it is tall (like a landscape photo)
          height = (height / width) * maxDimension;
          width = maxDimension;
        } else {
          // If it's taller than it is wide (like a portrait photo)
          width = (width / height) * maxDimension;
          height = maxDimension;
        }
      }

      // Tell the canvas how big to be
      canvas.width = width;
      canvas.height = height;

      // Draw the picture onto our canvas at the new size
      ctx.drawImage(img, 0, 0, width, height);
      
      // Turn the picture into a JPEG that's a little squeezed (80% quality)
      // This makes the file smaller but still looks good!
      const compressedBase64 = canvas.toDataURL('image/jpeg', 0.8);
      resolve(compressedBase64);
    };

    // If something goes wrong while loading the picture, let us know
    img.onerror = () => reject(new Error('Oops! Could not load the picture'));
  });
};

// How to use this code:
// 1. First, you can check if a picture file is too big:
//    if (validateImageSize(myPictureFile)) {
//      console.log("Yay! The file is not too big!");
//    }
//
// 2. Then, you can turn it into computer code (base64):
//    const base64Picture = await convertToBase64(myPictureFile);
//
// 3. Finally, you can make it smaller:
//    const smallerPicture = await compressImage(base64Picture);
