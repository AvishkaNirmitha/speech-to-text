from flask import Flask, request
import os

app = Flask(__name__)

UPLOAD_FOLDER = 'uploaded_audio_files'  # Directory to store uploaded files
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

@app.route('/upload_audio', methods=['POST'])
def upload_audio():
    """
    Endpoint to handle audio file uploads.
    """
    if 'file' not in request.files:
        return "No file part", 400
    
    file = request.files['file']
    
    if file.filename == '':
        return "No selected file", 400
    
    # Save the file
    filename = os.path.join(UPLOAD_FOLDER, file.filename)
    file.save(filename)
    
    return f"File {file.filename} uploaded successfully!", 200

if __name__ == "__main__":
    app.run(debug=True, port=5000)
