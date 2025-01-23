from gtts import gTTS
import pygame
import threading
import time

def text_to_speech_gtts(text, lang='en', slow=False, filename='output.mp3'):
    """
    Convert text to speech using gTTS, save it as a file, and play the audio using pygame.
    """
    try:
        # Generate and save audio
        tts = gTTS(text=text, lang=lang, slow=slow)
        tts.save(filename)
        print(f"Audio saved as: {filename}")

        # Initialize pygame mixer
        pygame.mixer.init()
        pygame.mixer.music.load(filename)
        pygame.mixer.music.play()

        # Wait until playback is complete
        while pygame.mixer.music.get_busy():
            time.sleep(0.1)

        # Quit pygame mixer after playing
        pygame.mixer.quit()

    except Exception as e:
        print(f"Error generating or playing audio: {e}")

def run_gtts_in_thread(text, lang='en', slow=False, filename='output.mp3'):
    """
    Run gTTS in a separate thread to process the text-to-speech.
    """
    tts_thread = threading.Thread(target=text_to_speech_gtts, args=(text, lang, slow, filename))
    tts_thread.start()
    return tts_thread

# Example usage
if __name__ == "__main__":
    # Create and start threads
    threads = []
    threads.append(run_gtts_in_thread("Hello, this is the first message!", filename="message1.mp3"))
    threads.append(run_gtts_in_thread("Bonjour, ceci est un message en français!", lang='fr', filename="message2.mp3"))
    threads.append(run_gtts_in_thread("Hola, este es un mensaje en español!", lang='es', filename="message3.mp3"))

    # Wait for all threads to finish
    for t in threads:
        t.join()

    print("All TTS tasks are completed.")

