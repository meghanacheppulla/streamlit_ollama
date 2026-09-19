from __future__ import annotations

import html

import requests
import streamlit as st

import engine
from styles import CSS, hero_html

st.set_page_config(page_title="Marginalia | Ask your PDF", page_icon="🖍️", layout="wide", initial_sidebar_state="auto")
st.markdown(CSS, unsafe_allow_html=True)

SUGGESTIONS = [
    "Summarize this document",
    "What are the key dates?",
    "Who is mentioned?",
    "What are the conclusions?",
]

for key, default in {"library": None, "source_key": None, "index_error": None, "history": [], "question": ""}.items():
    st.session_state.setdefault(key, default)


@st.cache_data(ttl=10, show_spinner=False)
def cached_models() -> list[str] | None:
    return engine.installed_models()


def use_suggestion(text: str) -> None:
    st.session_state.question = text
    st.session_state.auto_ask = True


def render_sources(passages, terms, matched, expanded):
    pages = ", ".join(str(p) for p in sorted({p.page for p in passages}))
    with st.expander(f"Passages read from pages {pages}", expanded=expanded):
        if not matched:
            st.markdown('<div class="hint">No passage matched your words directly, so Marginalia sampled pages across the document.</div>', unsafe_allow_html=True)
        rows = "".join(
            f'<div class="margin-note"><span class="pg">p. {p.page}</span>'
            f'<span class="txt">{engine.mark_terms(engine.snippet(p.text, terms), terms)}</span></div>'
            for p in passages
        )
        st.markdown(rows, unsafe_allow_html=True)


def render_question(text: str) -> None:
    st.markdown(f'<div class="asked"><span>You asked</span>{html.escape(text)}</div>', unsafe_allow_html=True)


# ---------- Sidebar ----------
models = cached_models()
with st.sidebar:
    st.markdown('<div class="side-title">Settings</div>', unsafe_allow_html=True)
    if models:
        model = st.selectbox("Model", models, index=models.index(engine.DEFAULT_MODEL) if engine.DEFAULT_MODEL in models else 0)
    else:
        model = st.text_input("Model", value=engine.DEFAULT_MODEL, help="Name of a model installed in Ollama.")
    top_k = st.slider("Passages to read", 3, 8, 5, help="More passages give the model more context but slow it down.")
    temperature = st.slider("Creativity", 0.0, 1.0, 0.1, 0.05, help="Keep this low so answers stay close to the PDF.")
    if st.button("Clear conversation", disabled=not st.session_state.history):
        st.session_state.history = []
        st.rerun()
    st.caption("Ollama must be running at 127.0.0.1:11434. Nothing is sent to the internet.")

# ---------- Hero ----------
st.markdown(hero_html(models is not None), unsafe_allow_html=True)

left, right = st.columns([1, 1.5], gap="large")

# ---------- Left: add a PDF ----------
with left:
    st.markdown('<div class="sec">Add a PDF</div>', unsafe_allow_html=True)
    uploaded = st.file_uploader("Upload a PDF", type=["pdf"], label_visibility="collapsed")

    if uploaded is None:
        st.session_state.update(library=None, source_key=None, index_error=None, history=[])
    else:
        source_key = (uploaded.name, uploaded.size)
        if source_key != st.session_state.source_key:
            with st.spinner("Reading pages and building the index..."):
                try:
                    st.session_state.library = engine.build_library(uploaded.name, uploaded.getvalue())
                    st.session_state.index_error = None
                except ValueError as error:
                    st.session_state.library = None
                    st.session_state.index_error = str(error)
            st.session_state.source_key = source_key
            st.session_state.history = []

    library = st.session_state.library
    if st.session_state.index_error:
        st.error(st.session_state.index_error)
    if library:
        st.markdown(
            f'<div class="stats"><div><b>{library.pages}</b><span>pages</span></div>'
            f'<div><b>{len(library.passages)}</b><span>passages</span></div>'
            f'<div><b>{library.words:,}</b><span>words</span></div></div>',
            unsafe_allow_html=True,
        )

# ---------- Right: ask ----------
with right:
    st.markdown('<div class="sec">Ask a question</div>', unsafe_allow_html=True)
    if not library:
        st.markdown(
            '<div class="empty"><b>Start with a PDF</b>Drop a file on the left. Marginalia indexes it in a few seconds, '
            'then you can ask anything about it.</div>',
            unsafe_allow_html=True,
        )
    else:
        chip_cols = st.columns(2)
        for i, suggestion in enumerate(SUGGESTIONS):
            chip_cols[i % 2].button(suggestion, key=f"chip{i}", on_click=use_suggestion, args=(suggestion,))
        st.text_area(
            "Your question", key="question", height=110, label_visibility="collapsed",
            placeholder="Ask anything, for example: What was decided on page 3?",
        )
        auto_ask = st.session_state.pop("auto_ask", False)
        ask = st.button("Ask Marginalia", type="primary", key="ask") or auto_ask
        just_answered = False

        if ask:
            question = st.session_state.question.strip()
            if not question:
                st.warning("Type a question first.")
            else:
                passages, terms, matched = engine.search(library, question, top_k)
                answer = None
                with st.container(border=True):
                    render_question(question)
                    try:
                        answer = st.write_stream(engine.stream_answer(engine.build_prompt(question, passages), model.strip() or engine.DEFAULT_MODEL, temperature))
                    except requests.exceptions.ConnectionError:
                        st.error("Ollama is not running. Open a terminal, run `ollama serve`, then ask again.")
                    except requests.exceptions.HTTPError as error:
                        if error.response is not None and error.response.status_code == 404:
                            st.error(f"The model `{model}` is not installed. Run `ollama pull {model}`, then ask again.")
                        else:
                            st.error(f"Ollama returned an error: {error}")
                    except (requests.RequestException, RuntimeError) as error:
                        st.error(f"Ollama could not answer: {error}")
                    if answer:
                        render_sources(passages, terms, matched, expanded=True)
                if answer:
                    st.session_state.history.insert(0, {"q": question, "a": answer, "passages": passages, "terms": terms, "matched": matched})
                    just_answered = True

        # Earlier answers (the newest one is already on screen if it was just streamed above)
        earlier = st.session_state.history[1:] if just_answered else st.session_state.history
        if earlier:
            st.markdown('<div class="hint">Earlier questions</div>', unsafe_allow_html=True)
        for entry in earlier:
            with st.container(border=True):
                render_question(entry["q"])
                st.markdown(entry["a"])
                render_sources(entry["passages"], entry["terms"], entry["matched"], expanded=False)

st.markdown('<div class="hint" style="margin-top:2rem">Marginalia runs on your machine: PDF reading and passage ranking happen in this app, and Ollama writes the answer locally.</div>', unsafe_allow_html=True)
