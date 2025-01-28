import requests
import os

def upload_audio_file(api_url, file_path):
    """
    Upload an audio file to the Flask API
    
    Args:
        api_url (str): The URL of the upload endpoint
        file_path (str): Path to the audio file to upload
    
    Returns:
        dict: Response from the server
    """
    # Check if file exists
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Audio file not found: {file_path}")
    
    # Check if file is mp3
    if not file_path.lower().endswith('.mp3'):
        raise ValueError("File must be an MP3")
    
    try:
        # Open the file in binary mode
        with open(file_path, 'rb') as audio_file:
            # Create the files dictionary for the request
            files = {
                'audio': (os.path.basename(file_path), audio_file, 'audio/mpeg')
            }
            
            # Make the POST request
            response = requests.post(api_url, files=files)
            
            # Check if request was successful
            response.raise_for_status()
            
            # Return the response data
            return response.json()
            
    except requests.exceptions.RequestException as e:
        print(f"Error uploading file: {e}")
        return None

# Example usage
if __name__ == "__main__":
    # URL of your Flask API endpoint
    API_URL = "https://940c-35-221-203-99.ngrok-free.app/api/upload/audio"
    
    # Path to your MP3 file
    AUDIO_FILE_PATH = "full.mp3"  # Replace with your actual file path
    
    try:
        # Upload the file
        result = upload_audio_file(API_URL, AUDIO_FILE_PATH)
        
        if result:
            print("Upload successful!")
            print("Server response:", result)
            print(f"File can be accessed at: {result.get('path')}")
        else:
            print("Upload failed!")
            
    except FileNotFoundError as e:
        print(f"Error: {e}")
    except ValueError as e:
        print(f"Error: {e}")
    except Exception as e:
        print(f"Unexpected error: {e}")