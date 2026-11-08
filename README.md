# deepdict-anki

A tiny German ⇄ Chinese command-line dictionary powered by the DeepSeek API.
Every word you look up is also saved to a file that Anki can import, so you can review your lookups as flashcards.

- **German → Chinese** and **Chinese → German**, detected automatically
- **Words**: a one-line definition. Nouns include their article and plural, verbs their past tense and past participle. A short example sentence with its translation comes last.
- **Sentences**: only the translation
- **Anki export**: words go into `anki/deepdict.txt`. Sentences and repeat lookups are skipped.

## Setup

Requires Python 3.8+.

```bash
pip install openai python-dotenv
```

Create a `.env` file next to `Deepdict.py`:

```
DEEPSEEK_API_KEY=your-key-here
```

The key is loaded from the script's own folder, so the tool works from any working directory.

## Usage

Look up a single word or sentence:

```bash
python Deepdict.py Haus
```

```
das Haus, die Häuser：房子
Das Haus ist groß. 这房子很大。
```

Run it with no arguments for interactive mode. Type one query per line, and press `Ctrl+Z` then `Enter` (Windows) or `Ctrl+D` (macOS/Linux) to quit:

```bash
python Deepdict.py
```

On Windows, `Deepdict.bat` wraps the script. Put this folder on your `PATH` and you can run `deepdict Haus` from anywhere. It finds `Deepdict.py` relative to its own location, so it keeps working if you move or clone the project.

## Anki export

Each word lookup is appended to `anki/deepdict.txt`. The folder and file are created on the first save. The file is tab-separated, UTF-8, and starts with Anki header lines:

```
#separator:tab
#html:true
#notetype:Basic
#deck:Deutsch::Deepdict
#tags column:3
Haus	das Haus, die Häuser：房子<br>Das Haus ist groß. 这房子很大。	deepdict
```

| Field | Content |
|-------|---------|
| Front | Your query, exactly as typed (with extra whitespace collapsed) |
| Back  | The dictionary result, with line breaks turned into `<br>` |
| Tags  | `deepdict` |

**What gets saved**

- **Sentences are skipped.** A query counts as a sentence if it contains punctuation (`. ! ? , ; :` or the Chinese equivalents), has more than 3 words, or has more than 8 Chinese characters. Short phrases such as `das Haus` or `sich freuen` are still saved.
- **Duplicates are skipped.** A query is skipped if the same Front already exists in the file. The check is case-sensitive, so `Essen` and `essen` are different entries.

### Importing into Anki

1. In Anki, choose **File → Import** and select `anki/deepdict.txt`.
2. The header lines set the note type, deck (`Deutsch::Deepdict`), and tags for you. Set **Existing notes** to **Preserve**.
3. Click **Import**.

You don't need to empty the file after importing. When you re-import the growing file, Anki matches notes by their first field and leaves cards you are already studying untouched.

## Configuration

These live at the top of `Deepdict.py`:

- `SYSTEM`: the prompt that sets the output format
- `model`: the DeepSeek model, `deepseek-flash` by default
- `ANKI_FILE` / `ANKI_HEADER`: where the export goes, plus the deck and note type
- `is_sentence()`: the rule that separates words from sentences
