##########

# setting the enviroment
# you need to creaet I am user have a TranslateFullAccess polciy
# Create secrect %AWS_ACCESS_KEY_ID%  %AWS_SECRET_ACCESS_KEY%
# install aws cli with $sudo apt install awscli
# wriet aws configure in terminal
# will ask to set AWS_ACCESS_KEY_ID, set AWS_SECRET_ACCESS_KEY, set Default_region:"us-east-1", set output: "json"
# install boto3 to inailaize the service client $pip install boto3
### now you could run the code 

import boto3

translate = boto3.client('translate', region_name='us-east-1')

# Define the text to translate and the target language
text = 'Hello, how are you? I hope you are doing well'
target_lang = 'fr'

# Call the translate_text method with automatic language detection
response = translate.translate_text(
    Text=text,
    TargetLanguageCode=target_lang,
    SourceLanguageCode='auto'
)

# Print the input language and the translated text
print(f"Detected input language: {response['SourceLanguageCode']}")
print(f"Translated text: {response['TranslatedText']}")
