import logging
from dotenv import load_dotenv

from helpers.gpt import (
    ask_gpt4_with_image,
    ask_gpt_4_vanilla,
    generate_translation,
    parse_user_command,
    text_to_speech,
)
from helpers.image import get_user_webcam_image
from helpers.models.Command import Translation
from helpers.sound import get_user_preference, record_user_audio, transcribe_audio

load_dotenv()

# Initialize logging
logging.basicConfig(level=logging.INFO)



def main():
    logging.info("Starting up Ailene now....")
    device = get_user_preference()
    transcription_file = record_user_audio(device)
    transcription = transcribe_audio(transcription_file)
    logging.info(f"Generated transcription of {transcription}")

    # TODO : Need to add in some loops so that if the user doesn't provide enough information, we can go perform a query. Idea here is an Arxiv scrapper database ( with metadata and linked papers ) AND a metaphor search integration + maybe other popular blogs and stuff I've saved that don't have a strong bot detection algo.

    command = parse_user_command(text=transcription)

    if not command.result:
        logging.info("Unable to determine that user is requesting for. TODO: Ask more questions(not implemented)")
        return
    
    response = None
    if isinstance(command.result,Translation):
        logging.info("User requesting a translation")
        response = generate_translation(transcription)        
    else:
        logging.info("User making a query")
        image_path = get_user_webcam_image()
        if not image_path:
            response = ask_gpt_4_vanilla(transcription)
        else:
            response = ask_gpt4_with_image(
                image_path,
                transcription
            )
        logging.info(f"Generated a response of {response}")
    # Now we generate audio response
    text_to_speech(response)

if __name__ == "__main__":
    main()