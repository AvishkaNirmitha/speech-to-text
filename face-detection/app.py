import cv2
import numpy as np
from tensorflow.keras.models import load_model
import time

class RealtimeEmotionDetector:
    def __init__(self, model_path, face_cascade_path='haarcascade_frontalface_default.xml'):
        """
        Initialize the real-time emotion detector
        
        Args:
            model_path (str): Path to the trained emotion detection model
            face_cascade_path (str): Path to OpenCV face cascade classifier
        """
        # Load the emotion detection model
        self.model = load_model(model_path)
        self.emotions = ['angry', 'disgust', 'fear', 'happiness', 
                        'neutral', 'sadness', 'surprise', 'contempt']
        
        # Load the face detection cascade classifier
        self.face_cascade = cv2.CascadeClassifier(face_cascade_path)
        
        # Initialize the webcam
        self.cap = cv2.VideoCapture(0)
        
    def preprocess_face(self, face_img):
        """
        Preprocess detected face for emotion detection
        """
        # Resize to model input size
        face_img = cv2.resize(face_img, (96, 96))
        # Convert to RGB (from BGR)
        face_img = cv2.cvtColor(face_img, cv2.COLOR_BGR2RGB)
        # Normalize
        face_img = face_img / 255.0
        # Add batch dimension
        face_img = np.expand_dims(face_img, axis=0)
        return face_img
    
    def run(self):
        """
        Run the real-time emotion detection
        """
        while True:
            # Read frame from webcam
            ret, frame = self.cap.read()
            if not ret:
                break
                
            # Convert to grayscale for face detection
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            
            # Detect faces
            faces = self.face_cascade.detectMultiScale(
                gray,
                scaleFactor=1.1,
                minNeighbors=5,
                minSize=(30, 30)
            )
            
            # Process each detected face
            for (x, y, w, h) in faces:
                # Extract face ROI
                face_roi = frame[y:y+h, x:x+w]
                
                # Preprocess face for emotion detection
                processed_face = self.preprocess_face(face_roi)
                
                # Predict emotion
                predictions = self.model.predict(processed_face)
                emotion_idx = np.argmax(predictions[0])
                emotion = self.emotions[emotion_idx]
                confidence = predictions[0][emotion_idx]
                
                # Draw rectangle around face
                cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 2)
                
                # Display emotion and confidence
                text = f"{emotion} ({confidence:.2f})"
                cv2.putText(frame, text, (x, y-10),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.9,
                           (0, 255, 0), 2)
            
            # Display the frame
            cv2.imshow('Real-time Emotion Detection', frame)
            
            # Break loop on 'q' press
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
        
        # Clean up
        self.cap.release()
        cv2.destroyAllWindows()
    
    def __del__(self):
        """
        Cleanup when the object is deleted
        """
        if hasattr(self, 'cap'):
            self.cap.release()

def main():
    # Initialize and run the detector
    try:
        detector = RealtimeEmotionDetector(
            model_path='emotiondetector.h5',
            face_cascade_path='haarcascade_frontalface_default.xml'
        )
        detector.run()
    except Exception as e:
        print(f"Error: {str(e)}")
        
if __name__ == "__main__":
    main()