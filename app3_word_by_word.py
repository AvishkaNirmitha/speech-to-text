from langchain_ollama import OllamaLLM
import sys
import pyttsx3



engine = pyttsx3.init()

# Configure properties
engine.setProperty('rate', 150)
engine.setProperty('volume', 1.0)

# Set voice
voices = engine.getProperty('voices')
voice_index = 1 if 'male' == 'female' else 0  # Usually 1=female, 0=male
engine.setProperty('voice', voices[voice_index].id)


def text_to_speech(text):

    print('text---------------------------------->',text)


    
    # Convert and play
    engine.say(text)
    engine.runAndWait()



def ask_question(question):
    llm = OllamaLLM(
        model="llama3:latest",
        temperature=0.1,
        base_url="http://localhost:11434",
        streaming=True
    )
    
    for chunk in llm.stream(question):
        # print(chunk, end='', flush=True)
        print(chunk)
        text_to_speech(chunk)
    # print()

# Test
question = "What is artificial intelligence?"
ask_question(question)

