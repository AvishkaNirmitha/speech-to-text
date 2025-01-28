const fs = require("fs");
const path = require("path");
const axios = require("axios");
const FormData = require("form-data");

/**
 * Upload an audio file to the Flask API
 *
 * @param {string} apiUrl - The URL of the upload endpoint
 * @param {string} filePath - Path to the audio file to upload
 * @returns {Promise<object>} - Response from the server
 */
async function uploadAudioFile(apiUrl, filePath) {
  // Check if file exists
  if (!fs.existsSync(filePath)) {
    throw new Error(`Audio file not found: ${filePath}`);
  }

  // Check if file is an MP3
  if (path.extname(filePath).toLowerCase() !== ".mp3") {
    throw new Error("File must be an MP3");
  }

  try {
    // Create a FormData instance and append the file
    const formData = new FormData();
    formData.append("audio", fs.createReadStream(filePath), {
      filename: path.basename(filePath),
      contentType: "audio/mpeg",
    });

    // Make the POST request
    const response = await axios.post(apiUrl, formData, {
      headers: {
        ...formData.getHeaders(),
      },
    });

    // Return the response data
    return response.data;
  } catch (error) {
    console.error(`Error uploading file: ${error.message}`);
    return null;
  }
}

// Example usage
(async () => {
  // URL of your Flask API endpoint
  const API_URL = "https://940c-35-221-203-99.ngrok-free.app/api/upload/audio";

  // Path to your MP3 file
  const AUDIO_FILE_PATH = "message1.mp3"; // Replace with your actual file path

  // Number of parallel API calls
  const numCalls = 2;

  try {
    // Create an array of promises for parallel API calls
    const promises = Array.from({ length: numCalls }, () =>
      uploadAudioFile(API_URL, AUDIO_FILE_PATH)
    );

    // Wait for all promises to resolve
    const results = await Promise.all(promises);

    results.forEach((result, index) => {
      if (result) {
        console.log(`Upload ${index + 1} successful!`);
        console.log("Server response:", result);
        console.log(`File can be accessed at: ${result.path}`);
      } else {
        console.log(`Upload ${index + 1} failed!`);
      }
    });
  } catch (error) {
    console.error(`Error: ${error.message}`);
  }
})();
