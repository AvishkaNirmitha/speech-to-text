import os
import queue
import sounddevice as sd
import pyttsx3
from vosk import Model, KaldiRecognizer

class VoiceAssistant:
    def __init__(self):
        # self.model_path = "vosk-model-en-us-0.22"
        self.model_path = "vosk-model-small-en-us-0.15"
        self.recognition_queue = queue.Queue()
        self.speech_engine = pyttsx3.init()
        self.recognizer = None
        self.is_listening = False

        # Load the Vosk model
        if not os.path.exists(self.model_path):
            print("Model not found! Please download the Vosk model.")
            exit(1)

        self.model = Model(self.model_path)
        self.recognizer = KaldiRecognizer(self.model, 16000)

        # Configure text-to-speech engine
        self.speech_engine.setProperty('rate', 150)

    def start_listening(self):
        self.is_listening = True
        print("Listening...")
        with sd.RawInputStream(samplerate=16000, blocksize=8000, dtype="int16",
                               channels=1, callback=self.audio_callback):
            while self.is_listening:
                self.process_audio()

    def stop_listening(self):
        self.is_listening = False
        print("Stopped listening.")

    def audio_callback(self, indata, frames, time, status):
        if status:
            print("Audio status:", status)
        self.recognition_queue.put(bytes(indata))

    def process_audio(self):
        while not self.recognition_queue.empty():
            data = self.recognition_queue.get()
            if self.recognizer.AcceptWaveform(data):
                result = self.recognizer.Result()
                print("Recognized:", result)
                self.respond_to_speech(result)

    def respond_to_speech(self, text):
        response = f"I heard you say: {text}"
        print('text',text)
        # print("Assistant:", response)
        # self.speech_engine.say(response)
        # self.speech_engine.runAndWait()

if __name__ == "__main__":
    assistant = VoiceAssistant()
    try:
        assistant.start_listening()
    except KeyboardInterrupt:
        assistant.stop_listening()
