from langchain_ollama import OllamaLLM
import threading
import queue
import time
from subprocess import call
import keyboard
import os
from dotenv import load_dotenv

load_dotenv()

model_name = os.getenv("OLLAMA_MODEL", "phi3:latest")
python_executable = os.getenv("PYTHON_EXECUTABLE", "C:/Python311/python.exe")
script_path = os.getenv("SPEAK_SCRIPT_PATH", "C:/Users/Nuwan/OneDrive/Desktop/ML/Spera ML/Task10_AI_agent/speech-to-text/new_test/speak.py")

class TextToSpeechSystem:
    def __init__(self):
        # Create a queue to hold generated words
        self.word_queue = queue.Queue()
        self.stop_flag = threading.Event()  # Event to signal threads to stop

    def text_generation_thread(self, question):
        llm = OllamaLLM(
            model=model_name,
            temperature=0.1,
            base_url="http://localhost:11434",
            streaming=True
        )
        
        chunk_buffer = []
        for chunk in llm.stream(question):

            if self.stop_flag.is_set():  # Check if stop signal is triggered
                break

            print(chunk)
            chunk_buffer.append(chunk)
            combined_text = ' '.join(chunk_buffer)
        
            # Check if we have a complete sentence (ends with period)
            if '.' in combined_text:
                # Split by period and keep the last incomplete sentence
                sentences = combined_text.split('.')
                complete_sentences = sentences[:-1]  # All complete sentences
                remainder = sentences[-1]  # Incomplete sentence
            
                # Speak complete sentences
                for sentence in complete_sentences:
                     # Add word to the queue
                    self.word_queue.put(sentence.strip())
                    time.sleep(1)  # Simulate some delay in word generation
                # Reset buffer with the remaining incomplete sentence
                chunk_buffer = [remainder.strip()] if remainder.strip() else []

        # Handle any remaining text in the buffer
        if chunk_buffer:
            self.word_queue.put(' '.join(chunk_buffer).strip())

        self.word_queue.put(None)  # Signal the end of word generation

    def text_to_speech_thread(self):
        while not self.stop_flag.is_set():  # Continue until stop signal is triggered
            word = self.word_queue.get()  # Get the next word from the queue

            if word is None:  # If `None` is encountered, stop the thread
                break

            print(f"Speaking: {word}")  # Print the word being spoken
            # Use subprocess to call the speak.py script
            call([python_executable, script_path, word])

    def keyboard_listener_thread(self):
        print("Press 'q' to stop the threads.")
        while not self.stop_flag.is_set():
            if keyboard.is_pressed('q'):  # Check if 'q' key is pressed
                print("Stopping threads...")
                self.stop_flag.set()  # Trigger the stop signal
                self.word_queue.put(None)  # Add termination signal for the speech thread
                break

    def run(self, words):
        # Create threads
        gen_thread = threading.Thread(target=self.text_generation_thread, args=(words,))
        tts_thread = threading.Thread(target=self.text_to_speech_thread)
        keyboard_thread = threading.Thread(target=self.keyboard_listener_thread)

        # Start threads
        gen_thread.start()
        tts_thread.start()
        keyboard_thread.start()

        # Wait for threads to complete
        gen_thread.join()
        tts_thread.join()
        keyboard_thread.join()

# Example usage
if __name__ == "__main__":
    question = "What is artificial intelligence?"
    tts_system = TextToSpeechSystem()
    tts_system.run(question)
