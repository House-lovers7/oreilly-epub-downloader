#!/usr/bin/env python3
"""Build an English learning corpus (frequency stats + example sentences)
from the O'Reilly EPUB library under downloads/.

Standard library only (zipfile, html.parser, xml.etree.ElementTree, re,
collections, json, math, pathlib). No third-party dependencies.

Outputs (all under knowledge-base/english-corpus/data/):
    books.tsv      title, filename, included, reason, tokens, en_ratio
    words.tsv      word, freq, doc_freq, per_million
    bigrams.tsv    ngram, freq, doc_freq, log_dice
    trigrams.tsv   ngram, freq, doc_freq
    sentences.jsonl  example-sentence index for high-signal words/n-grams
"""

from __future__ import annotations

import json
import math
import re
import sys
import xml.etree.ElementTree as ET
import zipfile
from collections import Counter
from html.parser import HTMLParser
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
DOWNLOADS_DIR = REPO_ROOT / "downloads"
OUT_DIR = REPO_ROOT / "knowledge-base" / "english-corpus" / "data"

# ---------------------------------------------------------------------------
# Constants / lexical resources
# ---------------------------------------------------------------------------

SKIP_NAME_KEYWORDS = (
    "nav",
    "toc",
    "index",
    "cover",
    "copyright",
    "colophon",
    "titlepage",
)

CONTENT_EXTENSIONS = (".xhtml", ".html", ".htm")

SKIP_TAGS = {"pre", "code", "script", "style"}

BLOCK_TAGS = {
    "p",
    "div",
    "li",
    "h1",
    "h2",
    "h3",
    "h4",
    "h5",
    "h6",
    "br",
    "tr",
    "table",
    "blockquote",
    "section",
    "article",
    "header",
    "footer",
    "ul",
    "ol",
    "dd",
    "dt",
    "figcaption",
    "figure",
}

EN_FUNCTION_WORDS = {
    "the", "of", "and", "a", "to", "in", "is", "that", "it", "for", "as",
    "with", "on", "be", "this", "are", "or", "by", "from", "at", "an",
    "we", "can", "will", "not", "have", "but", "you", "if", "which",
    "when", "more", "one", "all", "use", "each", "their", "has", "its",
    "also", "how", "other",
}

FR_FUNCTION_WORDS = {
    "le", "la", "les", "des", "du", "une", "est", "dans", "pour", "que",
    "qui", "nous", "vous", "avec", "sur", "pas", "plus", "par", "ce",
    "cette", "sont", "comme", "mais",
    # "etre" (être) is dropped: the ASCII-only TOKEN_RE strips the accented
    # "e" so the tokenizer actually emits "tre", not "etre"; keeping a form
    # that can never match would just be dead weight.
    "tre",
}

CJK_RE = re.compile(r"[぀-ヿ一-鿿＀-￯]")
TOKEN_RE = re.compile(r"[a-z][a-z'-]*[a-z]|[a-z]")
SENTENCE_SPLIT_RE = re.compile(r"(?<=[.!?])\s+(?=[A-Z\"'(])")
ALNUM_SPACE_RE = re.compile(r"[A-Za-z0-9\s]")

# Typographic-character normalization applied to full book text before any
# tokenization/sentence-splitting. Curly quotes -> straight quotes; em/en
# dash -> space-padded hyphen (acts as a word separator). Without this,
# curly apostrophes (U+2019) fall outside TOKEN_RE's [a-z'-] class and
# contractions like "it's"/"don't" get split into "it"+"s", "don"+"t".
TYPOGRAPHY_MAP = {
    "’": "'",  # RIGHT SINGLE QUOTATION MARK
    "‘": "'",  # LEFT SINGLE QUOTATION MARK
    "“": '"',  # LEFT DOUBLE QUOTATION MARK
    "”": '"',  # RIGHT DOUBLE QUOTATION MARK
    "—": " - ",  # EM DASH
    "–": " - ",  # EN DASH
}
TYPOGRAPHY_TABLE = str.maketrans(TYPOGRAPHY_MAP)

# Publisher boilerplate (colophon/credits/legal notices) that leaks into
# chapter body files and isn't caught by the filename-level skip list.
# Sentences containing any of these markers (case-insensitive substring)
# are dropped from both frequency stats and the example-sentence index.
BOILERPLATE_MARKERS = (
    "o'reilly",
    "oreil",
    "gravenstein",
    "sebastopol",
    "karen montgomery",
    "kate dullea",
    "errata",
    "registered trademark",
    "all rights reserved",
    "permissions@",
    "978-1-",
    "cover illustration",
    # Added beyond the original 11-marker list: this exact recurring O'Reilly
    # legal-disclaimer sentence ("...it is your responsibility to ensure
    # that your use thereof complies with such licenses and/or rights.")
    # appears verbatim across 18+ books and contains none of the markers
    # above, yet its removal was an explicitly named expected outcome.
    "thereof complies",
)

CJK_THRESHOLD = 0.03
EN_RATIO_THRESHOLD = 0.25
FR_MULTIPLIER = 2.0

WORD_MIN_FREQ = 10
BIGRAM_MIN_FREQ = 15
TRIGRAM_MIN_FREQ = 10

SENTENCE_MIN_LEN = 40
SENTENCE_MAX_LEN = 220
SENTENCE_MAX_SYMBOL_RATIO = 0.15
SENTENCE_MAX_PER_KEY = 3

WORD_KEY_MIN_FREQ = 50
WORD_KEY_MIN_DOC_FREQ = 8
BIGRAM_KEY_MIN_DOC_FREQ = 8
TRIGRAM_KEY_MIN_DOC_FREQ = 8


# ---------------------------------------------------------------------------
# HTML text extraction
# ---------------------------------------------------------------------------


class BodyTextExtractor(HTMLParser):
    """Extract visible text, dropping pre/code/script/style content and
    inserting newlines at block-element boundaries."""

    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self._skip_depth = 0
        self._parts: list[str] = []

    def handle_starttag(self, tag: str, attrs) -> None:  # noqa: ANN001
        tag = tag.lower()
        if tag in SKIP_TAGS:
            self._skip_depth += 1
        elif tag in BLOCK_TAGS and self._skip_depth == 0:
            self._parts.append("\n")

    def handle_startendtag(self, tag: str, attrs) -> None:  # noqa: ANN001
        tag = tag.lower()
        if tag in BLOCK_TAGS and self._skip_depth == 0:
            self._parts.append("\n")

    def handle_endtag(self, tag: str) -> None:
        tag = tag.lower()
        if tag in SKIP_TAGS:
            if self._skip_depth > 0:
                self._skip_depth -= 1
        elif tag in BLOCK_TAGS and self._skip_depth == 0:
            self._parts.append("\n")

    def handle_data(self, data: str) -> None:
        if self._skip_depth == 0 and data:
            self._parts.append(data)

    def get_text(self) -> str:
        return "".join(self._parts)


def extract_title(zf: zipfile.ZipFile, fallback: str) -> str:
    try:
        container = zf.read("META-INF/container.xml")
        croot = ET.fromstring(container)
        ns = {"c": "urn:oasis:names:tc:opendocument:xmlns:container"}
        rootfile = croot.find(".//c:rootfile", ns)
        if rootfile is None:
            return fallback
        opf_path = rootfile.get("full-path")
        if not opf_path:
            return fallback
        opf_data = zf.read(opf_path)
        oroot = ET.fromstring(opf_data)
        dc_ns = {"dc": "http://purl.org/dc/elements/1.1/"}
        title_el = oroot.find(".//dc:title", dc_ns)
        if title_el is not None and title_el.text and title_el.text.strip():
            return " ".join(title_el.text.strip().split())
    except Exception:
        pass
    return fallback


def extract_book_text(epub_path: Path) -> tuple[str, str]:
    """Return (full_text, title) for one EPUB. Raises on unreadable zip."""
    with zipfile.ZipFile(epub_path) as zf:
        title = extract_title(zf, fallback=epub_path.stem)
        names = sorted(zf.namelist())
        text_parts: list[str] = []
        for name in names:
            lower = name.lower()
            if not lower.endswith(CONTENT_EXTENSIONS):
                continue
            if any(kw in lower for kw in SKIP_NAME_KEYWORDS):
                continue
            try:
                raw = zf.read(name)
            except Exception:
                continue
            html_text = raw.decode("utf-8", errors="replace")
            parser = BodyTextExtractor()
            try:
                parser.feed(html_text)
                parser.close()
            except Exception:
                continue
            text_parts.append(parser.get_text())
        full_text = "\n".join(text_parts)
    return full_text, title


# ---------------------------------------------------------------------------
# Language gate + tokenization
# ---------------------------------------------------------------------------


def cjk_ratio(text: str) -> float:
    non_ws = sum(1 for ch in text if not ch.isspace())
    if non_ws == 0:
        return 0.0
    cjk = len(CJK_RE.findall(text))
    return cjk / non_ws


def tokenize_blocks(blocks: list[str]) -> list[list[str]]:
    return [TOKEN_RE.findall(block.lower()) for block in blocks]


def function_word_ratios(tokens: list[str]) -> tuple[float, float]:
    if not tokens:
        return 0.0, 0.0
    total = len(tokens)
    en_count = sum(1 for t in tokens if t in EN_FUNCTION_WORDS)
    fr_count = sum(1 for t in tokens if t in FR_FUNCTION_WORDS)
    return en_count / total, fr_count / total


def classify_book(text: str, tokens: list[str]) -> tuple[bool, str, float]:
    """Return (included, reason, en_ratio)."""
    c_ratio = cjk_ratio(text)
    if c_ratio > CJK_THRESHOLD:
        en_r, _ = function_word_ratios(tokens)
        return False, "japanese", round(en_r, 4)

    en_r, fr_r = function_word_ratios(tokens)
    # French books have a very low en_ratio too, so the french-specific
    # relative check must run before the generic low-english floor,
    # otherwise every french book is mislabeled as low_english_ratio.
    if en_r < FR_MULTIPLIER * fr_r:
        return False, "french", round(en_r, 4)
    if en_r < EN_RATIO_THRESHOLD:
        return False, "low_english_ratio", round(en_r, 4)
    return True, "ok", round(en_r, 4)


def sentence_ok(sentence: str) -> bool:
    length = len(sentence)
    if length < SENTENCE_MIN_LEN or length > SENTENCE_MAX_LEN:
        return False
    alnum_space = len(ALNUM_SPACE_RE.findall(sentence))
    symbol_ratio = 1.0 - (alnum_space / length)
    return symbol_ratio <= SENTENCE_MAX_SYMBOL_RATIO


def normalize_typography(text: str) -> str:
    return text.translate(TYPOGRAPHY_TABLE)


def is_boilerplate(sentence: str) -> bool:
    low = sentence.lower()
    return any(marker in low for marker in BOILERPLATE_MARKERS)


# ---------------------------------------------------------------------------
# Main pipeline
# ---------------------------------------------------------------------------


def main() -> int:
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    epub_paths = sorted(DOWNLOADS_DIR.glob("*.epub"), key=lambda p: p.name)
    print(f"[build_english_corpus] found {len(epub_paths)} epub files", file=sys.stderr)

    book_rows: list[dict] = []

    word_freq: Counter[str] = Counter()
    word_doc_freq: Counter[str] = Counter()
    bigram_freq: Counter[str] = Counter()
    bigram_doc_freq: Counter[str] = Counter()
    trigram_freq: Counter[str] = Counter()
    trigram_doc_freq: Counter[str] = Counter()

    total_corpus_tokens = 0
    # sentences kept only for included books, used in the second pass
    included_book_sentences: list[tuple[str, list[str]]] = []

    for i, epub_path in enumerate(epub_paths, start=1):
        filename = epub_path.name
        print(f"[{i}/{len(epub_paths)}] {filename}", file=sys.stderr)
        try:
            full_text, title = extract_book_text(epub_path)
        except Exception as exc:  # noqa: BLE001 - record and continue
            print(f"  parse_error: {exc}", file=sys.stderr)
            book_rows.append(
                {
                    "title": epub_path.stem,
                    "filename": filename,
                    "included": False,
                    "reason": "parse_error",
                    "tokens": 0,
                    "en_ratio": 0.0,
                }
            )
            continue

        full_text = normalize_typography(full_text)
        blocks = full_text.split("\n")

        # Book-level classification uses all extracted text/tokens
        # unfiltered by the boilerplate blacklist (the gate decision should
        # not depend on whether a paragraph happens to mention "O'Reilly").
        block_tokens = tokenize_blocks(blocks)
        all_tokens = [tok for toks in block_tokens for tok in toks]

        included, reason, en_r = classify_book(full_text, all_tokens)
        book_rows.append(
            {
                "title": title,
                "filename": filename,
                "included": included,
                "reason": reason,
                "tokens": len(all_tokens),
                "en_ratio": en_r,
            }
        )

        if not included:
            continue

        # Stats + example sentences: sentence-granularity, with boilerplate
        # sentences dropped from *both* so the same filter governs what
        # counts as corpus signal and what can be surfaced as an example.
        book_word_freq: Counter[str] = Counter()
        book_bigrams: Counter[str] = Counter()
        book_trigrams: Counter[str] = Counter()
        book_sentence_candidates: list[str] = []
        book_stat_tokens = 0

        for block in blocks:
            block = block.strip()
            if not block:
                continue
            for raw_sentence in SENTENCE_SPLIT_RE.split(block):
                sentence = raw_sentence.strip()
                if not sentence or is_boilerplate(sentence):
                    continue
                toks = TOKEN_RE.findall(sentence.lower())
                if toks:
                    book_stat_tokens += len(toks)
                    for t in toks:
                        book_word_freq[t] += 1
                    for j in range(len(toks) - 1):
                        book_bigrams[f"{toks[j]} {toks[j + 1]}"] += 1
                    for j in range(len(toks) - 2):
                        book_trigrams[f"{toks[j]} {toks[j + 1]} {toks[j + 2]}"] += 1
                if sentence_ok(sentence):
                    book_sentence_candidates.append(sentence)

        total_corpus_tokens += book_stat_tokens

        word_freq.update(book_word_freq)
        word_doc_freq.update(book_word_freq.keys())
        bigram_freq.update(book_bigrams)
        bigram_doc_freq.update(book_bigrams.keys())
        trigram_freq.update(book_trigrams)
        trigram_doc_freq.update(book_trigrams.keys())

        included_book_sentences.append((title, book_sentence_candidates))

    # -- books.tsv --------------------------------------------------------
    book_rows_sorted = sorted(book_rows, key=lambda r: r["filename"])
    books_tsv = OUT_DIR / "books.tsv"
    with books_tsv.open("w", encoding="utf-8") as f:
        f.write("title\tfilename\tincluded\treason\ttokens\ten_ratio\n")
        for r in book_rows_sorted:
            title_clean = " ".join(str(r["title"]).split())
            f.write(
                f"{title_clean}\t{r['filename']}\t"
                f"{'true' if r['included'] else 'false'}\t{r['reason']}\t"
                f"{r['tokens']}\t{r['en_ratio']:.4f}\n"
            )

    included_count = sum(1 for r in book_rows if r["included"])
    excluded_by_reason: Counter[str] = Counter(
        r["reason"] for r in book_rows if not r["included"]
    )
    print(
        f"[build_english_corpus] included={included_count} "
        f"excluded={dict(excluded_by_reason)}",
        file=sys.stderr,
    )

    # -- words.tsv ----------------------------------------------------------
    word_rows = []
    for word, freq in word_freq.items():
        if freq < WORD_MIN_FREQ:
            continue
        doc_freq = word_doc_freq[word]
        per_million = (
            (freq / total_corpus_tokens) * 1_000_000 if total_corpus_tokens else 0.0
        )
        word_rows.append((word, freq, doc_freq, round(per_million, 2)))
    word_rows.sort(key=lambda r: (-r[1], r[0]))

    words_tsv = OUT_DIR / "words.tsv"
    with words_tsv.open("w", encoding="utf-8") as f:
        f.write("word\tfreq\tdoc_freq\tper_million\n")
        for word, freq, doc_freq, per_million in word_rows:
            f.write(f"{word}\t{freq}\t{doc_freq}\t{per_million:.2f}\n")

    # -- bigrams.tsv (log_dice uses *unfiltered* global unigram freqs) -----
    def log_dice(xy_freq: int, x: str, y: str) -> float:
        fx = word_freq.get(x, 0)
        fy = word_freq.get(y, 0)
        denom = fx + fy
        if denom == 0 or xy_freq == 0:
            return float("-inf")
        return 14 + math.log2((2 * xy_freq) / denom)

    bigram_rows = []
    for ngram, freq in bigram_freq.items():
        if freq < BIGRAM_MIN_FREQ:
            continue
        w1, w2 = ngram.split(" ", 1)
        doc_freq = bigram_doc_freq[ngram]
        ld = log_dice(freq, w1, w2)
        bigram_rows.append((ngram, freq, doc_freq, round(ld, 3)))
    bigram_rows.sort(key=lambda r: (-r[3], r[0]))

    bigrams_tsv = OUT_DIR / "bigrams.tsv"
    with bigrams_tsv.open("w", encoding="utf-8") as f:
        f.write("ngram\tfreq\tdoc_freq\tlog_dice\n")
        for ngram, freq, doc_freq, ld in bigram_rows:
            f.write(f"{ngram}\t{freq}\t{doc_freq}\t{ld:.3f}\n")

    # -- trigrams.tsv --------------------------------------------------------
    trigram_rows = []
    for ngram, freq in trigram_freq.items():
        if freq < TRIGRAM_MIN_FREQ:
            continue
        doc_freq = trigram_doc_freq[ngram]
        trigram_rows.append((ngram, freq, doc_freq))
    trigram_rows.sort(key=lambda r: (-r[1], r[0]))

    trigrams_tsv = OUT_DIR / "trigrams.tsv"
    with trigrams_tsv.open("w", encoding="utf-8") as f:
        f.write("ngram\tfreq\tdoc_freq\n")
        for ngram, freq, doc_freq in trigram_rows:
            f.write(f"{ngram}\t{freq}\t{doc_freq}\n")

    # -- sentences.jsonl ------------------------------------------------------
    target_words = {
        word
        for word, freq, doc_freq, _pm in word_rows
        if freq >= WORD_KEY_MIN_FREQ and doc_freq >= WORD_KEY_MIN_DOC_FREQ
    }
    target_bigrams = {
        ngram
        for ngram, _freq, doc_freq, _ld in bigram_rows
        if doc_freq >= BIGRAM_KEY_MIN_DOC_FREQ
    }
    target_trigrams = {
        ngram
        for ngram, _freq, doc_freq in trigram_rows
        if doc_freq >= TRIGRAM_KEY_MIN_DOC_FREQ
    }

    # candidates[(type, key)] = {book_title: sentence_text}, insertion-ordered
    candidates: dict[tuple[str, str], dict[str, str]] = {}

    for title, sentences in included_book_sentences:
        for sentence in sentences:
            toks = TOKEN_RE.findall(sentence.lower())
            if not toks:
                continue
            seen_words = set(toks) & target_words
            seen_bigrams = {
                f"{toks[j]} {toks[j + 1]}"
                for j in range(len(toks) - 1)
            } & target_bigrams
            seen_trigrams = {
                f"{toks[j]} {toks[j + 1]} {toks[j + 2]}"
                for j in range(len(toks) - 2)
            } & target_trigrams

            for word in seen_words:
                key = ("word", word)
                bucket = candidates.setdefault(key, {})
                if len(bucket) >= SENTENCE_MAX_PER_KEY:
                    continue
                bucket.setdefault(title, sentence)
            for bg in seen_bigrams:
                key = ("bigram", bg)
                bucket = candidates.setdefault(key, {})
                if len(bucket) >= SENTENCE_MAX_PER_KEY:
                    continue
                bucket.setdefault(title, sentence)
            for tg in seen_trigrams:
                key = ("trigram", tg)
                bucket = candidates.setdefault(key, {})
                if len(bucket) >= SENTENCE_MAX_PER_KEY:
                    continue
                bucket.setdefault(title, sentence)

    sentences_jsonl = OUT_DIR / "sentences.jsonl"

    def key_sort(item: tuple[tuple[str, str], dict[str, str]]):
        (kind, key), _bucket = item
        kind_order = {"word": 0, "bigram": 1, "trigram": 2}
        return (kind_order[kind], key)

    with sentences_jsonl.open("w", encoding="utf-8") as f:
        for (kind, key), bucket in sorted(candidates.items(), key=key_sort):
            if not bucket:
                continue
            entries = [
                {"text": text, "book": book}
                for book, text in list(bucket.items())[:SENTENCE_MAX_PER_KEY]
            ]
            record = {"key": key, "type": kind, "sentences": entries}
            f.write(json.dumps(record, ensure_ascii=False) + "\n")

    print("[build_english_corpus] done", file=sys.stderr)
    print(f"  books.tsv: {len(book_rows_sorted)} rows", file=sys.stderr)
    print(f"  words.tsv: {len(word_rows)} rows", file=sys.stderr)
    print(f"  bigrams.tsv: {len(bigram_rows)} rows", file=sys.stderr)
    print(f"  trigrams.tsv: {len(trigram_rows)} rows", file=sys.stderr)
    print(f"  sentences.jsonl: {sum(1 for b in candidates.values() if b)} keys", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
