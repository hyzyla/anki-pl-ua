import json
from dataclasses import dataclass
from pathlib import Path

import genanki

DATA_PATH = Path("./movapp-data/data")
DICTIONARY_PATH = Path(DATA_PATH) / "uk-pl-dictionary.json"

PL_SOUNDS_PATH = DATA_PATH / "pl-sounds"

dictionary = json.loads(DICTIONARY_PATH.read_text())


class AnkiModel(genanki.Model):
    @property
    def guid(self):
        # We use "CID" for generating the GUID because it's the only field
        # that is guaranteed to be unique.
        return genanki.guid_for(self.fields[0])


@dataclass
class Phrase:
    id: str
    uk_text: str
    pl_text: str
    pl_sound_path: Path

    def __str__(self):
        return f"{self.uk_text} - {self.pl_text}"


def generate_anki(phrases: list[Phrase]):
    # Create deck (where we will put all the notes).
    deck = genanki.Deck(
        deck_id=1426754026,
        name="Polish-Ukrainian Movapp Deck",
    )

    # Create model (how the notes will look like).
    model = AnkiModel(
        model_id=4864239187,
        name="Polish-Ukrainian Movapp Model",
        fields=[
            # Unique ID for the note.
            {"name": "CID"},
            # Polish word.
            {"name": "PL"},
            # Ukrainian translation.
            {"name": "UA"},
            # Generated audio for the examples.
            {"name": "AUDIO"},
        ],
        templates=[
            # Ukrainian world -> Polish translation.
            {
                "name": "UA -> PL",
                "qfmt": "{{UA}}",
                "afmt": (
                    "{{FrontSide}}"
                    '<hr id="answer" />'
                    "<b>{{PL}}</b>"
                    "<br />"
                    "<br />"
                    "{{AUDIO}}"
                ),
            },
        ],
    )

    media_files = []

    for phrase in phrases:
        audio_field = f"[sound:{phrase.pl_sound_path.name}]"
        media_files.append(str(phrase.pl_sound_path))
        note = genanki.Note(
            model=model,
            fields=[
                phrase.id,
                phrase.pl_text,
                phrase.uk_text,
                audio_field,
            ],
        )

        deck.add_note(note)

    # Save the deck to a file.
    pacakge = genanki.Package(deck)
    pacakge.media_files = media_files
    pacakge.write_to_file("../output/plua-movapp.apkg")


def main():
    categories = dictionary["categories"]
    phrases = dictionary["phrases"]
    phrases_obj = []
    for category in categories:
        for phrase_id in category["phrases"]:
            phrase = phrases[phrase_id]
            pl_sound_url: str = phrase["main"]["sound_url"]
            pl_sound_url = pl_sound_url.removeprefix(
                "https://data.movapp.eu/pl-sounds/"
            )
            pl_sound_path = PL_SOUNDS_PATH / pl_sound_url
            if phrase["image_url"]:
                print(phrase["image_url"])
            phrase_obj = Phrase(
                id=phrase_id,
                uk_text=phrase["source"]["translation"],
                pl_text=phrase["main"]["translation"],
                pl_sound_path=pl_sound_path,
            )
            phrases_obj.append(phrase_obj)

    generate_anki(phrases_obj)


if __name__ == "__main__":
    main()
