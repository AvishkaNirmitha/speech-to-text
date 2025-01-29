import pyaudio
import numpy as np
from scipy.io.wavfile import write
import time
import pygame
import logging
from datetime import datetime
import threading
import requests

class AudioCapture:
    FORMAT = pyaudio.paInt16  # Audio format
    CHANNELS = 1  # Mono audio
    RATE = 44100  # Sample rate (Hz)
    CHUNK = 1024  # Frames per buffer

    def __init__(self, threshold: int, silence_limit: int, recording_limit: int, filename_prefix: str, keyword: str, model: str = "base.en"):
        """
        Initialize the AudioCapture class.

        :param threshold: The threshold value for starting the recording
        :param silence_limit: Silence limit in seconds
        :param recording_limit: Maximum recording length
        :param filename_prefix: Output filename prefix
        :param keyword: The word to listen for (not used here, for future use)
        :param model: The whisper model to use (for future use)
        """
        # Initialize variables
        self.threshold = threshold
        self.silence_limit = silence_limit
        self.recording_limit = recording_limit
        self.filename_prefix = filename_prefix
        self.keyword = keyword.lower()
        self.audio = pyaudio.PyAudio()
        self.play_sound = True  # Assume sound is available
        self.stop_recording_process = False  # Flag to stop recording process
        self.stop_program = False  # Flag to stop the entire program

        # Initialize Pygame for sound playback
        pygame.mixer.init()  # Initialize Pygame for sound
        pygame.mixer.music.set_volume(0.25)
        try:
            pygame.mixer.music.load("ding.mp3")  # Ensure this file is available
        except pygame.error as e:
            print(f"Error loading sound: {e}")
            self.play_sound = False

        # Set up logging
        self.logger = logging.getLogger("AudioCapture")
        logging.basicConfig(level=logging.INFO)

    def start_recording(self):
        """
        Start recording audio from the microphone.

        :return: None
        """
        frames = []
        silence_frames = 0
        total_frames = 0
        recording_started = False
        stream = self.audio.open(format=self.FORMAT, channels=self.CHANNELS, rate=self.RATE, input=True, frames_per_buffer=self.CHUNK)

        try:
            self.logger.info("Listening for speech...")

            while not self.stop_recording_process and not self.stop_program:
                try:
                    data = stream.read(self.CHUNK)
                except IOError:
                    self.logger.warning("Stream overflow: skipping this chunk of data.")
                    continue

                # Convert data to numpy array
                npdata = np.frombuffer(data, dtype=np.int16)
                np_mean = np.abs(npdata).mean()

                loud_enough = np_mean > self.threshold
                if loud_enough:
                    if not recording_started:
                        frames = []  # Reset frames to start new recording
                        recording_started = True
                    frames.append(npdata)
                    silence_frames = 0
                elif recording_started:
                    frames.append(npdata)
                    silence_frames += 1
                    if silence_frames > self.silence_limit * self.RATE / self.CHUNK:
                        self.logger.info("Reached silence limit. Stopping the current recording.")
                        # Save the audio once silence is detected
                        self.save_audio(frames)
                        frames = []  # Reset frames for the next recording
                        recording_started = False
                else:
                    # Decrease threshold dynamically (only if it's reasonable)
                    if np_mean < self.threshold and self.threshold > 150:
                        self.threshold -= 0.1 * self.threshold
                        self.logger.info(f"Threshold decreased to {self.threshold:.2f}")

                if self.recording_limit > 0 and recording_started and total_frames >= self.RATE / self.CHUNK * self.recording_limit:
                    self.logger.info("Reached recording time limit. Stopping the current recording.")
                    # Save the audio once time limit is reached
                    self.save_audio(frames)
                    frames = []  # Reset frames for the next recording
                    recording_started = False

                if recording_started:
                    total_frames += 1

        finally:
            stream.stop_stream()
            stream.close()

    def save_audio(self, frames):
        """
        Save the audio frames to a file and send the file to the server in a separate thread.

        :param frames: The audio frames to save
        :return: None
        """
        if frames:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"{self.filename_prefix}_{timestamp}.wav"  # Unique filename based on timestamp
            write(filename, self.RATE, np.concatenate(frames))  # Save audio as .wav file
            self.logger.info(f"Audio saved to {filename}")
            
            # Start a new thread for uploading the file to the server
            upload_thread = threading.Thread(target=self.upload_audio_to_server, args=(filename,))
            upload_thread.start()  # Start the thread for uploading

            # Optionally, play sound when finished
            if self.play_sound:
                pygame.mixer.music.play()
                while pygame.mixer.music.get_busy():
                    time.sleep(0.1)  # Wait for sound to finish

    def upload_audio_to_server(self, filename):
        """
        Function to upload the audio file to the server in a separate thread.

        :param filename: The filename of the audio to upload
        :return: None
        """
        server_url = "http://localhost:5000/upload_audio"
        try:
            files = {'file': open(filename, 'rb')}
            response = requests.post(server_url, files=files)
            files['file'].close()
            if response.status_code == 200:
                print("Audio file successfully sent to server.")
            else:
                print(f"Failed to send audio file to server. Status code: {response.status_code}")
        except Exception as e:
            print(f"Error while sending audio to server: {e}")

    def stop_recording(self):
        """
        Set the flag to stop the recording process.
        """
        self.stop_recording_process = True
        self.logger.info("Recording stopped.")

    def stop_program(self):
        """
        Set the flag to stop the entire program.
        """
        self.stop_program = True
        self.logger.info("Program stopped.")

def listen_for_input(audio_recorder):
    """
    Listen for user input to stop the recording process or the entire program.
    """
    while True:
        user_input = input("Press 'w' to stop recording, 'q' to stop the program: ")
        if user_input.lower() == 'w':
            audio_recorder.stop_recording()  # Stop only recording
        elif user_input.lower() == 'q':
            audio_recorder.stop_program()  # Stop the entire program
            break  # Exit the loop

if __name__ == "__main__":
    audio_recorder = AudioCapture(
        threshold=500, 
        silence_limit=2, 
        recording_limit=30, 
        filename_prefix="output", 
        keyword="hello"
    )

    # Start the recording in a separate thread
    recording_thread = threading.Thread(target=audio_recorder.start_recording)
    recording_thread.start()

    # Start listening for user input to stop recording or the program
    listen_for_input(audio_recorder)

    # Wait for the recording thread to finish before exiting
    recording_thread.join()

    print("Program terminated.")
