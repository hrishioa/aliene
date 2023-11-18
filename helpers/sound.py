from openai import OpenAI
import sounddevice as sd
import logging
import numpy as np
import wavio
import keyboard
import queue
import sys

from helpers.files import clear_input_buffer, generate_datecoded_filename

def transcribe_audio(file_path):
    client = OpenAI()
    with open(file_path, 'rb') as audio_file:
        response = client.audio.transcriptions.create(
            file=audio_file,
            model="whisper-1"
        )
    return response.text
    
def get_user_preference():
    devices = [device for device in sd.query_devices() if device['max_input_channels'] > 0]
    index_and_name = [
        (device['index'], device['name']) for device in devices
    ]
    for i, name in index_and_name:
        logging.info(f"{i} - {name}")
    user_choice = int(input("Please choose a device by entering its index: "))
    chosen_device = next(device for device in devices if device['index'] == user_choice)
    logging.info(f"You chose device {user_choice}: {chosen_device['name']}")
    return chosen_device

def record_user_audio(device):
    # Set the duration and sample rate
    
    fs = 44100  # Sample rate

    # Get the default device
    
        
    channels = device["max_input_channels"]

    if channels < 2:
        print(f"Warning: The default device only supports {channels} input channel(s).")
        print("Recording will be done with only 1 channel.")
        channels = 1
        
    buffer = queue.Queue()

    def callback(indata, frames, time, status):
        """This will be called for each block of audio."""
        buffer.put(indata.copy()) 

    # Create the stream
    stream = sd.InputStream(callback=callback, device=device["index"], channels=channels)

    # Start the stream
    stream.start()
    print("Recording... Press 'r' to stop.")

    # Wait for 'r' key press to stop recording
    keyboard.wait('r')

    # Stop the stream
    stream.stop()
    # Retrieve the audio data from the buffer and concatenate into one numpy array
    recording = np.concatenate(list(buffer.queue))
    filename = generate_datecoded_filename(
        "audio", "wav"
    )
    # Save the recording to a file
    wavio.write(filename, recording, fs, sampwidth=2)

    # Clear the input buffer by reading keys until the buffer is empty
    clear_input_buffer()

    return filename
    