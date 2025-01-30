import sounddevice as sd
import numpy as np
import datetime
import keyboard
import pyttsx3
import requests
import noisereduce as nr
import soundfile as sf
from pydub import AudioSegment
import os
from concurrent.futures import ThreadPoolExecutor
import aiohttp
import asyncio
import time
import new_pyttsx3
# import app5_chunk_by_chunk

class AudioClient:
    def __init__(self, sample_rate=16000):
        self.server_url = "https://4976-34-126-166-100.ngrok-free.app/"
        self.sample_rate = sample_rate
        self.is_recording = False
        self.audio_chunks = []
        
        # Initialize TTS engine only when needed
        self._engine = None
        self.stop_flag = False
        
        # Create thread pool for parallel processing
        self.executor = ThreadPoolExecutor(max_workers=3)

    @property
    def engine(self):
        """Lazy initialization of TTS engine"""
        if self._engine is None:
            self._engine = pyttsx3.init()
            self._engine.setProperty('rate', 200)
            self._engine.setProperty('volume', 1.0)
            voices = self._engine.getProperty('voices')
            self._engine.setProperty('voice', voices[0].id)
        return self._engine

    def stop_speaking(self):
        """Stop the speech synthesis process."""
        print("Speech synthesis stopped.")
        self.stop_flag = True
        if self._engine:
            self._engine.stop()

    async def send_audio_to_server(self, mp3_filename):
        """Asynchronous function to send audio to server"""

        start_time_audio_send = time.time()


        async with aiohttp.ClientSession() as session:
            with open(mp3_filename, 'rb') as f:
                data = aiohttp.FormData()
                data.add_field('audio', f, filename=mp3_filename, content_type='audio/mp3')
                
                async with session.post(f"{self.server_url}api/upload/audio", data=data) as response:
                    end_time_audio_send = time.time()
                    execution_time_audio_send = end_time_audio_send - start_time_audio_send
                    print(f"time for api call: {execution_time_audio_send:.6f} seconds")
                    response.raise_for_status()
                    return await response.json()

    def process_audio(self, recording):
        """Process audio in a separate thread"""
        reduced_noise = nr.reduce_noise(
            y=recording.flatten(), 
            sr=self.sample_rate,
            prop_decrease=0.7
        )
        
        mp3_filename = f"recording_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.mp3"
        temp_wav = "temp_recording.wav"
        
        # Write to WAV and convert to MP3
        sf.write(temp_wav, reduced_noise, self.sample_rate)
        audio = AudioSegment.from_wav(temp_wav)
        audio.export(mp3_filename, format="mp3", parameters=["-q:a", "0"])  # Use highest quality
        
        os.remove(temp_wav)
        return mp3_filename

    def text_to_speech(self, text):
        """Convert text to speech in a separate thread"""
        cleaned_text = ' '.join(text.split())
        print('Response:', cleaned_text)
        
        def speak():
            if not self.stop_flag:
                self.engine.say(cleaned_text)
                self.engine.runAndWait()
        
        self.executor.submit(speak)

    def record_audio(self):
        """Record audio with improved handling"""
        print("Recording started (press 'q' to stop)...")
        
        self.is_recording = True
        self.audio_chunks = []
        
        def audio_callback(indata, frames, time, status):
            if status:
                print(f"Status: {status}")
            if self.is_recording:
                # Pre-allocate numpy array for better performance
                chunk = np.empty_like(indata)
                np.copyto(chunk, indata)
                self.audio_chunks.append(chunk)
        
        keyboard.add_hotkey('q', self.stop_recording)
        
        with sd.InputStream(callback=audio_callback, 
                          channels=1, 
                          samplerate=self.sample_rate,
                          blocksize=4096):  # Larger blocksize for better performance
            while self.is_recording:
                sd.sleep(100)
        
        keyboard.remove_hotkey('q')
        
        if not self.audio_chunks:
            print("No audio recorded.")
            return None

        start_time = time.time()
        
        try:
            # Process audio in parallel
            recording = np.concatenate(self.audio_chunks)
            mp3_filename = self.executor.submit(self.process_audio, recording).result()

            end_time = time.time()
            execution_time = end_time - start_time
            print(f"time audio save: {execution_time:.6f} seconds")


            
            # Send to server asynchronously
            result = asyncio.run(self.send_audio_to_server(mp3_filename))

            # print('result---------------------------------->', result)
            print("\result json  converted:", result['result']['text'])

        

            
            return result
            
        except Exception as e:
            print(f"Error processing audio: {e}")
            return None
        finally:
            # Clean up in a separate thread
            def cleanup():
                if os.path.exists(mp3_filename):
                    os.remove(mp3_filename)
            self.executor.submit(cleanup)

    def stop_recording(self):
        print("Recording stopped.")
        self.is_recording = False

    def run(self):
        try:
            while True:
                print("\nChoose an option:")
                print("1. Record and process audio")
                print("2. Exit")
                choice = input("Enter your choice (1/2): ").strip()
                
                if choice == '1':
                    self.stop_flag = False
                    result = self.record_audio()
                    if result:
                        keyboard.add_hotkey('q', self.stop_speaking)

                        # app5_chunk_by_chunk.ask_question(result['result']['text'])

                        new_pyttsx3.text_to_answer(result['result']['text'])
            
                        keyboard.remove_hotkey('q')
                elif choice == '2':
                    break
                else:
                    print("Invalid choice. Please enter 1 or 2.")
        finally:
            # Cleanup resources
            self.executor.shutdown(wait=False)
            if self._engine:
                self._engine.stop()

def main():
    client = AudioClient()
    client.run()

if __name__ == "__main__":
    main()