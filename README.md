# Marginalia

Ask questions about any PDF and get answers that cite the page they came from.
Everything runs on your own computer: the PDF is read locally and a local
[Ollama](https://ollama.com) model writes the answer. No cloud key or internet API
is required while the app is running.

What you get:

- A hero section with an annotated page: highlighted answer, margin notes, page citations
- Upload a PDF and it is indexed automatically (pages, passages and word count shown)
- Answers stream in word by word
- The words from your question are highlighted in the passages the answer used
- One-click suggested questions, and a history of earlier answers
- Pick any installed Ollama model from the sidebar

---

## What you need to install

| # | Requirement | Version | Where to get it |
|---|-------------|---------|-----------------|
| 1 | Python | 3.10 or newer | https://www.python.org/downloads/ (tick **Add Python to PATH** on Windows) |
| 2 | Ollama | latest | https://ollama.com/download |
| 3 | An Ollama model | `llama3.2:latest` (about 2 GB) | `ollama pull llama3.2:latest` |
| 4 | Python packages | see `requirements.txt` | `pip install -r requirements.txt` |

The Python packages are only three:

| Package | Why it is needed |
|---------|------------------|
| `streamlit` | the web interface |
| `PyMuPDF` | reads text out of PDF files |
| `requests` | talks to Ollama on your machine |

Suggested hardware: 8 GB RAM is enough for `llama3.2`. A GPU is optional.

---

## Setup

### Windows (PowerShell)

Open PowerShell inside this folder, then run:

```powershell
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

Run `ollama pull llama3.2:latest` once while online to download the model. The
Python packages and model are then available for offline use.

If PowerShell blocks the activate script, run this once and try again:
`Set-ExecutionPolicy -Scope CurrentUser RemoteSigned`

### macOS / Linux

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
ollama pull llama3.2:latest
```

---

## Run it

1. Make sure Ollama is running. The Ollama desktop app on Windows and macOS starts it
   for you. If it is not running, open a terminal and run:

   ```powershell
   ollama serve
   ```

   If `ollama serve` says the address or port is already in use, Ollama is already
   running and you can continue.

2. In a second terminal, from this folder (with the virtual environment active):

   ```powershell
   python -m streamlit run app.py
   ```

3. Open http://localhost:8501 in your browser.

The hero shows a yellow dot and "Ollama is running on this computer" when everything
is connected.

After the Python packages and Ollama model have been downloaded once, the app can run
offline. Keep Ollama running locally; PDF reading, search, and answering use only your
computer. Internet access does not change the app behavior: online and offline runs
use the same local PDF and Ollama workflow.

---

## How to use it

1. Drop a PDF into **Add a PDF**. It is indexed automatically.
2. Click a suggested question, or type your own.
3. Click **Ask Marginalia**.
4. Open **Passages read** under the answer to see the exact text, with your words highlighted.

Use the sidebar to change the model, how many passages are read, and how creative the
model may be (keep it low so answers stay close to the PDF).

---

## Project files

```
app.py            the Streamlit interface
engine.py         PDF reading, BM25 passage ranking, Ollama calls (no UI code)
styles.py         colours, fonts and the hero section
requirements.txt  Python packages
.streamlit/config.toml   theme colours
```

## Colours

| Name | Hex | Used for |
|------|-----|----------|
| Ultramarine | `#3B36F5` | hero, buttons, numbers |
| Highlighter lemon | `#FFE14D` | highlighted text |
| Marker pink | `#FF5C93` | margin notes, page tags |
| Ink | `#14163A` | text |
| Paper | `#F1F3FF` | page background |

To rebrand, change these in `styles.py` (the `:root` block) and `.streamlit/config.toml`.

## Troubleshooting

| Problem | Fix |
|---------|-----|
| "Ollama is not running" | Start it with `ollama serve`, or open the Ollama app |
| "The model ... is not installed" | Run `ollama pull <model name>` |
| "No selectable text was found" | The PDF is a scan. Run OCR on it first, then upload the searchable file |
| "This PDF is password protected" | Remove the password, then upload again |
| `streamlit` is not recognised | Activate the virtual environment first |
| Answers are slow | Use a smaller model, or lower "Passages to read" in the sidebar |
| Fonts look plain | The app uses local system fonts and does not need an internet connection |
