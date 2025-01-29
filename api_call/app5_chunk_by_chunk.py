from langchain_ollama import OllamaLLM
import sys
import pyttsx3
import os
import time
# from dotenv import load_dotenv

engine = pyttsx3.init()
engine.setProperty('rate', 200)
engine.setProperty('volume', 1.0)

voices = engine.getProperty('voices')
voice_index = 0
engine.setProperty('voice', voices[voice_index].id)

# load_dotenv()

model_name = 'phi3:latest'
model_name = 'phi3:latest' # temp

llm = OllamaLLM(
    model=model_name,
    temperature=0.1,
    base_url="http://localhost:11434",
    streaming=True
)

def text_to_speech(text):
    print('text---------------------------------->', text)
    engine.say(text)
    engine.runAndWait()

def ask_question(question):
    print('question---------------------------------->', question)


    
    chunk_buffer = []
    start_time = time.time()
    for chunk in llm.stream(question):
        end_time_audio_send = time.time()
        execution_time_audio_send = end_time_audio_send - start_time
        print(f"time for one chunk: {execution_time_audio_send:.6f} seconds")
        print(chunk)
        chunk_buffer.append(chunk)
        combined_text = ' '.join(chunk_buffer)

        text_to_speech(chunk)
        # return
        
        # Check if we have a complete sentence (ends with period)
        # if '.' in combined_text:
        #     # Split by period and keep the last incomplete sentence
        #     sentences = combined_text.split('.')
        #     complete_sentences = sentences[:-1]  # All complete sentences
        #     remainder = sentences[-1]  # Incomplete sentence
            
        #     # Speak complete sentences
        #     if complete_sentences:
        #         text_to_speech('. '.join(complete_sentences) + '.')
            
        #     # Reset buffer with the remaining incomplete sentence
        #     chunk_buffer = [remainder] if remainder.strip() else []
    
    # Handle any remaining text in the buffer
    if chunk_buffer:
        combined_text = ' '.join(chunk_buffer)
        if combined_text.strip():
            text_to_speech(combined_text)

# Test
# question = "What is artificial intelligence?"
# ask_question(question)

ask_question("What is artificial intelligence?")