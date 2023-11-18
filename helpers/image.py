import base64 
import cv2
import logging
import keyboard
import time
from helpers.files import generate_datecoded_filename

def encode_image(image_path):
  with open(image_path, "rb") as image_file:
    return base64.b64encode(image_file.read()).decode('utf-8');

def get_user_webcam_image():
  # Initialize the camera

  logging.info("press 'p' to take a picture to accompany your query in 3 seconds. Otherwise, we'll skip this step.")
  start_time = time.time()  # get the current time

  while True:
      if keyboard.is_pressed('p'):  # if key 'p' is pressed 
          break  # finish the loop
      if time.time() - start_time > 3:  # if 3 seconds have passed
          logging.info('No key press detected within 3 seconds.')
          return  # early return
      time.sleep(0.1)  # pause execution for 0.1 seconds
  
  cam = cv2.VideoCapture(0)
  # Read input from the camera
  result, image = cam.read()

  # If input image detected without any error, save the image
  if result:
      filename = generate_datecoded_filename(
        "cam",
        "png"
      )
      cv2.imwrite(filename, image)
      logging.info(f"Image succesfully taken and stored at {filename}")
      return filename

  # Release the camera
  cam.release()
  