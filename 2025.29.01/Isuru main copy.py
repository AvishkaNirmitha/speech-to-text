import torch
import numpy as np
import pyaudio
import time
from pydub import AudioSegment
import sys
import keyboard  # Add this import at the top

# Configuration Constants
CHUNK_SIZE = 512
RATE = 16000
FORMAT = pyaudio.paInt16
CHANNELS = 1
VAD_THRESHOLD = 0.7
SILENCE_DURATION = 5
MAX_RECORD_TIME = 60
INITIAL_BUFFER_TIME = 1

# Human voice frequency range (Hz)
MIN_HUMAN_FREQ = 85  # Typical adult male lowest fundamental
MAX_HUMAN_FREQ = 300  # Typical child/young female highest fundamental

# Initialize PyAudio and VAD model
p = pyaudio.PyAudio()
vad_model = torch.jit.load("C:\\Users\\menuk\\Desktop\\whisper b and f\\silero_vad.jit")
if isinstance(vad_model, tuple):
    vad_model = vad_model[0]

def get_dominant_frequency(audio_chunk, sample_rate):
    """Estimate dominant frequency using FFT"""
    fft_data = np.fft.rfft(audio_chunk)
    magnitudes = np.abs(fft_data)
    frequencies = np.fft.rfftfreq(len(audio_chunk), 1/sample_rate)
    
    # Find peak frequency with significant energy
    peak_index = np.argmax(magnitudes)
    peak_magnitude = magnitudes[peak_index]
    
    # Basic noise floor threshold (adjust based on your environment)
    if peak_magnitude < 1000:
        return None  # No significant frequency component
    
    return frequencies[peak_index]

def is_human_voice(audio_chunk, sample_rate):
    """Combined VAD and frequency range check"""
    # Convert to float32 for VAD
    float_audio = audio_chunk.astype(np.float32) / 32768.0
    
    # First check VAD
    with torch.no_grad():
        vad_prob = vad_model(torch.from_numpy(float_audio).unsqueeze(0), sample_rate).item()
    
    if vad_prob < VAD_THRESHOLD:
        return False
    
    # Then check frequency characteristics
    dominant_freq = get_dominant_frequency(audio_chunk, sample_rate)
    
    if dominant_freq is None:
        return False
    
    return MIN_HUMAN_FREQ <= dominant_freq <= MAX_HUMAN_FREQ

def record_audio():
    print("Recording started... Press 'q' to stop recording")
    stream = p.open(format=FORMAT,
                    channels=CHANNELS,
                    rate=RATE,
                    input=True,
                    frames_per_buffer=CHUNK_SIZE)

    frames = []  # Store all frames (including silence)
    silence_counter = 0
    has_speech = False
    start_time = time.time()

    try:
        while True:
            # Check if 'q' is pressed
            if keyboard.is_pressed('q'):
                print("\nStopping recording due to 'q' key press...")
                break

            # Read audio chunk
            raw_data = np.frombuffer(stream.read(CHUNK_SIZE), dtype=np.int16)
            
            # Append all recorded data (including silence)
            frames.append(raw_data.copy())

            # Human voice check
            human_voice = is_human_voice(raw_data, RATE)

            # Update silence counter
            if human_voice:
                silence_counter = 0
                has_speech = True  # Mark that speech was detected
            else:
                if time.time() - start_time > INITIAL_BUFFER_TIME:
                    silence_counter += CHUNK_SIZE / RATE

            # Check termination conditions
            elapsed = time.time() - start_time
            if silence_counter >= SILENCE_DURATION:
                print(f"Stopped after {SILENCE_DURATION}s silence/non-human sounds")
                break
            if elapsed >= MAX_RECORD_TIME:
                print(f"Maximum recording time ({MAX_RECORD_TIME}s) reached")
                break

            # Debug info
            print(f"Human: {human_voice} | Silence counter: {silence_counter:.1f}s")

    finally:
        stream.stop_stream()
        stream.close()
        p.terminate()

    # Save all recorded audio (including silence)
    save_audio(frames)

def save_audio(frames):
    filename = f"recording_{time.strftime('%Y%m%d-%H%M%S')}.mp3"
    audio_data = np.concatenate(frames, axis=0)
    audio_segment = AudioSegment(
        data=audio_data.tobytes(),
        sample_width=audio_data.dtype.itemsize,
        frame_rate=RATE,
        channels=CHANNELS
    )
    audio_segment.export(filename, format="mp3")
    print(f"Saved recording to {filename}")

def main():
    print("Choose an option:")
    print("1. Input voice")
    print("2. Exit")
    
    choice = input("Enter your choice (1/2): ")
    
    if choice == '1':
        record_audio()
    elif choice == '2':
        print("Exiting...")
        sys.exit(0)
    else:
        print("Invalid choice. Exiting...")
        sys.exit(1)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nRecording cancelled")
        sys.exit(0)