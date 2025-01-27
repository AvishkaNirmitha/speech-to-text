from langchain_ollama import OllamaLLM
import sys
import pyttsx3
import os
from dotenv import load_dotenv

engine = pyttsx3.init()
engine.setProperty('rate', 200)
engine.setProperty('volume', 1.0)

voices = engine.getProperty('voices')
voice_index = 0
engine.setProperty('voice', voices[voice_index].id)

load_dotenv()

model_name = os.getenv("OLLAMA_MODEL", "phi3:latest")

def text_to_speech(text):
    print('text---------------------------------->', text)
    engine.say(text)
    engine.runAndWait()

def ask_question(question):
    llm = OllamaLLM(
        model=model_name,
        temperature=0.1,
        base_url="http://localhost:11434",
        streaming=True
    )
    
    chunk_buffer = []
    for chunk in llm.stream(question):
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
            if complete_sentences:
                text_to_speech('. '.join(complete_sentences) + '.')
            
            # Reset buffer with the remaining incomplete sentence
            chunk_buffer = [remainder] if remainder.strip() else []
    
    # Handle any remaining text in the buffer
    if chunk_buffer:
        combined_text = ' '.join(chunk_buffer)
        if combined_text.strip():
            text_to_speech(combined_text)

# Test
question = "What is artificial intelligence?"
ask_question(question)