import pyttsx3

def text_to_speech(text, rate=150, volume=1.0, voice_gender='male'):

    print('text',text)

    return

    """
    Convert text to speech
    rate: speaking rate (default 150)
    volume: volume level 0-1 (default 1.0)
    voice_gender: 'male' or 'female' (default female)
    """
    engine = pyttsx3.init()
    
    # Configure properties
    engine.setProperty('rate', rate)
    engine.setProperty('volume', volume)
    
    # Set voice
    voices = engine.getProperty('voices')
    voice_index = 1 if voice_gender == 'female' else 0  # Usually 1=female, 0=male
    engine.setProperty('voice', voices[voice_index].id)
    
    # Convert and play
    engine.say(text)
    engine.runAndWait()

# Example usage
# text_to_speech("Hello, this is a test message.", rate=150, volume=0.8)