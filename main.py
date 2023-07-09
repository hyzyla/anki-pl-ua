import hashlib
import html
import json
import pathlib

import genanki

from speech import TextToSpeechClient

OUTPUT_FOLDER = "output"
OUTPUT_AUDIO_FOLDER = pathlib.Path(f"{OUTPUT_FOLDER}/audio")
TTS_CREDENTIALS = "./credentials.json"

if not OUTPUT_AUDIO_FOLDER.exists():
    OUTPUT_AUDIO_FOLDER.mkdir(parents=True)

tts_client = TextToSpeechClient(config=TTS_CREDENTIALS)


class Model(genanki.Model):
    @property
    def guid(self):
        # We use "CID" for generating the GUID because it's the only field
        # that is guaranteed to be unique.
        return genanki.guid_for(self.fields[0])


# Create deck (where we will put all the notes).
deck = genanki.Deck(
    deck_id=1426754026,
    name="PL-UA Deck",
)

# Create model (how the notes will look like).
model = Model(
    model_id=1864309187,
    name="PL-UA Model",
    fields=[
        # Unique ID for the note.
        {"name": "CID"},
        # Polish word.
        {"name": "PL"},
        # Ukrainian translation.
        {"name": "UA"},
        # Examples in Polish.
        {"name": "EXAMPLES"},
        # Generated audio for the examples.
        {"name": "AUDIO"},
    ],
    templates=[
        # First template: Polish word -> Ukrainian translation.
        {
            "name": "UA -> PL",
            "qfmt": "{{UA}}",
            "afmt": (
                "{{FrontSide}}"
                '<hr id="answer" />'
                "<b>{{PL}}</b>"
                "<br />"
                "<br />"
                "{{EXAMPLES}}"
                "<br />"
                "<br />"
                "{{AUDIO}}"
            ),
        },
        # Second template: Ukrainian translation -> Polish word.
        {
            "name": "PL -> UA",
            "qfmt": "{{PL}}",
            "afmt": (
                "{{FrontSide}}"
                '<hr id="answer" />'
                "<b>{{UA}}</b>"
                "<br />"
                "<br />"
                "{{EXAMPLES}}"
            ),
        },
    ],
)

# Load the notes from a JSON file.
with open("notes.json", "r") as f:
    data = json.load(f)

seen_ids = set()
media_files = []
# Create a new note for each note in the JSON file.
for note in data:
    id_field = note["id"]
    if id_field in seen_ids:
        raise ValueError(f"Duplicate ID: {id_field}")
    seen_ids.add(id_field)

    # Escape HTML characters in the fields to avoid rendering issues.
    pl_filed = html.escape(note["pl"])
    ua_filed = html.escape(note["ua"])

    # Examples should be always as a list
    examples = note["examples"]
    if not isinstance(examples, list):
        raise ValueError(f"Examples is not a list: {examples}")

    # Create <ul></ul> list with examples
    examples = [html.escape(example) for example in examples]
    examples = [f"<li>{example}</li>" for example in examples]
    examples_field = f"<ul>{''.join(examples)}</ul>"

    # Generate audio for the examples. Ouput should be in ouput/audio folder
    # and each file should be named as the note ID + hash of the example.
    # If the file already exists, we don't generate it again.
    audio_field = ""
    for example in note["examples"]:
        audio_hash = hashlib.md5(example.encode("utf-8")).hexdigest()
        audio_filname = f"{id_field}_{audio_hash}.mp3"
        audio_path = pathlib.Path(f"{OUTPUT_AUDIO_FOLDER}/{audio_filname}")
        if not audio_path.exists():
            audio = tts_client.generate_audio(example)
            audio_path.write_bytes(audio)

        media_files.append(audio_path)
        audio_field += f"[sound:{audio_filname}]"

    print(
        "Adding note: \n"
        f"  ID: {id_field}\n"
        f"  PL: {pl_filed}\n"
        f"  UA: {ua_filed}\n"
        f"  Examples: {examples_field}\n"
        f"  Audio: {audio_field}\n"
    )

    note = genanki.Note(
        model=model,
        fields=[
            id_field,
            pl_filed,
            ua_filed,
            examples_field,
            audio_field,
        ],
    )

    deck.add_note(note)

# Save the deck to a file.
pacakge = genanki.Package(deck)
pacakge.media_files = media_files
pacakge.write_to_file(f"{OUTPUT_FOLDER}/plua.apkg")
