from instructor import patch
from openai import OpenAI
import requests
import os
from helpers.image import encode_image
from models.Command import Translation, UserCommand
from dotenv import load_dotenv
load_dotenv()
client = patch(OpenAI())

def ask_gpt_4_vanilla(prompt):
    response = client.chat.completions.create(
        model="gpt-4-0613",
        messages=[
            {
                "role":"system",
                "content":"You are a world class helpful assistant. Your"
            },
            {
            "role": "user",
            "content": prompt
            }
        ],
        max_tokens=300,
    )

    return response.choices[0].message.content

def ask_gpt4_with_image(image_path, text):
    base64_image = encode_image(image_path)
    openai_api_key = os.getenv("OPENAI_API_KEY")
    headers = {
      "Content-Type": "application/json",
      "Authorization": f"Bearer {openai_api_key}"
    }
    

    payload = {
      "model": "gpt-4-vision-preview",
      "messages": [
        {
          "role": "user",
          "content": [
            {
              "type": "text",
              "text": text
            },
            {
              "type": "image_url",
              "image_url": {
                "url": f"data:image/jpeg;base64,{base64_image}"
              }
            }
          ]
        }
      ],
      "max_tokens": 300
    }

    response = requests.post("https://api.openai.com/v1/chat/completions", headers=headers, json=payload)

    return response.json()
    

def generate_translation(text:str):
    completion:Translation = client.chat.completions.create(
        model = "gpt-4-0613",
        response_model = Translation,
        messages= [
            {
                "role":"system",
                "content":"You are a world class translation entity which excels in translating any given text to english. You are about to be given a chunk of text by a user to be translated into english. Make sure to do a great job and to return the translation in the specified format."
            },
            {
                "role":"user",
                "content":f"Please translate this - {text}"
            }
        ],
        max_retries=3
    )

    return completion.translation

def parse_user_command(text:str):
    completion:UserCommand = client.chat.completions.create(
        model = "gpt-4-0613",
        response_model = UserCommand,
        messages=[
            {
                "role":"system",
                "content":"""You are an expert at identifying what commands users want executed.

                Users always want to execute one of the following 2 commands
                1. Translate a foreign sentence into english
                2. Get their query answered
                """
            },
            {
                "role":"assistant",
                "content":"Remember if the request is not in english, assume that a translation needs to be done."
            },
            {
                "role":"assistant",
                "content":"Only answer queries that have been provided in english."
            },
            {
                "role":"user",
                "content":text
            }
        ],
        max_retries=3
    )
    return completion.command