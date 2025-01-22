from langchain_ollama import OllamaLLM
import sys
import pyttsx3
import threading
import queue

class TTSThread(threading.Thread):
    def __init__(self, text_queue):
        threading.Thread.__init__(self)
        self.text_queue = text_queue
        self.daemon = True
        self.engine = pyttsx3.init()
        self.engine.setProperty('rate', 150)
        self.engine.setProperty('volume', 1.0)
        voices = self.engine.getProperty('voices')
        voice_index = 1 if 'male' == 'female' else 0
        self.engine.setProperty('voice', voices[voice_index].id)

    def run(self):
        while True:
            text = self.text_queue.get()
            if text == "STOP":
                break
            print('text---------------------------------->', text)
            self.engine.say(text)
            self.engine.runAndWait()
            self.text_queue.task_done()

text_queue = queue.Queue()
tts_thread = TTSThread(text_queue)
tts_thread.start()

def text_to_speech(text):
    text_queue.put(text)

def ask_question(question):
    llm = OllamaLLM(
        # model="llama3:latest",
        model="phi3:latest",
        temperature=0.1,
        base_url="http://localhost:11434",
        streaming=True
    )
    
    for chunk in llm.stream(question):
        print(chunk)
        text_to_speech(chunk)

    text_queue.put("STOP")

# Test
question = "What is artificial intelligence?"
ask_question(question)

# text_to_speech("Hello, this is a test message.")