import vosk
import pyaudio
import json
import sys

class RealtimeWordSTT:                         
    def __init__(self, model_path="vosk-model-small-en-us-0.15"):
        # Initialize audio parameters
        self.CHUNK = 4096
        self.FORMAT = pyaudio.paInt16
        self.CHANNELS = 1
        self.RATE = 16000

        # Initialize Vosk model
        vosk.SetLogLevel(-1)  # Disable logging
        self.model = vosk.Model(model_path)
        self.rec = vosk.KaldiRecognizer(self.model, self.RATE)

        # Initialize PyAudio
        self.p = pyaudio.PyAudio()
        self.stream = None

    def start_listening(self):
        """Start listening and printing words in real-time"""
        try:
            self.stream = self.p.open(
                format=self.FORMAT,
                channels=self.CHANNELS,
                rate=self.RATE,
                input=True,
                frames_per_buffer=self.CHUNK
            )

            print("Listening... Speak into your microphone.")
            print("Press Ctrl+C to stop.")
            
            while True:
                data = self.stream.read(self.CHUNK, exception_on_overflow=False)
                if self.rec.AcceptWaveform(data):
                    # This branch handles complete utterances
                    result = json.loads(self.rec.Result())
                    if result.get("text", "").strip():
                        print(result["text"])
                else:
                    # This branch handles partial results (words as they're spoken)
                    result = json.loads(self.rec.PartialResult())
                    if result.get("partial", "").strip():
                        # Clear line and print partial result
                        sys.stdout.write('\r' + ' ' * 80 + '\r')
                        sys.stdout.write(result["partial"])
                        sys.stdout.flush()

        except KeyboardInterrupt:
            print("\nStopping...")
        finally:
            self.stop_listening()

    def stop_listening(self):
        """Clean up resources"""
        if self.stream:
            self.stream.stop_stream()
            self.stream.close()
        self.p.terminate()

def main():
    """Main function to run the speech-to-text system"""
    print("Initializing speech recognition system...")
    print("First, download the Vosk model if you haven't already:")
    print("wget https://alphacephei.com/vosk/models/vosk-model-small-en-us-0.15.zip")
    print("unzip vosk-model-small-en-us-0.15.zip")
    
    # Initialize and start the speech recognition
    stt = RealtimeWordSTT()
    stt.start_listening()

if __name__ == "__main__":
    main()