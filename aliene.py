import keyboard
import cv2
import sounddevice as sd
import numpy as np
import wavio
import base64
import requests
from openai import OpenAI
from playsound import playsound
import logging
import threading
from datetime import datetime
import os
from dotenv import load_dotenv

from helpers.gpt import ask_gpt4_with_image, ask_gpt_4_vanilla, generate_translation, parse_user_command
from models.Command import Command, UserCommand

load_dotenv()

# Initialize logging
logging.basicConfig(level=logging.INFO)

openai_api_key = os.getenv("OPENAI_API_KEY")

client = OpenAI(
    api_key=openai_api_key,
    # default is 2
    max_retries=0,
)

def listen_for_keypress(key):
    keyboard.wait(key)

def capture_image(filename):
    cap = cv2.VideoCapture(-0)
    cap.set(3,640)
    cap.set(3,480)  # 0 is typically the default camera
    ret, frame = cap.read()
    while(True):
        success, img = cap.read()

        cv2.imshow('frame',img)

        if cv2.waitKey(1) & 0xFF == ord('p'):
            cv2.imwrite(filename, img)
            break
    cap.release()
    cv2.destroyAllWindows()

class AudioRecorder:
    def __init__(self, filename, fs=44100):
        self.filename = filename
        self.fs = fs
        self.recording = np.array([])
        self.is_recording = False
        self.thread = threading.Thread(target=self.record_background)

    def record_background(self):
        with sd.InputStream(samplerate=self.fs, channels=1, dtype='int16') as stream:
            self.is_recording = True
            while self.is_recording:
                data, _ = stream.read(1024)  # Read chunks of 1024 frames
                self.recording = np.append(self.recording, data)

    def normalize_audio(self, audio):
        """
        Normalize the audio data to be within the range -1.0 to 1.0
        """
        max_val = np.max(np.abs(audio))
        if max_val > 0:
            return audio / max_val
        return audio

    def start(self):
        self.thread.start()

    def stop(self):
        self.is_recording = False
        self.thread.join()
        wavio.write(self.filename, self.normalize_audio(self.recording.reshape(-1, 2)), self.fs/2, sampwidth=2)

def record_audio_on_keypress(filename, key='r'):
    """
    Records audio until the specified key is pressed.

    Args:
    filename (str): The name of the file to save the recording.
    key (str, optional): Key to stop recording. Defaults to 'r'.
    """
    recorder = AudioRecorder(filename)
    keyboard.wait(key)  # Wait for key press
    
    print(f"Recording... Press '{key}' to stop.")

    recorder.start()
    keyboard.wait(key)
    recorder.stop()
    print("Recording completed.")

def transcribe_audio(file_path):
    with open(file_path, 'rb') as audio_file:
        response = client.audio.transcriptions.create(
            file=audio_file,
            model="whisper-1"
        )
    return response

def ask_gpt4(question):
    response = client.chat.completions.create(
        model="gpt-4",
        messages=[
            {"role": "user", "content": question}
        ]
    )
    return response.choices[0].message.content

def text_to_speech(text, filename):
    response = client.audio.speech.create(
        model="tts-1",
        voice="shimmer",
        input=text
    )
    with open(filename, "wb") as f:
        f.write(response.content)
    playsound(filename)

def encode_image(image_path):
  with open(image_path, "rb") as image_file:
    return base64.b64encode(image_file.read()).decode('utf-8');



def generate_datecoded_filename(prefix, extension):
    datecode = datetime.now().strftime("%Y%m%d_%H%M%S")
    return f"data/{prefix}_{datecode}.{extension}"

def get_transcription():
    logging.info(" Press 'r' to start recording.")
    audio_file_path = generate_datecoded_filename("audio", "wav")
    record_audio_on_keypress(audio_file_path, 'r')
    transcription = transcribe_audio(audio_file_path)
    return transcription.text


def main():
    # Boot-up 
    logging.info("Ailene Starting up....")
    logging.info("Starting the application.")

    
    
    for i in range(4):
        if i > 0:
            choice = input("Would you like to continue interacting with Ailene? (Press q to quit and anything else to continue)")
            if choice and choice[-1] == "q":
                break
            

        transcription = get_transcription()
        logging.info(f"Obtained Transcript of {transcription}")
        
        command:Command = parse_user_command(transcription)
        

        if command == Command.QUERY:
            # Then we take a picture 
            choice = input("Would you like to include an image with this query? (Press y and everything else to skip)")
            comparison = choice == "y"
            logging.info(f"User made choice of {choice}. Choice is {comparison}")
            image_file_path = None
            if choice and choice[-1] == "y":
                image_file_path = generate_datecoded_filename("image", "jpg")
                logging.info(f"Generated image_file_path of {image_file_path}")
                capture_image(image_file_path)
                logging.info(f"Generated image of {image_file_path}")
            
            
            if image_file_path:
                response = ask_gpt4_with_image(
                    image_file_path,
                    transcription
                )
                response = response["choices"][0]["message"]["content"]
            else:
                response = ask_gpt_4_vanilla(
                    transcription
                )
            logging.info(f"Obtained Response of {response}")
            text_to_speech(response, generate_datecoded_filename("response", "mp3"))
        else:
            # We generate a translation
            response = generate_translation(transcription)
            text_to_speech(response, generate_datecoded_filename("response", "mp3"))


if __name__ == "__main__":
    main()