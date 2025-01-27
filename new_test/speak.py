import sys
import pyttsx3

def init_engine():
    engine = pyttsx3.init()
    engine.setProperty('rate', 200)
    engine.setProperty('volume', 1.0)   
    return engine

def say(phrase):
    engine = init_engine()
    engine.say(phrase)
    engine.runAndWait()  # Blocks until the phrase is spoken

if __name__ == "__main__":
    say(sys.argv[1])  # Speak the phrase passed as a command-line argument
