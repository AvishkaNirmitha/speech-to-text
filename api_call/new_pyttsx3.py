from langchain_ollama import OllamaLLM
import threading
import queue
import time
from subprocess import call, Popen
import keyboard
import os
from dotenv import load_dotenv
import signal

load_dotenv()

model_name =  "phi3:3.8b"
python_executable = "python"
script_path = "api_call\speak.py"

class TextToSpeechSystem:
    def __init__(self):
        # Create a queue to hold generated answers
        self.answers_sentence_queue = queue.Queue()
        self.stop_flag = threading.Event()  # Event to signal threads to stop
        self.current_process = None

    def answers_generation_thread(self, question):
        start_time = time.time()
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
                end_time = time.time()
                execution_time = end_time - start_time
                print(f"Total execution time: {execution_time:.6f} seconds")
            
                # Split by period and keep the last incomplete sentence
                sentences = combined_text.split('.')
                complete_sentences = sentences[:-1]  # All complete sentences
                remainder = sentences[-1]  # Incomplete sentence
            
                


                # Speak complete sentences
                for sentence in complete_sentences:


                     # Add sentence to the queue
                    self.answers_sentence_queue.put(sentence.strip())
                    time.sleep(1)  # Simulate some delay in sentence generation
                # Reset buffer with the remaining incomplete sentence
                chunk_buffer = [remainder.strip()] if remainder.strip() else []

        # Handle any remaining text in the buffer
        if chunk_buffer:
            self.answers_sentence_queue.put(' '.join(chunk_buffer).strip())

        self.answers_sentence_queue.put(None)  # Signal the end of sentence generation

    def text_to_speech_thread(self):
        while not self.stop_flag.is_set():  # Continue until stop signal is triggered
            speaking_sentence = self.answers_sentence_queue.get()  # Get the next speaking_sentence from the queue

            if speaking_sentence is None:  # If `None` is encountered, stop the thread
                self.stop_flag.set()
                if self.current_process:  # Check if a subprocess is running
                    self.current_process.terminate()  # Terminate the subprocess
                self.answers_sentence_queue.put(None)  # Add termination signal for TTS thread
                break

            print(f"Speaking: {speaking_sentence}")  # Print the speaking_sentence being spoken
            # Use subprocess to call the speak.py script
            self.current_process = Popen([python_executable, script_path, speaking_sentence])  # Start the subprocess
            self.current_process.wait()  # Wait for the subprocess to complete

            if self.stop_flag.is_set() and self.current_process:
                self.current_process.terminate()  # Terminate the subprocess
                self.current_process = None  # Clear the reference

    def keyboard_listener_thread(self):
        print("Press 'q' to stop the threads.")
        while not self.stop_flag.is_set():
            if keyboard.is_pressed('q'):  # Check if 'q' key is pressed
                print("Stopping threads...")
                self.stop_flag.set()
                if self.current_process:  # Check if a subprocess is running
                    self.current_process.terminate()  # Terminate the subprocess
                self.answers_sentence_queue.put(None)  # Add termination signal for TTS thread
                break

    def run(self, question):
        # Create threads
        gen_thread = threading.Thread(target=self.answers_generation_thread, args=(question,))
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

# # Example usage
# if __name__ == "__main__":
#     #listens for the questio

#     while True:
        
#         question = input("\nEnter a question (or type 'exit' to quit): ").strip()
#         if question.lower() == "exit":
#             print("Exiting the program.")
#             break
#         tts_system = TextToSpeechSystem()
#         tts_system.run(question)


def text_to_answer(question):
    tts_system = TextToSpeechSystem()
    tts_system.run(question)
