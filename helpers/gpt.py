from instructor import patch
from openai import OpenAI
import requests
import os
from helpers.files import generate_datecoded_filename
from helpers.image import encode_image
from helpers.models.Command import MaybeUserCommand, Translation
from dotenv import load_dotenv
from playsound import playsound
load_dotenv()
client = patch(OpenAI())


command_prompt = """
You are categorizing the Question in the context into one of the following commands. 

1. Translation: A translation request or a non-english sentence
2. Query: A clearly defined question that needs to be answered

Make sure to adhere to the requested response format. If you are unsure of the exact command to classify the question into, do not return a result and instead return an error message explaning why you are unable to do so in the requested format.
"""

def strip_identation(text:str):
    return text.strip()


def parse_user_command(text:str) -> MaybeUserCommand:
    completion:MaybeUserCommand = client.chat.completions.create(
        model = "gpt-4-0613",
        response_model = MaybeUserCommand,
        messages=[
            {
                "role":"system",
                "content":strip_identation(command_prompt)
            },
            {
                "role":"user",
                "content":text
            }
        ],
        max_retries=3
    )
    return completion

def text_to_speech(text:str):
    filename = generate_datecoded_filename("response","mp3")
    
    response = client.audio.speech.create(
        model="tts-1",
        voice="shimmer",
        input=text
    )
    
    with open(filename, "wb") as f:
        f.write(response.content)
    playsound(filename)
    return filename

    

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

    assert response.status_code == 200, f"Encountered error making GPT4-V API Call - {response.reason}"

    result = response.json()

    return result["choices"][0]["message"]["content"]
    

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
                "role":"assistant",
                "content":"Make sure to ignore any filler words that do not contribute to the sentence. Eg. Can you translate this for me ... (rest of sentence). In such a case you would not translate the phrase `Can you translate this for me`."
            },
            {
                "role":"user",
                "content":f"Please translate this - {text}"
            }
        ],
        max_retries=3
    )

    return completion.translation