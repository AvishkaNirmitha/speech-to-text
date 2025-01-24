from langchain_ollama import OllamaLLM
import threading
import queue
import pyttsx3

class TextToSpeechManager:
    def __init__(self):
        self.text_queue = queue.Queue()
        self.tts_engine = pyttsx3.init()
        self.tts_engine.setProperty('rate', 150)
        self.tts_engine.setProperty('volume', 1.0)
        
        voices = self.tts_engine.getProperty('voices')
        self.tts_engine.setProperty('voice', voices[0].id)
        
        self.tts_thread = threading.Thread(target=self._tts_worker, daemon=True)
        self.tts_thread.start()

    def _tts_worker(self):
        while True:
            text = self.text_queue.get()
            if text == "STOP":
                break
            self.tts_engine.say(text)
            self.tts_engine.runAndWait()
            self.text_queue.task_done()

    def speak(self, text):
        self.text_queue.put(text)

    def stop(self):
        self.text_queue.put("STOP")

def ask_question(tts_manager, question):
    llm = OllamaLLM(
        model="phi3:latest",
        temperature=0.1,
        base_url="http://localhost:11434",
        streaming=True
    )
    
    full_response = ""
    for chunk in llm.stream(question):
        full_response += chunk
        print(chunk, end='', flush=True)
    
    tts_manager.speak(full_response)
    tts_manager.stop()

# Usage
tts_manager = TextToSpeechManager()
question = "What is artificial intelligence?"
ask_question(tts_manager, question)