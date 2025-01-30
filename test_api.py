import sounddevice as sd
import numpy as np
import datetime
import keyboard
import pyttsx3
import requests
import noisereduce as nr
import soundfile as sf
from pydub import AudioSegment
import os

class AudioClient:
    def __init__(self, sample_rate=16000):
        """
        Initialize audio recorder and text-to-speech engine.
        
        Args:
        sample_rate (int): Audio sample rate
        """
        self.server_url = "https://4cf5-34-125-42-238.ngrok-free.app/"  # Base URL without /upload
        self.sample_rate = sample_rate
        self.is_recording = False
        self.audio_chunks = []
        
        # Text-to-Speech setup
        self.engine = pyttsx3.init()
        self.engine.setProperty('rate', 200)
        self.engine.setProperty('volume', 1.0)
        
        # Set voice (first available voice)
        voices = self.engine.getProperty('voices')
        self.engine.setProperty('voice', voices[0].id)
        
        # Initialize stop flag
        self.stop_flag = False

    def text_to_speech(self, text):
        """Convert text to speech."""
        cleaned_text = ' '.join(text.split())
        print('Response:', cleaned_text)
        
        def on_word(name, location, length):
            if self.stop_flag:
                self.engine.stop()
        
        self.engine.connect('started-word', on_word)
        self.engine.say(cleaned_text)
        self.engine.runAndWait()

    def stop_speaking(self):
        """Stop the speech synthesis process."""
        print("Speech synthesis stopped.")
        self.stop_flag = True
        self.engine.stop()

    def record_audio(self):
        """Record audio and send to server for processing."""
        print("Recording started (press 'q' to stop)...")
        
        self.is_recording = True
        self.audio_chunks = []
        
        def audio_callback(indata, frames, time, status):
            if status:
                print(f"Status: {status}")
            if self.is_recording:
                self.audio_chunks.append(indata.copy())
        
        keyboard.add_hotkey('q', self.stop_recording)
        
        with sd.InputStream(callback=audio_callback, 
                          channels=1, 
                          samplerate=self.sample_rate):
            while self.is_recording:
                sd.sleep(100)
        
        keyboard.remove_hotkey('q')
        
        if not self.audio_chunks:
            print("No audio recorded.")
            return None
        
        # Process and save audio
        recording = np.concatenate(self.audio_chunks)
        reduced_noise = nr.reduce_noise(y=recording.flatten(), 
                                      sr=self.sample_rate,
                                      prop_decrease=0.7)
        
        # Save as MP3
        mp3_filename = f"recording_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.mp3"
        temp_wav = "temp_recording.wav"
        
        sf.write(temp_wav, reduced_noise, self.sample_rate)
        audio = AudioSegment.from_wav(temp_wav)
        audio.export(mp3_filename, format="mp3")
        
        os.remove(temp_wav)
        
        print(f"Recording saved as {mp3_filename}")
        
        # Send to server
        try:
            with open(mp3_filename, 'rb') as f:
                files = {'audio': (mp3_filename, f, 'audio/mp3')}
                response = requests.post(f"{self.server_url}/upload", files=files)
                
                # Print response details for debugging
                print(f"Response status code: {response.status_code}")
                print(f"Response content: {response.text}")
                
                response.raise_for_status()
                result = response.json()
                print("\nTranscription:", result['transcription'])
                return result
                
        except requests.exceptions.RequestException as e:
            print(f"Error sending audio to server: {e}")
            return None
        except Exception as e:
            print(f"Unexpected error: {e}")
            return None
        finally:
            # Clean up the temporary file
            if os.path.exists(mp3_filename):
                os.remove(mp3_filename)

    def stop_recording(self):
        """Stop the recording process."""
        print("Recording stopped.")
        self.is_recording = False

    def run(self):
        """Main run method."""
        while True:
            print("\nChoose an option:")
            print("1. Record and process audio")
            print("2. Exit")
            choice = input("Enter your choice (1/2): ").strip()
            
            if choice == '1':
                self.stop_flag = False
                result = self.record_audio()
                if result:
                    keyboard.add_hotkey('q', self.stop_speaking)
                    self.text_to_speech(result.get('response', 'No response from server'))
                    keyboard.remove_hotkey('q')
            elif choice == '2':
                print("Exiting the program.")
                break
            else:
                print("Invalid choice. Please enter 1 or 2.")

def main():
    client = AudioClient()
    client.run()

if __name__ == "__main__":
    main()