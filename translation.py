##########

# setting the enviroment
# you need to creaet I am user have a TranslateFullAccess polciy
# Create secrect %AWS_ACCESS_KEY_ID%  %AWS_SECRET_ACCESS_KEY%
# install aws cli with $sudo apt install awscli
# wriet aws configure in terminal
# will ask to set AWS_ACCESS_KEY_ID, set AWS_SECRET_ACCESS_KEY, set Default_region:"us-east-1", set output: "json"
# install boto3 to inailaize the service client $pip install boto3
### now you could run the code 

# setting aws cerdentail with .env
import os
from dotenv import load_dotenv
# Load environment variables from .env file
load_dotenv()
os.environ['AWS_CONFIG_FILE'] = ''
access_key = os.environ.get('AWS_ACCESS_KEY_ID')
secret_key = os.environ.get('AWS_SECRET_ACCESS_KEY')
region = os.environ.get('AWS_REGION')



import boto3
from translate import Translator
from langdetect import detect
def aws_translation(input_text):
    translate = boto3.client('translate', region_name='us-east-1')

    # Define the text to translate and the target language
    target_lang = 'en'

    # Call the translate_text method with automatic language detection
    response = translate.translate_text(
        Text=input_text,
        TargetLanguageCode=target_lang,
        SourceLanguageCode='auto'
    )

    # Print the input language and the translated text
    print(f"Detected input language: {response['SourceLanguageCode']}")
    print(f"Translated text: {response['TranslatedText']}")


def non_api_translation(input_text):
    language = detect(input_text)

    # Print the detected language code
    if language == "en":
        return input_text
    else:
        translator = Translator(from_lang=language, to_lang="en")
        # Translate a string from English to Spanish
        translation = translator.translate(input_text)
        #Print the translated string
        print(f"Detected input language: {language}")
        print(f"Translated text: {translation}")

if __name__ == "__main__":
    try:
        aws_translation("Je voudrais jouer avec Ahmed.")
    except Exception as e:
        non_api_translation("j'ai le pizza")
        