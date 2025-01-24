import whisper
import sounddevice as sd
import soundfile as sf
import numpy as np
import datetime
import noisereduce as nr
import keyboard
import pyttsx3
from langchain_ollama import OllamaLLM

class AudioLLMAssistant:
    def __init__(self, sample_rate=16000):
        """
        Initialize audio recorder and text-to-speech engine.
        
        Args:
        sample_rate (int): Audio sample rate
        """
        # Audio recording setup
        self.sample_rate = sample_rate
        self.is_recording = False
        self.audio_chunks = []
        
        # Whisper model
        self.whisper_model = whisper.load_model("small")
        
        # Text-to-Speech setup
        self.engine = pyttsx3.init()
        self.engine.setProperty('rate', 200)
        self.engine.setProperty('volume', 1.0)
        
        # Set voice (first available voice)
        voices = self.engine.getProperty('voices')
        self.engine.setProperty('voice', voices[0].id)
        
        # Ollama LLM setup
        self.llm = OllamaLLM(
            model="llama3.1:8b",
            temperature=0.1,
            base_url="http://localhost:11434",
            streaming=True
        )
        
        # Initialize stop flag
        self.stop_flag = False

    def text_to_speech(self, text):
        """
        Convert text to speech.
        
        Args:
        text (str): Text to be spoken
        """
        # Remove extra spaces
        cleaned_text = ' '.join(text.split())
        print('Text response:', cleaned_text)
        
        # Convert text to speech in chunks
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
        """
        Continuously record audio until stopped.
        
        Returns:
        str: Transcribed text from the recording
        """
        print("Continuous recording started (press 'q' to stop)...")
        
        self.is_recording = True
        self.audio_chunks = []
        
        def audio_callback(indata, frames, time, status):
            if status:
                print(f"Status: {status}")
            if self.is_recording:
                self.audio_chunks.append(indata.copy())
        
        # Set up keyboard listener for 'q' key
        keyboard.add_hotkey('q', self.stop_recording)
        
        with sd.InputStream(callback=audio_callback, 
                            channels=1, 
                            samplerate=self.sample_rate):
            while self.is_recording:
                sd.sleep(100)
        
        # Remove 'q' key hotkey after recording
        keyboard.remove_hotkey('q')
        
        # If no audio was recorded, return None
        if not self.audio_chunks:
            print("No audio recorded.")
            return None
        
        # Combine recorded chunks
        recording = np.concatenate(self.audio_chunks)
        
        # Noise reduction
        reduced_noise = nr.reduce_noise(y=recording.flatten(), 
                                        sr=self.sample_rate, 
                                        prop_decrease=0.7)
        
        # Generate a unique filename with timestamp
        filename = f"recording_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.wav"
        
        # Save the recording as WAV
        sf.write(filename, reduced_noise, self.sample_rate)
        print(f"Recording saved as {filename}")
        
        # Transcribe the audio
        result = self.whisper_model.transcribe(filename, fp16=False)
        transcribed_text = result["text"]
        
        print("\nTranscription:")
        print(transcribed_text)
        
        return transcribed_text

    def stop_recording(self):
        """Stop the recording process."""
        print("Recording stopped.")
        self.is_recording = False

    def ask_question(self, question):
        """
        Send question to LLM and speak the response.
        
        Args:
        question (str): Question to be sent to LLM
        """
        print('Processing question:', question)
        
        chunk_buffer = []
        full_response = ""
        
        def stop_check():
            if keyboard.is_pressed('q'):
                self.stop_speaking()
                return True
            return False
        
        for i, chunk in enumerate(self.llm.stream(question)):
            if stop_check():
                break
            print(chunk, end='')
            chunk_buffer.append(chunk)
            full_response += chunk
            
            if (i + 1) % 16 == 0:
                combined_text = ' '.join(chunk_buffer)
                self.text_to_speech(combined_text)
                chunk_buffer = []
        
        # Handle any remaining chunks
        if chunk_buffer and not stop_check():
            combined_text = ' '.join(chunk_buffer)
            self.text_to_speech(combined_text)

    def run(self):
        """
        Main run method to record audio and process question.
        """
        while True:
            print("\nChoose an option:")
            print("1. Input voice")
            print("2. Exit")
            choice = input("Enter your choice (1/2): ").strip()
            
            if choice == '1':
                self.stop_flag = False  # Reset stop flag
                # Record audio
                transcription = self.record_audio()
                
                # If transcription is successful, process the question
                if transcription:
                    # Set up keyboard listener for 'q' key
                    keyboard.add_hotkey('q', self.stop_speaking)
                    self.ask_question(transcription)
                    # Remove 'q' key hotkey after speech synthesis
                    keyboard.remove_hotkey('q')
            elif choice == '2':
                print("Exiting the program.")
                break
            else:
                print("Invalid choice. Please enter 1 or 2.")

def main():
    assistant = AudioLLMAssistant()
    assistant.run()

if __name__ == "__main__":
    main()
