import html
import json

import genanki


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
# Create a new note for each note in the JSON file.
for note in data:
    # Escape HTML characters in the fields to avoid rendering issues.
    pl_filed = html.escape(note["pl"])
    ua_filed = html.escape(note["ua"])
    id_field = note["id"]

    # Examples should be always as a list
    examples = note["examples"]
    if not isinstance(examples, list):
        raise ValueError(f"Examples is not a list: {examples}")

    # Create <ul></ul> list with examples
    examples = [html.escape(example) for example in examples]
    examples = [f"<li>{example}</li>" for example in examples]
    examples_field = f"<ul>{''.join(examples)}</ul>"

    if id_field in seen_ids:
        raise ValueError(f"Duplicate ID: {id_field}")
    seen_ids.add(id_field)

    print(
        "Adding note: \n"
        f"  ID: {id_field}\n"
        f"  PL: {pl_filed}\n"
        f"  UA: {ua_filed}\n"
        f"  Examples: {examples_field}\n"
    )

    note = genanki.Note(
        model=model,
        fields=[
            id_field,
            pl_filed,
            ua_filed,
            examples_field,
        ],
    )

    deck.add_note(note)

# Save the deck to a file.
genanki.Package(deck).write_to_file("output/plua.apkg")
