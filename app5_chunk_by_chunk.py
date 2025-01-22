from langchain_ollama import OllamaLLM
import sys
import pyttsx3

engine = pyttsx3.init()
engine.setProperty('rate', 150)
engine.setProperty('volume', 1.0)

voices = engine.getProperty('voices')
voice_index = 1 if 'male' == 'female' else 0
engine.setProperty('voice', voices[voice_index].id)

def text_to_speech(text):
    print('text---------------------------------->', text)
    engine.say(text)
    engine.runAndWait()

def ask_question(question):
    llm = OllamaLLM(
        model="llama3:latest",
        temperature=0.1,
        base_url="http://localhost:11434",
        streaming=True
    )
    
    chunk_buffer = []
    for i, chunk in enumerate(llm.stream(question)):
        print(chunk)
        chunk_buffer.append(chunk)
        
        if (i + 1) % 13 == 0:
            combined_text = ' '.join(chunk_buffer)
            text_to_speech(combined_text)
            chunk_buffer = []
    
    # Handle any remaining chunks
    if chunk_buffer:
        combined_text = ' '.join(chunk_buffer)
        text_to_speech(combined_text)

# Test
question = "What is artificial intelligence?"
ask_question(question)