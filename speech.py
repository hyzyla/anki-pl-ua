from google.cloud import texttospeech
from google.oauth2 import service_account


class TextToSpeechClient:
    """Generate audio from text using Google Cloud Text-to-Speech API."""

    def __init__(self, config: str) -> None:
        credentials = service_account.Credentials.from_service_account_file(config)
        self.client = texttospeech.TextToSpeechClient(credentials=credentials)

    def generate_audio(self, text: str) -> bytes:
        # Set the text input to be synthesized
        synthesis_input = texttospeech.SynthesisInput(text=text)

        # Build the voice request, select the language code and the ssml
        # voice gender
        voice = texttospeech.VoiceSelectionParams(
            language_code="pl-PL",
            ssml_gender=texttospeech.SsmlVoiceGender.MALE,
        )

        # Select the type of audio file you want returned
        audio_config = texttospeech.AudioConfig(
            audio_encoding=texttospeech.AudioEncoding.MP3
        )

        # Perform the text-to-speech request on the text input with the selected
        # voice parameters and audio file type
        response = self.client.synthesize_speech(
            input=synthesis_input,
            voice=voice,
            audio_config=audio_config,
        )
        return response.audio_content
